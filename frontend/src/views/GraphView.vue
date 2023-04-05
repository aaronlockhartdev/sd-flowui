<script setup lang="ts">
import NodeComponent from '@/components/NodeComponent.vue'

import { onMounted, onUnmounted, markRaw, type Component } from 'vue'

import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import type { Node, Edge } from '@vue-flow/core'

import { webSocketHandler } from '@/services/websocket'

const apiUrl = import.meta.env.PROD
  ? `${location.protocol}//${location.hostname}:${location.port}/api/v1/`
  : 'http://localhost:8000/'

const {
  addNodes,
  addEdges,
  removeNodes,
  removeEdges,
  findNode,
  findEdge,
  setElements,
  nodes,
  edges
} = useVueFlow()

let version: number
let templates: object

webSocketHandler.addEventListener('message', (event) => {
  const msg = (<CustomEvent>event).detail

  if (msg.stream != 'graph') return

  const data = msg.data as {
    version: number
    action: string
    id?: string
    node?: Node
    edge?: Edge
  }

  if (data.version <= version) return
  else if (data.version > version + 1) {
    syncGraph()
    return
  }

  version++

  switch (data.action) {
    case undefined:
      throw new Error(`Required value 'action' not received`)
    case 'create_node':
      if (!data.node) throw new Error(`Required value 'node' not received`)

      addNodes([data.node])
      break
    case 'delete_node':
      if (!data.id) throw new Error(`Required value 'id' not received`)

      removeNodes([data.id])
      break
    case 'update_node':
      if (!data.node) throw new Error(`Required value 'node' not received`)

      const node = findNode(data.node.id)

      if (!node) {
        syncGraph()
        throw new Error(`Node '${data.node.id}' does not exist, resyncing graph...`)
      }

      if (data.node.data) node.data = { ...node.data, ...data.node.data }
      if (data.node.position) node.position = data.node.position

      break
    case 'create_edge':
      if (!data.edge) throw new Error(`Required value 'edges' not received`)

      addEdges([data.edge])
      break
    case 'delete_edge':
      if (!data.id) throw new Error(`Required value 'ids' not received`)

      removeEdges([data.id])
      break
    default:
      throw new Error(`Unrecognized action '${data.action}''`)
  }
})

async function syncGraph() {
  const { version_, elements, templates_ } = await fetch(new URL('graph/', apiUrl), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json;charset=UTF-8'
    }
  }).then((res) => {
    return res.json()
  })

  version = version_
  templates = templates_

  setElements(elements)
}

function init() {
  webSocketHandler.send('subscribe', { action: 'subscribe', streams: ['graph'] })
  syncGraph()
}

onMounted(async () => {
  if (webSocketHandler.active) init()

  webSocketHandler.addEventListener('open', init)
})

onUnmounted(() => {
  if (webSocketHandler.active) {
    webSocketHandler.send('subscribe', { action: 'unsubscribe', streams: ['graph'] })
  }

  webSocketHandler.removeEventListener('open', init)
})
</script>

<template>
  <div class="wrapper">
    <VueFlow :node-types="{ node: markRaw(<Component>NodeComponent) }">
      <Background style="background-color: #111827" pattern-color="#374151" :gap="16" />
    </VueFlow>
  </div>
</template>

<style>
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';
</style>

<style scoped lang="sass">
.vue-flow
  height: 100vh
</style>
