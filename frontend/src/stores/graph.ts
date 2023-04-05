import { defineStore } from 'pinia'

import { ref } from 'vue'
import type { Ref } from 'vue'

import type { Node, Edge, Element } from '@vue-flow/core'

import { app } from '@/main'
import { webSocketHandler } from '@/services/websocket'

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
    component: string
  }[]
}

export const useGraphStore = defineStore('graph', () => {
  const templates: Ref<Template[]> = ref([])
  const elements: Ref<Element[]> = ref([])

  let version = 0
  const elementMap = new Map<string, Element>()

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
      elements: elements_
    } = await fetch(new URL('graph/', app.config.globalProperties.apiURL), {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json;charset=UTF-8'
      }
    }).then((res) => {
      return res.json()
    })

    version = version_
    templates.value = templates_
    elements.value = elements_

    elementMap.clear()
    for (const element of elements_) {
      elementMap.set(element.id, element)
    }
  }

  webSocketHandler.addEventListener('message', (event) => {
    const msg = (<CustomEvent>event).detail

    if (msg.stream != 'graph') return

    const data = msg.data as {
      version: number
      action: string
      id?: string
      element?: Node
    }

    if (data.version <= version) return
    else if (data.version > version + 1) {
      fetchGraph()
      return
    }

    version++

    switch (data.action) {
      case undefined:
        throw new Error(`Required value 'action' not received`)
      case 'create':
        if (!data.element) throw new Error(`Required value 'element' not received`)

        elementMap.set(data.element.id, data.element)
        break
      case 'delete':
        if (!data.id) throw new Error(`Required value 'id' not received`)

        elementMap.delete(data.id)
        break
      case 'update':
        if (!data.element) throw new Error(`Required value 'element' not received`)

        const node = <Node>elementMap.get(data.element.id)

        if (!node) {
          fetchGraph()
          throw new Error(`Node '${data.element.id}' does not exist, resyncing graph...`)
        }

        if (data.element.data) node.data = { ...node.data, ...data.element.data }
        if (data.element.position) node.position = data.element.position

        break
      default:
        throw new Error(`Unrecognized action '${data.action}''`)
    }

    elements.value = Array.from(elementMap.values())
  })

  if (webSocketHandler.active) startListening()

  webSocketHandler.addEventListener('open', startListening)

  return { elements, templates }
})
