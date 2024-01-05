export type SearchItem = {
    _index: string;
    _score: number;
    _source: {
        subject_number: string,
        subject_name: string,
        class_method: string,
        credit: string,
        grade: string,
        semester: string,
        schedule: string,
        classroom: string,
        instructor: string,
        overview: string,
        note: string,
        application_condition: string,
        subject_name_en: string,
        subject_code: string,
        required_subject_name: string,
        updated_at: string,
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
    search_fields: string[];
}

export type SearchAPIParams = SearchOptParams & PagenateParams;

export type SearchData = {
    query: string;
    posts: Array<SearchItem>;
    total: number;
};