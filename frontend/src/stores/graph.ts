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

export const useGraphStore = defineStore('graph', () => {
  const filesStore = useFilesStore()

  const templates: Ref<{ [key: string]: Template }> = ref({})
  const nodes: Ref<Node[]> = ref([])
  const edges: Ref<Edge[]> = ref([])
  const version = ref(0)

  function getNode(id: number) {
    return nodes.value.find((node) => node.id === `${id}`)
  }

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

  function nodeToVueFlow(node: NodeSchema): Node {
    return {
      id: `${node.id}`,
      type: 'node',
      position: node.position,
      data: { type: node.type, values: node.values },
      isValidTargetPos: connectionValid,
      isValidSourcePos: connectionValid
    }
  }

  function edgeToVueFlow(edge: EdgeSchema): Edge {
    return {
      id: edge.id,
      type: 'edge',
      updatable: true,
      source: `${edge.source}`,
      sourceHandle: edge.sourceHandle,
      target: `${edge.target}`,
      targetHandle: edge.targetHandle
    }
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
      case 'createNode':
        if (!data.node) throw new Error(`Required value 'node' not received`)

        nodes.value.push(nodeToVueFlow(data.node))
        break
      case 'deleteNode':
        if (!data.id) throw new Error(`Required value 'id' not received`)
        if (typeof data.id === 'string') throw new Error(`'id' is of type 'string'`)

        let idx = nodes.value.findIndex((node) => node.id === `${data.id}`)

        if (idx > -1) nodes.value.splice(idx, 1)
        else throw new Error(`Invalid node ID ${data.id}`)

        break
      case 'updatePositionNode':
        if (!data.node) throw new Error(`Required value 'node' not received`)

        const node = getNode(data.node.id)

        if (!node) {
          fetchGraph()
          throw new Error(`Node '${data.node.id}' does not exist, resyncing graph...`)
        }

        node.position = data.node.position

        break
      case 'updateValuesNode':
        if (!data.node) throw new Error(`Required value 'node' not received`)

        const node_ = getNode(data.node.id)

        if (!node_) {
          fetchGraph()
          throw new Error(`Node '${data.node.id}' does not exist, resyncing graph...`)
        }

        node_.data.values = { ...node_.data.values, ...data.node.values }

        break

      case 'createEdge':
        if (!data.edge) throw new Error(`Required value 'edge' not received`)

        edges.value.push(edgeToVueFlow(data.edge))

        break
      case 'deleteEdge':
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

  function addNode(type: string, position: { x: number; y: number }) {
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

    console.log({
      item: {
        version: version.value - 1,
        action: 'createNode',
        ...node
      }
    })

    webSocketHandler.send('graph', {
      item: {
        version: version.value - 1,
        action: 'createNode',
        ...node
      }
    })

    return node.id
  }

  function removeNode(id: number) {
    const idx = nodes.value.findIndex((node) => node.id === `${id}`)

    if (idx > -1) nodes.value.splice(idx, 1)
    else throw new Error(`Invalid node ID ${id}`)

    version.value++

    webSocketHandler.send('graph', {
      item: {
        version: version.value - 1,
        action: 'deleteNode',
        id: id
      }
    })
  }

  function updatePositionNode(id: number, position: { x: number; y: number }) {
    const node = nodes.value.find((node) => node.id === `${id}`)

    if (!node) throw new Error(`Invalid node ID '${id}'`)

    version.value++

    node.position = position

    webSocketHandler.send('graph', {
      item: {
        version: version.value - 1,
        action: 'updatePositionNode',
        id: id,
        position: position
      }
    })
  }

  function updateValuesNode(id: number, values: { [key: string]: any }) {
    const node = nodes.value.find((node) => node.id === `${id}`)

    if (!node) throw new Error(`Invalid node ID '${id}'`)

    version.value++

    node.data.values = { ...node.data.values, ...values }

    webSocketHandler.send('graph', {
      item: {
        version: version.value - 1,
        action: 'updateValuesNode',
        id: id,
        values: values
      }
    })
  }

  function addEdge(source: number, target: number, sourceHandle: string, targetHandle: string) {
    const edge: EdgeSchema = {
      id: `e${source}${sourceHandle}-${target}${targetHandle}`,
      source: source,
      target: target,
      sourceHandle: sourceHandle,
      targetHandle: targetHandle
    }

    version.value++

    edges.value.push(edgeToVueFlow(edge))

    webSocketHandler.send('graph', {
      item: {
        version: version.value - 1,
        action: 'createEdge',
        ...edge
      }
    })

    return edge.id
  }

  function removeEdge(id: string) {
    const idx = edges.value.findIndex((edge) => edge.id === id)

    if (idx > -1) edges.value.splice(idx, 1)
    else throw new Error(`Invalid edge ID ${id}`)

    version.value++

    webSocketHandler.send('graph', {
      item: {
        version: version.value - 1,
        action: 'deleteEdge',
        id: id
      }
    })
  }

  function connectionValid(connection: Connection) {
    const source = nodes.value.find((node) => node.id === connection.source)
    const target = nodes.value.find((node) => node.id === connection.target)

    if (!source) throw new Error(`Invalid source node '${connection.source}'`)
    if (!target) throw new Error(`Invalid target node '${connection.target}'`)

    if (!connection.sourceHandle) throw new Error(`Connection requires 'sourceHandle'`)
    if (!connection.targetHandle) throw new Error(`Connection requires 'targetHandle'`)

    const sourceType = templates.value[source.data.type].outputs[connection.sourceHandle].type

    const targetType = templates.value[target.data.type].inputs[connection.targetHandle].type

    return sourceType === targetType
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
    updateValuesNode,
    addEdge,
    removeEdge
  }
})
