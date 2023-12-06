<script lang="ts">
    import { SlideToggle } from "@skeletonlabs/skeleton";
    import { Accordion, AccordionItem } from "@skeletonlabs/skeleton";
    import { goto } from "$app/navigation";

    export let topk: number;
    export let term_filter: boolean;
    export let query = "";
    let compositioning = false;

    const onSearchKeyDown = function (event: KeyboardEvent) {
        if (event.key === "Enter" && !compositioning) {
            const search_params = {
                query: query,
                topk: `${topk}`,
                hybrid: `${Number(term_filter)}`,
                from: "0",
                size: "10",
            };
            const searchParams = new URLSearchParams(search_params);
            goto("/search?" + searchParams.toString());
        }
    };
</script>

<div class="space-y-10 my-10">
    <label class="label">
        <span>Search</span>
        <input
            class="input"
            type="text"
            placeholder="search ..."
            bind:value={query}
            on:keydown={onSearchKeyDown}
            on:compositionstart={() => (compositioning = true)}
            on:compositionend={() => (compositioning = false)}
        />
    </label>
    <Accordion>
        <AccordionItem open>
            <svelte:fragment slot="summary">advance settings</svelte:fragment>
            <svelte:fragment slot="content">
                <SlideToggle
                    name="term filtering"
                    bind:checked={term_filter}
                    size="sm"
                >
                    <span
                        class={term_filter ? "text-gray-600" : "text-gray-400"}
                        >term filtering</span
                    >
                </SlideToggle>
            </svelte:fragment>
        </AccordionItem>
    </Accordion>
</div>
