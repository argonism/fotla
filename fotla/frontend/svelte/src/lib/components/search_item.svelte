<script lang="ts">
    import type { SearchItem } from "$lib/type/types";
    export let item: SearchItem;
</script>

<div class="w-full card-hover">
    <header class="card-header text-xl text-left pl-5">
        {item._source.title}
    </header>
    <hr
        class="h-px my-2 w-99% bg-surface-100 border-0 dark:bg-gray-700 mx-auto"
    />
    <section class="p-5 text-ellipsis overflow-hidden max-w-full max-h-20">
        {item._source.text}...
    </section>
</div>
