import type {
    SearchAPIParams,
    PagenateParams,
    SearchOptParams
} from "$lib/type/types";


export function getPagenationParams(
    searchParams: URLSearchParams,
): PagenateParams {
    const from = searchParams.get("from") || "0";
    const size = searchParams.get("size") || "10";
    return { from: Number(from), size: Number(size) };
}

export function getSearchOptParams(
    searchParams: URLSearchParams,
): SearchOptParams {
    const query = searchParams.get("query");
    if (query == null) {
        throw new Error("query is null");
    }
    const topk = parseInt(searchParams.get("topk") ?? "10");
    const hybrid = Boolean(parseInt(searchParams.get("hybrid") ?? "0"));
    const search_fields = searchParams.get("search_fields")?.split(",") ?? [""];

    return { query, topk, hybrid, search_fields };
}

export function parseSearchParams(searchParams: URLSearchParams): SearchAPIParams {
    const pagenate_params = getPagenationParams(searchParams);
    const search_opt_params = getSearchOptParams(searchParams);
    return { ...pagenate_params, ...search_opt_params };
};