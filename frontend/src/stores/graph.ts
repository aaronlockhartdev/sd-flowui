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
    data: { type: node.type, values: node.values }
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

    nodes.value = nodes_.map(nodeToVueFlow)
    edges.value = edges_.map(edgeToVueFlow)
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

        nodes.value.push(nodeToVueFlow(data.node))
        break
      case 'delete_node':
        if (!data.id) throw new Error(`Required value 'id' not received`)
        if (typeof data.id === 'string') throw new Error(`'id' is of type 'string'`)

        let idx = nodes.value.findIndex((node) => node.id === `${data.id}`)

        if (idx > -1) nodes.value.splice(idx, 1)
        else throw new Error(`Invalid node ID ${data.id}`)

        break
      case 'update_position_node':
        if (!data.node) throw new Error(`Required value 'node' not received`)

        let node = nodes.value.find((node) => node.id === `${data.node!.id}`)

        if (!node) {
          fetchGraph()
          throw new Error(`Node '${data.node.id}' does not exist, resyncing graph...`)
        }

        node.position = data.node.position

        break
      case 'update_values_node':
        if (!data.node) throw new Error(`Required value 'node' not received`)

        node = nodes.value.find((node) => node.id === `${data.node!.id}`)

        if (!node) {
          fetchGraph()
          throw new Error(`Node '${data.node.id}' does not exist, resyncing graph...`)
        }

        node.data.values = { ...node.data.values, ...data.node.values }

      case 'create_edge':
        if (!data.edge) throw new Error(`Required value 'edge' not received`)

        edges.value.push(edgeToVueFlow(data.edge))

        break
      case 'delete_edge':
        if (!data.id) throw new Error(`Required value 'id' not received`)
        if (typeof data.id === 'number') throw new Error(`'id' is of type 'number'`)

        idx = edges.value.findIndex((edge) => edge.id === data.id)

        if (idx > -1) edges.value.splice(idx, 1)
        else throw new Error(`Invalid edge ID ${data.id}`)

        break
      default:
        throw new Error(`Unrecognized action '${data.action}''`)
    }
  })

  if (webSocketHandler.active) startListening()

  webSocketHandler.addEventListener('open', startListening)

  function connectionValid(connection: Connection) {
    const source = nodes.value.find((node) => node.id === connection.source)
    const target = nodes.value.find((node) => node.id === connection.target)

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

    nodes.value.push(nodeToVueFlow(node))

    version.value++

    await webSocketHandler.send('graph', {
      version: version.value - 1,
      action: 'create_node',
      id: version.value - 1,
      node: node
    })
  }

  async function removeNode(id: number) {
    let idx = nodes.value.findIndex((node) => node.id === `${id}`)

    if (idx > -1) nodes.value.splice(idx, 1)
    else throw new Error(`Invalid node ID ${id}`)

    version.value++

    await webSocketHandler.send('graph', {
      version: version.value - 1,
      action: 'delete_node',
      id: id
    })
  }

  async function updatePositionNode(id: number, position: { x: number; y: number }) {
    const node = nodes.value.find((node) => node.id === `${id}`)

    if (!node) throw new Error(`Invalid node ID '${id}'`)

    version.value++

    node.position = position

    await webSocketHandler.send('graph', {
      version: version.value - 1,
      action: 'update_position_node',
      node: {
        id: id,
        position: position
      }
    })
  }

  async function updateValuesNode(id: number, values: { [key: string]: any }) {
    const node = nodes.value.find((node) => node.id === `${id}`)

    if (!node) throw new Error(`Invalid node ID '${id}'`)

    version.value++

    node.data.values = { ...node.data.values, ...values }

    await webSocketHandler.send('graph', {
      version: version.value - 1,
      action: 'update_position_node',
      node: {
        id: id,
        values: values
      }
    })
  }

  return {
    nodes,
    edges,
    version,
    templates,
    connectionValid,
    addNode,
    removeNode,
    updatePositionNode,
    updateValuesNode
  }
})
