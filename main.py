import os

from fotla.backend.api import start_api
from fotla.backend.corpus_loader import AdhocCorpusLoader, Doc, JsonlCorpusLoader
from fotla.backend.encoder import HFSymetricDenseEncoder
from fotla.backend.indexer.elasticsearch import (
    ElasticsearchBM25,
    ElasticsearchConfig,
    ElasticsearchIndexer,
)
from fotla.backend.retriever import DenseRetriever
from fotla.backend.utils import project_dir


def load_indexer(recreate_index: bool = False):
    es_host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
    es_port = os.environ.get("ELASTICSEARCH_PORT", 9200)
    es_config = ElasticsearchConfig(
        es_host,
        es_port,
        index_name="fotla",
        index_scheme_path=project_dir / "vector_indexer/elasticsearch/mappngs.json",
    )
    indexer = ElasticsearchIndexer(es_config, recreate_index=recreate_index)
    return indexer


def load_retirever(indexer):
    # encoder = HFSymetricDenseEncoder("facebook/mcontriever-msmarco")
    # retriever = DenseRetriever(encoder, indexer)
    retriever = ElasticsearchBM25(indexer)

    return retriever


def index(retriever):
    corpus_loader = AdhocCorpusLoader(
        [
            {
                "doc_id": "1",
                "text": "hello! This is the first doc.",
                "title": "first doc",
            },
            {
                "doc_id": "2",
                "text": "world! This is the second doc.",
                "title": "second doc",
            },
            {
                "doc_id": "3",
                "text": "hello world! This is the third doc.",
                "title": "third doc",
            },
            {"doc_id": "3", "text": "This is the forth doc.", "title": "forth doc"},
        ]
    )
    retriever.index(corpus_loader)
    # retriever.async_index(corpus_loader)


def main(args):
    indexer = load_indexer(args.recreate_index)
    retriever = load_retirever(indexer)

    if args.index:
        index(retriever)

    if not args.retrieve == "":
        results = retriever.retrieve([args.retrieve], 100)
        print(results)
    else:
        start_api(retriever, port=9999)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--index", action="store_true")
    parser.add_argument("--retrieve", default="")
    parser.add_argument("--recreate_index", action="store_true")
    return parser.parse_args()


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    main(args)
