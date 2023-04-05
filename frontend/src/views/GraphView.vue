<script setup lang="ts">
import { markRaw } from 'vue'
import type { Component } from 'vue'

import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'

import NodeComponent from '@/components/NodeComponent.vue'

import { useGraphStore } from '@/stores/graph'

const store = useGraphStore()
</script>

<template>
  <div class="wrapper">
    <VueFlow v-model="store.elements" :node-types="{ node: markRaw(<Component>NodeComponent) }">
      <Background style="background-color: #0b0f19" pattern-color="#374151" :gap="16" />
    </VueFlow>
  </div>
</template>

<style>
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';

.vue-flow {
  height: 100vh;
}
</style>
