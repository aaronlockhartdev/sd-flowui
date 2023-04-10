<script setup lang="ts">
import { markRaw } from 'vue'
import type { Component } from 'vue'

import { VueFlow, useVueFlow, ConnectionMode, type EdgeUpdateEvent } from '@vue-flow/core'
import type { NodeChange, Connection, Edge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'

import Node from '@/components/Node.vue'
import Edge_ from '@/components/Edge.vue'

import { useGraphStore } from '@/stores/graph'

const store = useGraphStore()

const { vueFlowRef, project } = useVueFlow()

function onDrop(evt: DragEvent) {
  const type = evt.dataTransfer?.getData('application/vueflow')

  if (!type) return

  const { left, top } = vueFlowRef.value!.getBoundingClientRect()

  store.addNode(type, project({ x: evt.clientX - left - 100, y: evt.clientY - top }))
}

function onClick(type: string) {
  const { x, y, width, height } = vueFlowRef.value!.getBoundingClientRect()

  console.log(vueFlowRef.value?.getBoundingClientRect())

  const center = project({ x: x + 0.5 * width - 100, y: y + 0.5 * height - 200 })

  console.log(center)

  store.addNode(type, center)
}

function onNodesChange(changes: NodeChange[]) {
  for (const change of changes) {
    switch (change.type) {
      case 'remove':
        store.removeNode(parseInt(change.id))
        break
      case 'position':
        if (change.position) store.updatePositionNode(parseInt(change.id), change.position)
    }
  }
}

function onConnect(connection: Connection) {
  if (store.connectionValid(connection))
    store.addEdge(
      parseInt(connection.source),
      parseInt(connection.target),
      connection.sourceHandle!,
      connection.targetHandle!
    )
}

function onEdgeUpdate({ edge, connection }: EdgeUpdateEvent) {
  store.removeEdge(edge.id)
  if (store.connectionValid(connection))
    store.addEdge(
      parseInt(connection.source),
      parseInt(connection.target),
      connection.sourceHandle!,
      connection.targetHandle!
    )
}
</script>

<template>
  <div class="wrapper">
    <div class="flex h-[calc(100vh-3rem)] flex-col items-stretch bg-gray-800">
      <ul class="left-0 flex w-full border-b border-gray-700 bg-gray-800 py-1">
        <li v-for="k in Object.keys(store.templates)" class="m-2">
          <button
            @click="(_) => onClick(k)"
            :draggable="true"
            @dragstart="(evt: DragEvent) => {
              if (!evt.dataTransfer) return 

              evt.dataTransfer.dropEffect = 'move'
              evt.dataTransfer.effectAllowed = 'move'

              evt.dataTransfer.setData('application/vueflow', k)}"
            class="rounded-lg border border-gray-700 bg-gray-800 px-2 py-1"
          >
            <h5 class="px-2 text-sm font-medium text-gray-300">
              {{ k }}
            </h5>
          </button>
        </li>
      </ul>
      <VueFlow
        v-model:nodes="store.nodes"
        v-model:edges="store.edges"
        :node-types="{ node: markRaw(<Component>Node) }"
        :edge-types="{ edge: markRaw(<Component>Edge_)}"
        @nodes-change="onNodesChange"
        @edge-update="onEdgeUpdate"
        @connect="onConnect"
        @drop="onDrop"
        @dragover.prevent
        @dragenter.prevent
        :connection-mode="ConnectionMode.Strict"
        class="h-100"
      >
        <Background pattern-color="#4B5563" :gap="24" :size="1.6" class="bg-gray-900" />
        <MiniMap
          pannable
          zoomable
          node-color="#1C64F2"
          node-stroke-color="#fff"
          :node-stroke-width="20"
          :node-border-radius="30"
          mask-color="rgb(31, 41, 55, 0.6)"
          class="left-0 rounded"
        />
      </VueFlow>
    </div>
  </div>
</template>

<style>
@import '@vue-flow/core/dist/style.css';
</style>
