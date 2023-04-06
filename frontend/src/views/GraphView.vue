<script setup lang="ts">
import Graph from '@/components/Graph.vue'

import { useGraphStore } from '@/stores/graph'

const store = useGraphStore()
</script>

<template>
  <div class="wrapper">
    <div class="flex items-stretch">
      <ul class="left-0 flex h-full flex-col">
        <li v-for="[k, _] in Object.entries(store.templates)">
          <button @click="(type) => store.addNode(type)">{{ k }}</button>
        </li>
      </ul>
      <Graph class="grow" />
    </div>
  </div>
</template>
