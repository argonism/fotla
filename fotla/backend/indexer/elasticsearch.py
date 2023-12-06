import json
from dataclasses import dataclass
from logging import getLogger
from typing import Dict, Iterable, List, Optional, Tuple

import elasticsearch
import numpy as np
from tqdm import tqdm

from fotla.backend.corpus_loader import CorpusLoader
from fotla.backend.indexer import DenseIndexer, Record
from fotla.backend.retriever import Retriever
from fotla.backend.utils import project_dir

logger = getLogger(__name__)


@dataclass
class ElasticsearchConfig:
    host: str
    port: int
    schema: str = "http"
    index_name: str = "fotla_index"
    index_scheme_path: str = project_dir / "vector_indexer/elasticsearch/mappngs.json"


class ElasticsearchIndexer(DenseIndexer):
    def __init__(
        self,
        config: ElasticsearchConfig,
        fields: Optional[List[str]] = None,
        recreate_index: bool = False,
    ) -> None:
        self.config = config
        self.fields = fields
        self.es = elasticsearch.Elasticsearch(
            f"{self.config.schema}://{self.config.host}:{self.config.port}",
        )
        self.index_name = self.config.index_name
        logger.info(f"setting index: {self.index_name}")

        if recreate_index and self.exist_index(self.index_name):
            self.delete_index(self.index_name)

        if not self.exist_index(self.index_name):
            logger.info(f"Index {self.index_name} does not exist. creating...")
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

    def delete_index(self, index_name: str) -> None:
        """Deletes the index.

        Args:
            index_name: The name of the index.
        """
        self.es.indices.delete(index=index_name)

    def exist_index(self, index_name: str) -> bool:
        """Returns whether the index exists.

        Args:
            index_name: The name of the index.

        Returns:
            True if the index exists, False otherwise.
        """
        return self.es.indices.exists(index=index_name)

    def async_index(self, records: Iterable[Record]) -> None:
        try:
            import asyncio
        except ImportError:
            raise ImportError("asyncio is required for async_index")

        try:
            from elasticsearch.helpers import async_streaming_bulk
        except ImportError:
            raise ImportError("elasticsearch-async is required for async_index")

        from typing import AsyncIterable

        async def create_index_body(records: Iterable[Record]) -> AsyncIterable[Dict]:
            for record in records:
                body = {
                    "doc_id": record.doc_id,
                    "title": record.title,
                    "text": record.text,
                }

                if record.vec is not None:
                    unit_vec = record.vec / np.linalg.norm(record.vec)
                    body["vec"] = unit_vec

                yield {
                    "_op_type": "index",
                    "_index": self.index_name,
                    "_source": body,
                }

        async def main():
            write_count = 0
            async for ok, result in async_streaming_bulk(
                es, create_index_body(records)
            ):
                action, result = result.popitem()
                if not ok:
                    print(f"failed to {action} document {result}")
                else:
                    write_count += 1
            return write_count

        es = elasticsearch.AsyncElasticsearch(
            f"{self.config.schema}://{self.config.host}:{self.config.port}",
        )
        loop = asyncio.get_event_loop()
        write_count = loop.run_until_complete(main())
        return write_count

    def index(
        self,
        records: Iterable[Record],
        refresh: bool = True,
    ) -> int:
        """Indexes the given vectors.

        Args:
            vectors: The vectors to index.

        Returns:
            The number of vectors fitted.
        """

        def create_index_body(record: Record, fields: Optional[List[str]]) -> Dict:
            if fields is None:
                body = {
                    "doc_id": record.doc_id,
                    "title": record.title,
                    "text": record.text,
                }
            else:
                body = {}
                record_dict = record.asdict()
                for field in fields:
                    body[field] = record_dict.get(field, None)

            if record.vec is not None:
                unit_vec = record.vec / np.linalg.norm(record.vec)
                body["vec"] = unit_vec

            return body

        write_count = 0
        for record in records:
            body = create_index_body(record, self.fields)

            self.es.index(index=self.index_name, body=body, refresh=refresh)
            write_count += 1

        return write_count

    def query(
        self,
        queries: List[str],
        term_fields: List[str] = [],
        vectors: List[np.ndarray] = [],
        vec_field: str = "vec",
        top_k: int = 10,
        from_: int = 0,
        size: int = 10,
        source: Optional[List[str]] = None,
    ) -> List[Tuple[str, Dict]]:
        """Returns the top_k most similar vectors to the given vectors.

        Args:
            vectors: The vectors to query.
            top_k: The number of similar vectors to return.

        Returns:
            The indices of the top_k most similar vectors.
        """
        logger.debug(f"Querying {len(queries)} queries.")

        if len(vectors) <= 0 and len(term_fields) <= 0:
            raise ValueError("Either vectors or term_field must be given.")

        if len(vectors) > 0 and len(vectors) != len(queries):
            raise ValueError(
                "The number of vectors must be equal to the number of queries."
            )

        results: List[Tuple[str, Dict]] = []
        for i, query in enumerate(queries):
            logger.debug(f"Retrieving with query: {query}")

            vec = vectors[i] if len(vectors) > 0 else None
            knn_param = None
            if vec is not None:
                unit_vec = vec / np.linalg.norm(vec)
                knn_param = {
                    "field": "vec",
                    "query_vector": unit_vec,
                    "k": top_k,
                    "num_candidates": top_k * 2,
                }

            term_query = (
                None
                if len(term_fields) <= 0
                else {
                    "multi_match": {
                        "query": query,
                        "fields": term_fields,
                    }
                }
            )

            res = self.es.search(
                index=self.index_name,
                knn=knn_param,
                query=term_query,
                source=self.fields if source is None else source,
                from_=from_,
                size=size,
            )
            result = {
                "total": res["hits"]["total"]["value"],
                "hits": res["hits"]["hits"],
            }
            logger.debug(f"query {query} retrieved {len(result['hits'])} results.")
            results.append((query, result))

            logger.debug(f"Retrieved {len(result)} results.")
        return results


