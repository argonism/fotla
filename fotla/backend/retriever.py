import abc
from logging import getLogger
from typing import Iterable, List, Tuple

import numpy as np

from fotla.backend.corpus_loader import CorpusLoader, Doc
from fotla.backend.encoder import DenseEncoder
from fotla.backend.indexer import DenseIndexer, Record

logger = getLogger(__name__)


class Retriever(abc.ABC):
    @abc.abstractmethod
    def index(self, corpus: CorpusLoader):
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve(self, queries: List[str], top_k: int) -> List[Tuple]:
        raise NotImplementedError


class DenseRetriever(Retriever):
    def __init__(self, encoder: DenseEncoder, vector_indexer: DenseIndexer) -> None:
        self.encoder = encoder
        self.vector_indexer = vector_indexer

    def docs_to_texts(self, docs: Iterable[Doc]) -> Tuple[List[str], List[str]]:
        docids = []
        texts = []
        for doc in docs:
            docids.append(doc.doc_id)
            texts.append(doc.text + " " + doc.title)
        return texts, docids

    def encode_docs(self, docs: Iterable[Doc]) -> Tuple[np.ndarray, List[str]]:
        texts, docids = self.docs_to_texts(docs)
        return self.encoder.encode_corpus(texts), docids

    def encode_queries(self, queries: Iterable[str]) -> np.ndarray:
        return self.encoder.encode_queries(queries)

    def index(
        self,
        corpus_loader: CorpusLoader,
        batch_size: int = 10_000,
    ) -> None:
        def yield_doc_vector(
            embs: np.ndarray, docids: List[str], docs_chunk: List[Doc]
        ):
            for emb, docid, doc in zip(embs, docids, docs_chunk):
                yield Record(emb, docid, doc.title, doc.text)

        for docs_chunk in corpus_loader.load(batch_size=batch_size):
            embeddings, docids = self.encode_docs(docs_chunk)
            self.vector_indexer.index(
                yield_doc_vector(embeddings, docids, docs_chunk)
            )

    def retrieve(self, queries: List[str], top_k: int) -> List[Tuple]:
        embeddings = self.encode_queries(queries)
        return self.vector_indexer.query(queries, embeddings, top_k)
