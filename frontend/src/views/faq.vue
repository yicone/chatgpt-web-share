<template>
    <div class="justify-center flex-1">
        <NotionRenderer :blockMap="blockMap" fullPage />
    </div>
    <div class="mt-9 mb-9" style="text-align: center;">
        <p>© 2023 ShareGPT</p>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NotionRenderer, getPageBlocks } from "vue-notion";

const blockMap = ref(null)

onMounted(async () => {
    blockMap.value = await getPageBlocks('55be2945cf3248c099ce617bec69d6be', 'https://notion-api.sharegpt.vip/v1')
})
</script>

<style>
/* optional Notion-like styles */
@import "vue-notion/src/styles.css";
</style>