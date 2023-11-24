import os

from fotla.backend.api import start_api
from fotla.backend.corpus_loader import AdhocCorpusLoader
from fotla.backend.indexer.elasticsearch import (
    ElasticsearchBM25,
    ElasticsearchConfig,
    ElasticsearchIndexer,
)


def main():
    # HFSymetricDenseEncoder("facebook/mcontriever-msmarco")
    es_host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
    es_port = os.environ.get("ELASTICSEARCH_PORT", 9200)
    indexer = ElasticsearchIndexer(ElasticsearchConfig(es_host, es_port))

    # retriever = DenseRetriever(encoder, indexer)
    retriever = ElasticsearchBM25(indexer)

    corpus_loader = AdhocCorpusLoader(
        [
            {"doc_id": "1", "text": "hello! This is the first doc."},
            {"doc_id": "2", "text": "world! This is the second doc."},
            {"doc_id": "3", "text": "This is the third doc."},
        ]
    )
    retriever.index(corpus_loader)
    start_api(retriever, port=9999)

    # results = retriever.retrieve(["hello world"], 10)
    # print(results)


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)
    main()
