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
    [key: string]: {
      name: string
      type: string
    }
  }
  outputs: {
    [key: string]: {
      name: string
      type: string
    }
  }
  values: {
    [key: string]: {
      name: string
      component: { type: string; [key: string]: any }
    }
  }
}

interface NodeSchema {
  id: number
  type: string
  values: { [key: string]: any }
  position: { x: number; y: number }
}

interface EdgeSchema {
  id: string
  source: number
  sourceHandle: string
  target: number
  targetHandle: string
}

function nodeToVueFlow(node: NodeSchema): Node {
  return {
    id: `${node.id}`,
    type: 'node',
    position: node.position,
    data: node
  }
}

function edgeToVueFlow(edge: EdgeSchema): Edge {
  return {
    id: edge.id,
    source: `${edge.source}`,
    sourceHandle: edge.sourceHandle,
    target: `${edge.target}`,
    targetHandle: edge.targetHandle
  }
}

export const useGraphStore = defineStore('graph', () => {
  const filesStore = useFilesStore()

  const templates: Ref<{ [key: string]: Template }> = ref({})
  const nodes: Ref<Node[]> = ref([])
  const edges: Ref<Edge[]> = ref([])
  const version = ref(0)

  const nodeMap = new Map<number, Node>()
  const edgeMap = new Map<string, Edge>()

  function startListening() {
    webSocketHandler.send('streams', { action: 'subscribe', streams: ['graph'] })

    fetchGraph()
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

    nodeMap.clear()
    for (const node of nodes_) {
      nodeMap.set(node.id, nodeToVueFlow(node))
    }

    edgeMap.clear()
    for (const edge of edges_) {
      edgeMap.set(edge.id, edgeToVueFlow(edge))
    }

    nodes.value = Array.from(nodeMap.values())
    edges.value = Array.from(edgeMap.values())
  }

  webSocketHandler.addEventListener('message', (event) => {
    const msg = (<CustomEvent>event).detail

    if (msg.stream != 'graph') return

    const data = msg.data as {
      version: number
      action: string
      id?: string | number
      node?: NodeSchema
      edge?: EdgeSchema
    }

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

        nodeMap.set(data.node.id, nodeToVueFlow(data.node))
        break
      case 'delete_node':
        if (!data.id) throw new Error(`Required value 'id' not received`)
        if (typeof data.id === 'string') throw new Error(`'id' is of type 'string'`)

        nodeMap.delete(data.id)
        break
      case 'update_node':
        if (!data.node) throw new Error(`Required value 'node' not received`)

        const oldNode = nodeMap.get(data.node.id)

        if (!oldNode) {
          fetchGraph()
          throw new Error(`Node '${data.node.id}' does not exist, resyncing graph...`)
        }

        const newNode = nodeToVueFlow(data.node)

        if (newNode.data) oldNode.data = { ...oldNode.data, ...newNode.data }
        if (newNode.position) oldNode.position = newNode.position

        break
      case 'create_edge':
        if (!data.edge) throw new Error(`Required value 'edge' not received`)

        edgeMap.set(data.edge.id, edgeToVueFlow(data.edge))
        break
      case 'delete_edge':
        if (!data.id) throw new Error(`Required value 'id' not received`)
        if (typeof data.id === 'number') throw new Error(`'id' is of type 'number'`)

        edgeMap.delete(data.id)
        break
      default:
        throw new Error(`Unrecognized action '${data.action}''`)
    }

    nodes.value = Array.from(nodeMap.values())
    edges.value = Array.from(edgeMap.values())
  })

  if (webSocketHandler.active) startListening()

  webSocketHandler.addEventListener('open', startListening)

  function connectionValid(connection: Connection) {
    const source = nodeMap.get(parseInt(connection.source))
    const target = nodeMap.get(parseInt(connection.target))

    if (!source) throw new Error(`Invalid source node '${connection.source}'`)
    if (!target) throw new Error(`Invalid target node '${connection.target}'`)

    if (!connection.sourceHandle) throw new Error(`Connection requires 'sourceHandle'`)
    if (!connection.targetHandle) throw new Error(`Connection requires 'targetHandle'`)

    const sourceType =
      templates.value[source.data.type].values[connection.sourceHandle].component.type

    const targetType =
      templates.value[target.data.type].values[connection.targetHandle].component.type

    return sourceType === targetType
  }

  async function addNode(type: string, position: { x: number; y: number }) {
    const values: { [key: string]: any } = {}

    for (const [k, v] of Object.entries(templates.value[type].values)) {
      if (v.component.type === 'FileDropdown') {
        function recurse(subStructure: Directory): string[] {
          let [dir, file]: [string | null, Directory | null] = [null, null]
          for ([dir, file] of Object.entries(subStructure)) if (!file) return [dir]

          if (!dir || !file) return ['']

          return [dir, ...recurse(file)]
        }

        values[k] = recurse(filesStore.getSubStructure(v.component.directory))
      } else {
        values[k] = v.component.default
      }
    }

    const node: NodeSchema = {
      id: version.value,
      type: type,
      values: values,
      position: position
    }

    nodeMap.set(version.value - 1, nodeToVueFlow(node))

    version.value++
    nodes.value = Array.from(nodeMap.values())

    await webSocketHandler.send('graph', {
      version: version.value - 1,
      action: 'create_node',
      id: version.value - 1,
      node: node
    })
  }

  async function removeNode(id: number) {
    if (!nodeMap.has(id)) throw new Error(`Invalid node ID '${id}'`)

    version.value++
    nodeMap.delete(id)

    await webSocketHandler.send('graph', {
      version: version.value - 1,
      action: 'delete_node',
      id: id
    })
  }

  async function updateNode(
    id: number,
    values?: { [key: string]: any },
    position?: { x: number; y: number }
  ) {
    const node = nodeMap.get(id)

    if (!node) throw new Error(`Invalid node ID '${id}'`)

    version.value++

    if (values) node.data.values = { ...node.data.values, ...values }
    if (position) node.position = position
  }

  return { nodes, edges, version, templates, connectionValid, addNode, removeNode, updateNode }
})
