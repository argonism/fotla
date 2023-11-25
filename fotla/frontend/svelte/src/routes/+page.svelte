<script lang="ts">
    type SearchItem = {
        _index: string;
        _score: number;
        _source: {
            doc_id: string;
            title: string;
            text: string;
        };
    };

    let search_box = "aaa";
    let search_result: Array<SearchItem> = [];

    const search = async function (query: string) {
        const response = await fetch("http://localhost:9999/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query: query, topk: 10 }),
        });
        const response_json = await response.json();
        search_result = response_json.result[0][1];
    };

    const onSearchKeyDown = function (event: KeyboardEvent) {
        if (event.key === "Enter") {
            search(search_box);
        }
    };
</script>

<div class="container h-full mx-auto flex justify-center items-center">
    <div class="space-y-4 text-center flex flex-col items-center w-10/12">
        <div class="space-y-10 my-10">
            <h2 class="h2">FRESH OFF THE LAB</h2>
            <label class="label">
                <span>Search</span>
                <input
                    class="input"
                    type="text"
                    placeholder="search ..."
                    bind:value={search_box}
                    on:keydown={onSearchKeyDown}
                />
            </label>
        </div>
        {#if search_result.length > 0}
            {#each search_result as item}
                <div class="card variant-ringed-surface w-full card-hover">
                    <header class="card-header">
                        title: {item._source.title}
                    </header>
                    <section class="p-4">{item._source.text}</section>
                    <footer class="card-footer">(footer)</footer>
                </div>
            {/each}
        {/if}
    </div>
</div>

<style lang="postcss">
</style>
