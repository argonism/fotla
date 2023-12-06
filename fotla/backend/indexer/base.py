import abc
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

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
        raise NotImplementedError