class ElasticsearchBM25(Retriever):
    def __init__(
        self,
        es_indexer: ElasticsearchIndexer,
        fields: Optional[List[str]] = ["title", "text"],
    ) -> None:
        self.es_indexer = es_indexer
        self.fields = fields

    def async_index(
        self,
        corpus_loader: CorpusLoader,
        batch_size: int = 10_000,
        total: int = 65613666,
    ) -> None:
        def load_corpus(
            corpus_loader: CorpusLoader, batch_size: int
        ) -> Iterable[Record]:
            for docs_chunk in tqdm(
                corpus_loader.load(batch_size=batch_size),
                desc="loading corpus..",
                total=(total // batch_size) + 1,
            ):
                for doc in docs_chunk:
                    yield Record(doc_id=doc.doc_id, title=doc.title, text=doc.text)

        self.es_indexer.async_index(load_corpus(corpus_loader, batch_size))

    def index(
        self,
        corpus_loader: CorpusLoader,
        batch_size: int = 10_000,
        total: int = 65613666,
    ) -> None:
        for docs_chunk in tqdm(
            corpus_loader.load(batch_size=batch_size),
            desc="indexing..",
            total=(total // batch_size) + 1,
        ):
            self.es_indexer.index(
                [
                    Record(doc_id=doc.doc_id, title=doc.title, text=doc.text)
                    for doc in docs_chunk
                ],
                refresh=False,
            )

    def retrieve(
        self,
        queries: List[str],
        top_k: int,
        from_: int = 0,
        size: int = 10,
        hybrid: bool = False,
    ) -> List[Tuple[str, Dict]]:
        result = self.es_indexer.query(
            queries, term_fields=self.fields, top_k=top_k, from_=from_, size=size
        )
        return result
