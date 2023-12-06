<script lang="ts">
    import type { PagenateParams } from "$lib/type/types";
    export let params: PagenateParams;
    export let rest_param: string;
    export let total: number;
    export let page_margin: number = 1;
    export let search_path: string = "/search";

    function buildPagenateURL(page_num: number) {
        const pagenate_info = {
            from: `${page_num * params.size}`,
            size: `${params.size}`,
        };

        const pagenate_params = new URLSearchParams(pagenate_info);
        return (
            search_path + "?" + rest_param + "&" + pagenate_params.toString()
        );
    }

    function* range(start: number, end: number) {
        for (let i = start; i < end; i++) {
            yield i;
        }
    }

    $: page_end =
        total % params.size !== 0
            ? Math.floor(total / params.size)
            : Math.floor(total / params.size) - 1;
    $: current_page = Math.floor(params.from / params.size);

    $: nav_range_start = Math.max(0, current_page - page_margin);
    $: nav_range_end = Math.min(page_end, current_page + page_margin);
    $: page_range = [...range(nav_range_start, nav_range_end + 1)];
</script>

<nav aria-label="Page navigation">
    <ul class="inline-flex space-x-5 text-sm my-5 mb-10">
        {#if current_page !== 0}
            <li>
                <a
                    href={buildPagenateURL(Math.max(0, current_page - 1))}
                    class="flex items-center justify-center px-3 h-8 ms-0 leading-tight text-gray-500 border-e-0 border-gray-300 rounded-s-lg hover:bg-surface-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-surface-700 dark:hover:text-white"
                    >Previous</a
                >
            </li>
        {/if}
        {#if nav_range_start !== 0}
            <li>
                <a
                    href={buildPagenateURL(0)}
                    class="flex items-center justify-center px-3 h-8 leading-tight text-gray-500 border-gray-300 hover:bg-surface-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-surface-700 dark:hover:text-white"
                    >0</a
                >
            </li>
            {#if nav_range_start - 1 !== 0}<div>...</div>{/if}
        {/if}

        {#each page_range as page_num}
            <li>
                <a
                    href={buildPagenateURL(page_num)}
                    class="flex items-center justify-center px-3 h-8 leading-tight {page_num ===
                    current_page
                        ? ''
                        : 'text-gray-500 dark:text-gray-400'} border-gray-300 hover:bg-surface-100 hover:text-gray-700 dark:hover:bg-surface-700 dark:hover:text-white"
                    >{page_num}</a
                >
            </li>
        {/each}

        {#if nav_range_end !== page_end}
            {#if nav_range_end !== page_end - 1}<div>...</div>{/if}
            <li>
                <a
                    href={buildPagenateURL(page_end)}
                    class="flex items-center justify-center px-3 h-8 leading-tight text-gray-500 border-gray-300 hover:bg-surface-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-surface-700 dark:hover:text-white"
                    >{page_end}</a
                >
            </li>
        {/if}
        {#if current_page !== page_end}
            <li>
                <a
                    href={buildPagenateURL(
                        Math.min(page_end, current_page + 1),
                    )}
                    class="flex items-center justify-center px-3 h-8 leading-tight text-gray-500 rounded-e-lg hover:bg-surface-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-surface-700 dark:hover:text-white"
                    >Next</a
                >
            </li>
        {/if}
    </ul>
</nav>
