import { env } from '$env/dynamic/private';
import type { ServerLoadEvent } from '@sveltejs/kit';
import { parseSearchParams } from '../../lib/utils/util';

/** @type {import('./$types').PageServerLoad} */
export async function load({ url, fetch }: ServerLoadEvent) {
    // const { query, topk } = await request.json();
    const { query, topk, hybrid, from, size } = parseSearchParams(url.searchParams);

    if (env.FOTLA_SEARCH_URL == null) {
        throw new Error("FOTLA_SEARCH_URL is not set");
    }
    const response = await fetch(env.FOTLA_SEARCH_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ query, topk, hybrid, size, from_: from, }),
    });
    const response_json = await response.json();

    return {
        query: response_json.result[0][0],
        total: response_json.result[0][1].total,
        posts: response_json.result[0][1].hits
    };
}