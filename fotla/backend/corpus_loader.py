import abc
import json

if False:
    from typing import Dict, Iterator, List, Type


from more_itertools import chunked
from pydantic import BaseModel
from tqdm import tqdm


class Doc(BaseModel):
    doc_id: str
    text: str
    title: str = ""


class CorpusLoader(abc.ABC):
    def load(self, batch_size: int = 10_000) -> Iterator[List[Doc]]:
        raise NotImplementedError


class JsonlCorpusLoader(CorpusLoader):
    def __init__(
        self, path: str, data_type: Type[Doc] = Doc, verbose: bool = True
    ) -> None:
        self.path = path
        self.data_type = data_type
        self.verbose = verbose

    def iter_lines(self, path: str) -> Iterator[Doc]:
        with open(path) as f:
            for i, line in enumerate(f):
                doc_dict = json.loads(line)
                doc = self.data_type(**doc_dict)

                yield doc

    def load(self, batch_size: int = 10_000) -> Iterator[List[Doc]]:
        iterator = chunked(self.iter_lines(self.path), batch_size)
        if self.verbose:
            iterator = tqdm(iterator, desc="Loading corpus")
        for chunk in iterator:
            yield chunk


class AdhocCorpusLoader(CorpusLoader):
    def __init__(self, docs: List[Dict]) -> None:
        self.docs = docs

    def dict_to_doc(self, dicts: List[Dict]) -> List[Doc]:
        return [Doc(**doc) for doc in dicts]

    def load(self, batch_size: int = 10_000) -> Iterator[List[Doc]]:
        for chunk in chunked(self.docs, batch_size):
            yield self.dict_to_doc(chunk)
