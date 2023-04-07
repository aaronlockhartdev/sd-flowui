import { defineStore } from 'pinia'

import { ref } from 'vue'
import type { Ref } from 'vue'

import type { Node, Edge, Connection } from '@vue-flow/core'

import { app } from '@/main'
import { webSocketHandler } from '@/services/websocket'
import { useFilesStore } from '@/stores/files'
import type { Directory } from '@/stores/files'

export interface Template {
  inputs: {
    id: string
    name: string
    type: string
  }[]
  outputs: {
    id: string
    name: string
    type: string
  }[]
  params: {
    id: string
    name: string
    component: { type: string; [key: string]: any }
  }[]
}

export const useGraphStore = defineStore('graph', () => {
  const filesStore = useFilesStore()

  const templates: Ref<{ [key: string]: Template }> = ref({})
  const nodes: Ref<Node[]> = ref([])
  const edges: Ref<Edge[]> = ref([])
  const version = ref(0)

  const nodeMap = new Map<string, Node>()
  const edgeMap = new Map<string, Edge>()

  function startListening() {
    webSocketHandler.send('streams', { action: 'subscribe', streams: ['graph'] })

    fetchGraph()
  }

  function stopListening() {
    webSocketHandler.send('streams', { action: 'unsubscribe', streams: ['graph'] })
  }

  async function fetchGraph() {
    const {
      version: version_,
      templates: templates_,
      nodes: nodes_,
      edges: edges_
    } = await fetch(new URL('graph/', app.config.globalProperties.apiURL), {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json;charset=UTF-8'
      }
    }).then((res) => {
      return res.json()
    })

    version.value = version_
    templates.value = templates_
    nodes.value = nodes_
    edges.value = edges_

    console.log(templates_)

    nodeMap.clear()
    for (const node of nodes_) {
      nodeMap.set(node.id, node)
    }

    edgeMap.clear()
    for (const edge of edges_) {
      edgeMap.set(edge.id, edge)
    }
  }

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

    console.log(data)

    if (data.version <= version.value) return
    else if (data.version > version.value + 1) {
      fetchGraph()
      return
    }

    version.value++

    switch (data.action) {
      case undefined:
        throw new Error(`Required value 'action' not received`)
      case 'create_node':
        if (!data.node) throw new Error(`Required value 'node' not received`)

        nodeMap.set(data.node.id, data.node)
        break
      case 'delete_node':
        if (!data.id) throw new Error(`Required value 'id' not received`)

        nodeMap.delete(data.id)
        break
      case 'update_node':
        if (!data.node) throw new Error(`Required value 'node' not received`)

        const node = nodeMap.get(data.node.id)

        if (!node) {
          fetchGraph()
          throw new Error(`Node '${data.node.id}' does not exist, resyncing graph...`)
        }

        if (data.node.data) node.data = { ...node.data, ...data.node.data }
        if (data.node.position) node.position = data.node.position

        break
      case 'create_edge':
        if (!data.edge) throw new Error(`Required value 'edge' not received`)

        edgeMap.set(data.edge.id, data.edge)
        break
      case 'delete_edge':
        if (!data.id) throw new Error(`Required value 'id' not received`)

        edgeMap.delete(data.id)
        break
      default:
        throw new Error(`Unrecognized action '${data.action}''`)
    }

    if (data.action.includes('node')) nodes.value = Array.from(nodeMap.values())
    else if (data.action.includes('edge')) edges.value = Array.from(edgeMap.values())
  })

  if (webSocketHandler.active) startListening()

  webSocketHandler.addEventListener('open', startListening)

  function connectionValid(connection: Connection) {
    let sourceHandleType = ''

    for (const output of templates.value[nodeMap.get(connection.source)?.data.label].outputs) {
      if (output.id === connection.sourceHandle) {
        sourceHandleType = output.type
        break
      }
    }

    for (const input of templates.value[nodeMap.get(connection.target)?.data.label].inputs)
      if (input.id === connection.targetHandle) return input.type === sourceHandleType
  }

  async function addNode(type: string, position?: { x: number; y: number }) {
    const params: { [key: string]: any } = {}

    for (const param of templates.value[type].params) {
      if (param.component.type === 'FileDropdown') {
        function recurse(subStructure: Directory): string[] {
          let [k, v]: [string | null, Directory | null] = [null, null]
          for ([k, v] of Object.entries(subStructure)) {
            if (!v) return [k]
          }

          if (!k || !v) return ['']

          return [k, ...recurse(v)]
        }

        params[param.id] = recurse(filesStore.getSubStructure(param.component.directory))
      } else {
        params[param.id] = param.component.default
      }
    }

    console.log(params)

    await webSocketHandler.send('graph', {
      version: version.value,
      action: 'create_node',
      id: version.value,
      node: {
        type: type,
        params: params,
        pos: position
      }
    })
  }

  return { nodes, edges, version, templates, connectionValid, addNode }
})
