<template>
    <NotionRenderer :blockMap="blockMap" fullPage />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NotionRenderer, getPageBlocks } from "vue-notion";

const blockMap = ref(null)

onMounted(async () => {
    blockMap.value = await getPageBlocks('55be2945cf3248c099ce617bec69d6be')
})
</script>

<style>
/* optional Notion-like styles */
@import "vue-notion/src/styles.css";
</style>