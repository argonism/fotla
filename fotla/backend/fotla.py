from fotla.corpus_loader import AdhocCorpusLoader
from fotla.encoder import DenseRetriever, HFSymetricDenseEncoder
from fotla.vector_indexer import ElasticsearchConfig, ElasticsearchIndexer


def main():
    encoder = HFSymetricDenseEncoder("facebook/mcontriever-msmarco")
    vector_indexer = ElasticsearchIndexer(
        ElasticsearchConfig("localhost", 9200, "https")
    )
    retriever = DenseRetriever(encoder, vector_indexer)

    corpus_loader = AdhocCorpusLoader(
        [
            {"doc_id": "1", "text": "hello! This is the first doc."},
            {"doc_id": "2", "text": "world! This is the second doc."},
            {"doc_id": "3", "text": "This is the third doc."},
        ]
    )
    retriever.index(corpus_loader)
    results = retriever.retrieve(["hello world"], 10)
    print(results)


if __name__ == '__main__':
    main()
