<template>
    <NotionRenderer :blockMap="blockMap" fullPage />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NotionRenderer, getPageBlocks } from "vue-notion";

const blockMap = ref(null)

onMounted(async () => {
    blockMap.value = await getPageBlocks('6258c5e84cbd412dbd69b73c8d656fe4')
})
</script>

<style>
/* optional Notion-like styles */
@import "vue-notion/src/styles.css";
</style>
