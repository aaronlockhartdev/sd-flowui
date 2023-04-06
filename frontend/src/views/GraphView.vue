<script setup lang="ts">
import { markRaw } from 'vue'
import type { Component } from 'vue'

import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'

import Node from '@/components/Node.vue'

import { useGraphStore } from '@/stores/graph'

const store = useGraphStore()
</script>

<template>
  <div class="wrapper">
    <VueFlow
      v-model:nodes="store.nodes"
      v-model:edges="store.edges"
      :node-types="{ node: markRaw(<Component>Node) }"
    >
      <Background style="background-color: #0b0f19" pattern-color="#374151" :gap="16" />
    </VueFlow>
  </div>
</template>

<style>
@import '@vue-flow/core/dist/style.css';

.vue-flow {
  height: 100vh;
}
</style>
