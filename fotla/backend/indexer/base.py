import abc
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import numpy as np


@dataclass
class Record:
    doc_id: str
    vec: Optional[np.ndarray] = None
    title: Optional[str] = None
    text: Optional[str] = None


class DenseIndexer(abc.ABC):
    @abc.abstractmethod
    def index(self, records: Iterable[Record]) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def query_vectors(
        self, queries: List[str], vectors: List[np.ndarray], top_k: int
    ) -> List[Tuple]:
        raise NotImplementedError


class SparseIndexer(abc.ABC):
    @abc.abstractmethod
    def index(self, records: Iterable[Record]) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def query(
        self,
        queries: List[str],
        top_k: int,
        vectors: Optional[List[np.ndarray]] = None,
    ) -> List[Tuple]:
        raise NotImplementedError
