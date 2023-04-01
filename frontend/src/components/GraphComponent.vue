<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

import { VueFlow, useVueFlow } from '@vue-flow/core'
import type { GraphNode, GraphEdge, EdgeChange } from '@vue-flow/core'

import { webSocketHandler } from '@/services/websocket'

const apiUrl =
  process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000/'
    : `${location.protocol}//${location.hostname}:${location.port}/api/v1/`

let { applyNodeChanges, applyEdgeChanges, findNode, nodes, edges } = useVueFlow()

async function receiveUpdates() {
  while (true) {
    const data = (await webSocketHandler.message('graph')) as {
      action: string
      node?: GraphNode
      nodeData?: {}
      nodePos?: { x: number; y: number }
      nodeId?: string
      edges?: GraphEdge[]
      edgeIds?: string[]
    }

    switch (data.action) {
      case 'addNode':
        applyNodeChanges([{ type: 'add', item: data.node! }])
        break
      case 'updateNode':
        const node = findNode(data.nodeId!)
        if (data.nodePos) {
          applyNodeChanges([
            { type: 'position', id: data.nodeId!, position: data.nodePos!, from: node?.position! }
          ])
        } else {
          node!.data = data.nodeData!
        }
        break
      case 'removeNode':
        applyNodeChanges([{ type: 'remove', id: data.nodeId! }])
        break

      case 'addEdges':
        const addChanges: EdgeChange[] = []
        for (const e of data.edges!) applyEdgeChanges([{ type: 'add', item: e }])
        applyEdgeChanges(addChanges)
        break

      case 'removeEdges':
        const removeChanges: EdgeChange[] = []
        for (const id of data.edgeIds!) applyEdgeChanges([{ type: 'remove', id: id }])
        applyEdgeChanges(removeChanges)
        break
    }
  }
}

async function syncGraph() {
  const components = await fetch(new URL('graph/components', apiUrl), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json;charset=UTF-8'
    }
  }).then((res) => {
    return res.json()
  })

  for (const c of components) {
  }

  const nodes_ = await fetch(new URL('graph/nodes', apiUrl), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json;charset=UTF-8'
    }
  }).then((res) => {
    return res.json()
  })

  const edges_ = await fetch(new URL('graph/edges', apiUrl), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json;charset=UTF-8'
    }
  }).then((res) => {
    return res.json()
  })

  nodes.value = nodes_
  edges.value = edges_
}

function startListening() {
  webSocketHandler.send('subscribe', { action: 'subscribe', streams: ['graph'] })
  receiveUpdates()
  syncGraph()
}

async function restartListening() {
  while (true) {
    await webSocketHandler.open

    startListening()
  }
}

onMounted(async () => {
  if (webSocketHandler.active) startListening()

  restartListening()
})

onUnmounted(() => {
  if (webSocketHandler.active) {
    webSocketHandler.send('subscribe', { action: 'unsubscribe', streams: ['graph'] })
  }
})

function logElements() {
  console.log(nodes.value)
  console.log(edges.value)
}
</script>

<template>
  <div class="wrapper">
    <VueFlow />
    <button @click="logElements">logElements</button>
  </div>
</template>

<style>
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';
</style>

<style scoped lang="sass">
.vue-flow
  height: 40vh
</style>
