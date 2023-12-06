export type SearchItem = {
    _index: string;
    _score: number;
    _source: {
        doc_id: string;
        title: string;
        text: string;
        url: string;
    };
}


export type PagenateParams = {
    from: number;
    size: number;
}

export type SearchOptParams = {
    query: string;
    topk: number;
    hybrid: boolean;
}

export type SearchAPIParams = SearchOptParams & PagenateParams;

export type SearchData = {
    query: string;
    posts: Array<SearchItem>;
    total: number;
};