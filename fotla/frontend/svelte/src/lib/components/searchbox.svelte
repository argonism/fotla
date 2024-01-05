<script lang="ts">
    import { SlideToggle } from "@skeletonlabs/skeleton";
    import { ListBox, ListBoxItem } from "@skeletonlabs/skeleton";
    import { Accordion, AccordionItem } from "@skeletonlabs/skeleton";
    import { goto } from "$app/navigation";

    export let topk: number;
    export let term_filter: boolean;
    export let query = "";
    export let search_fields: string[] = ["subject_number", "subject_name"];

    let compositioning = false;

    let available_fields: { [key: string]: string } = {
        subject_number: "科目番号",
        subject_name: "科目名",
        class_method: "授業方法",
        semester: "学期",
        schedule: "曜時限",
        instructor: "担当教員",
        note: "備考",
    };

    const onSearchKeyDown = function (event: KeyboardEvent) {
        if (event.key === "Enter" && !compositioning) {
            const search_params = {
                query: query,
                topk: `${topk}`,
                hybrid: `${Number(term_filter)}`,
                from: "0",
                size: "10",
                search_fields: search_fields.join(","),
            };
            const searchParams = new URLSearchParams(search_params);
            goto("/search?" + searchParams.toString());
        }
    };
</script>

<div class="space-y-10 my-10 w-full">
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
    <Accordion class="w-full">
        <AccordionItem open class="w-full">
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
                <div class="w-full overflow-auto">
                    <ListBox multiple>
                        <div class="w-full whitespace-nowrap flex gap-4">
                            {#each Object.entries(available_fields) as [field_id, name]}
                                <ListBoxItem
                                    class="border-2 border-gray-700 dark:border-gray-200"
                                    bind:group={search_fields}
                                    rounded="md"
                                    name="small"
                                    value={field_id}>{name}</ListBoxItem
                                >
                            {/each}
                        </div>
                    </ListBox>
                </div>
            </svelte:fragment>
        </AccordionItem>
    </Accordion>
</div>
