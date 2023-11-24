import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import elasticsearch
import numpy as np

from fotla.backend.corpus_loader import CorpusLoader
from fotla.backend.indexer import DenseIndexer, Record, SparseIndexer
from fotla.backend.retriever import Retriever
from fotla.backend.utils import project_dir


@dataclass
class ElasticsearchConfig:
    host: str
    port: int
    schema: str = "http"
    index_name: str = "fotla_index"
    index_scheme_path: str = project_dir / "vector_indexer/elasticsearch/mappngs.json"


class ElasticsearchIndexer(DenseIndexer, SparseIndexer):
    def __init__(self, config: ElasticsearchConfig) -> None:
        self.config = config
        self.es = elasticsearch.Elasticsearch(
            f"{self.config.schema}://{self.config.host}:{self.config.port}",
        )
        print(self.es.info())
        self.index_name = self.config.index_name
        if not self.exist_index(self.index_name):
            self.create_index(self.index_name)

    def read_index_scheme(self) -> dict:
        """Reads the index scheme from the index scheme path.

        Returns:
            The index scheme.
        """
        with open(self.config.index_scheme_path) as f:
            return json.load(f)

    def create_index(self, index_name: str) -> None:
        """Creates an index in Elasticsearch for the given vector dimension.

        Args:
            index_name: The name of the index.
        """
        self.es.indices.create(
            index=index_name,
            body=self.read_index_scheme(),
        )

    def exist_index(self, index_name: str) -> bool:
        """Returns whether the index exists.

        Args:
            index_name: The name of the index.

        Returns:
            True if the index exists, False otherwise.
        """
        return self.es.indices.exists(index=index_name)

    def index(self, records: Iterable[Record]) -> int:
        """Indexes the given vectors.

        Args:
            vectors: The vectors to index.

        Returns:
            The number of vectors fitted.
        """
        write_count = 0
        for record in records:
            body = {
                "doc_id": record.doc_id,
                "title": record.title,
                "text": record.text,
            }
            if record.vec is not None:
                unit_vec = record.vec / np.linalg.norm(record.vec)
                body["vec"] = unit_vec

            self.es.index(index=self.index_name, body=body)
            write_count += 1

        return write_count

    def query_vectors(
        self, queries: List[str], vectors: List[np.ndarray], top_k: int
    ) -> List[Tuple[str, Dict]]:
        """Returns the top_k most similar vectors to the given vectors.

        Args:
            vectors: The vectors to query.
            top_k: The number of similar vectors to return.

        Returns:
            The indices of the top_k most similar vectors.
        """
        results: List[Tuple[str, Dict]] = []
        for query, vec in zip(queries, vectors):
            unit_vec = vec / np.linalg.norm(vec)
            request_body = {
                "knn": {
                    "field": "vec",
                    "query_vector": unit_vec,
                    "k": 10,
                    "num_candidates": 100,
                },
                "_source": ["doc_id", "title", "text"],
            }
            res = self.es.knn_search(index=self.index_name, body=request_body)
            results.append((query, res["hits"]["hits"]))
        return results

    def query(
        self,
        queries: List[str],
        top_k: int,
        fields: Optional[List[str]] = ["title", "text"],
    ) -> List[Tuple[str, Dict]]:
        """Returns the top_k most similar documents to the given queries.

        Args:
            queries: The queries to query.
            top_k: The number of similar documents to return.
            fields: The fields to search in.

        Returns:
            The indices of the top_k most similar documents.
        """

        results: List[Tuple[str, Dict]] = []
        for query in queries:
            request_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": fields,
                    }
                },
                "_source": ["doc_id", "title", "text"],
            }
            res = self.es.search(index=self.index_name, body=request_body)
            results.append((query, res["hits"]["hits"]))
        return results


class ElasticsearchBM25(Retriever):
    def __init__(
        self,
        es_indexer: ElasticsearchIndexer,
        fields: Optional[List[str]] = ["title", "text"],
    ) -> None:
        self.es_indexer = es_indexer
        self.fields = fields

    def index(
        self,
        corpus_loader: CorpusLoader,
        batch_size: int = 10_000,
    ) -> None:
        for docs_chunk in corpus_loader.load(batch_size=batch_size):
            self.es_indexer.index(
                [
                    Record(doc_id=doc.doc_id, title=doc.title, text=doc.text)
                    for doc in docs_chunk
                ]
            )

    def retrieve(self, queries: List[str], top_k: int) -> List[Tuple[str, Dict]]:
        return self.es_indexer.query(queries, top_k, self.fields)
