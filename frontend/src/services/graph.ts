import { webSocketHandler } from '@/services/websocket'
import type { Element, Elements } from '@vue-flow/core'
import { reactive } from 'vue'

class GraphHandler {
  readonly _apiUrl: string
  readonly _elementsMap: Map<number | string, Element>
  _listening: boolean

  readonly elements: Elements

  constructor(apiUrl: string) {
    this._apiUrl = apiUrl
    this._elementsMap = new Map<string, Element>()
    this._listening = false

    this.elements = []

    webSocketHandler.onMessage('graph', (obj: object) => {
      const data = obj as { action: string; elements?: Elements; ids?: string[] }

      switch (data.action!) {
        case 'add' || 'update':
          for (const el of data.elements!) this._elementsMap.set(el.id, reactive(el))
          break
        case 'remove':
          for (const id of data.ids!) this._elementsMap.delete(id)
      }
    })

    webSocketHandler.onOpen(() => {
      if (this._listening) this.startListening()
    })
  }

  startListening() {
    this._listening = true

    if (webSocketHandler.active) {
      webSocketHandler.send('subscribe', { action: 'subscribe', streams: ['graph'] })
      this._syncGraph()
    }
  }

  stopListening() {
    this._listening = false

    if (webSocketHandler.active) {
      webSocketHandler.send('subscribe', { action: 'unsubscribe', streams: ['graph'] })
    }
  }

  async _syncGraph() {
    const components = await fetch(new URL('graph/components', this._apiUrl), {
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

    const elements = await fetch(new URL('graph/', this._apiUrl), {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json;charset=UTF-8'
      }
    }).then((res) => {
      return res.json()
    })

    this._elementsMap.clear()
    for (const el of elements) {
      this._elementsMap.set(el.id, reactive(el))
      this.elements.push(el)
    }
  }
}

export const graphHandler = reactive(
  new GraphHandler(
    process.env.NODE_ENV === 'development'
      ? 'http://localhost:8000/'
      : `${location.protocol}//${location.hostname}:${location.port}/api/v1/`
  )
)
