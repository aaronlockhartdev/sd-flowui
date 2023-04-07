<script setup lang="ts">
import { markRaw, watch } from 'vue'
import type { Component } from 'vue'
import { storeToRefs } from 'pinia'

import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'

import Node from '@/components/Node.vue'

import { useGraphStore } from '@/stores/graph'

const store = useGraphStore()

const { vueFlowRef, project } = useVueFlow()

function onDrop(evt: DragEvent) {
  const type = evt.dataTransfer?.getData('application/vueflow')

  if (!type) return

  const { left, top } = vueFlowRef.value!.getBoundingClientRect()

  store.addNode(type, project({ x: evt.clientX - left - 100, y: evt.clientY - top }))
}

function onClick(evt: MouseEvent) {}
</script>

<template>
  <div class="wrapper">
    <div class="flex h-[calc(100vh-3rem)] items-stretch">
      <ul class="left-0 flex h-full flex-col border-r border-gray-700 bg-gray-900">
        <li v-for="k in Object.keys(store.templates)" class="m-2">
          <button
            @click="onClick"
            :draggable="true"
            @dragstart="(evt: DragEvent) => {
              if (!evt.dataTransfer) return 

              evt.dataTransfer.dropEffect = 'move'
              evt.dataTransfer.effectAllowed = 'move'

              evt.dataTransfer.setData('application/vueflow', k)}"
            class="rounded-lg bg-gray-800 px-2 py-1"
          >
            <h5 class="px-2 text-sm font-medium text-white">
              {{ k }}
            </h5>
          </button>
        </li>
      </ul>
      <VueFlow
        v-model:nodes="store.nodes"
        v-model:edges="store.edges"
        :node-types="{ node: markRaw(<Component>Node) }"
        @drop="onDrop"
        @dragover.prevent
        @dragenter.prevent
        class="h-100"
      >
        <Background style="background-color: #101523" pattern-color="#374151" :gap="16" />
      </VueFlow>
    </div>
  </div>
</template>

<style>
@import '@vue-flow/core/dist/style.css';
</style>
