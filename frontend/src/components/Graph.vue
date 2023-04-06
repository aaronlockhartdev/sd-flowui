<script setup lang="ts">
import { markRaw, watch } from 'vue'
import type { Component } from 'vue'
import { storeToRefs } from 'pinia'

import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'

import Node from '@/components/Node.vue'

import { useGraphStore } from '@/stores/graph'

const store = useGraphStore()

const { nodes } = storeToRefs(store)

watch(nodes, (val) => console.log(val))
</script>

<template>
  <div class="wrapper">
    <VueFlow
      v-model:nodes="store.nodes"
      v-model:edges="store.edges"
      :node-types="{ node: markRaw(<Component>Node) }"
      class=""
    >
      <Background style="background-color: #101523" pattern-color="#374151" :gap="16" />
    </VueFlow>
  </div>
</template>

<style>
@import '@vue-flow/core/dist/style.css';
</style>
