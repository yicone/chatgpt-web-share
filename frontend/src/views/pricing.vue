<template>
    <NotionRenderer :blockMap="blockMap" fullPage />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NotionRenderer, getPageBlocks } from "vue-notion";

const blockMap = ref(null)

onMounted(async () => {
    blockMap.value = await getPageBlocks('cf09e1517f3347d4a2e2b2d64f24e34a', 'https://notion-api.sharegpt.vip/v1')
})
</script>

<style>
/* optional Notion-like styles */
@import "vue-notion/src/styles.css";
</style>