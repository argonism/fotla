import os

from fotla.backend.corpus_loader import AdhocCorpusLoader
from fotla.backend.encoder import HFSymetricDenseEncoder
from fotla.backend.indexer.elasticsearch import (
    ElasticsearchConfig,
    ElasticsearchIndexer,
)
from fotla.backend.retriever import DenseRetriever


def main():
    es_host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
    es_port = os.environ.get("ELASTICSEARCH_PORT", 9200)
    es_config = ElasticsearchConfig(es_host, es_port)
    indexer = ElasticsearchIndexer(es_config, recreate_index=True)

    encoder = HFSymetricDenseEncoder("facebook/mcontriever-msmarco")
    retriever = DenseRetriever(encoder, indexer)
    # retriever = ElasticsearchBM25(indexer)

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
    # start_api(retriever, port=9999)

    results = retriever.retrieve(["hello world"], 10)
    print(results)


if __name__ == '__main__':
    main()
