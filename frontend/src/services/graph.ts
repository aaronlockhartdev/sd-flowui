import { WebSocketHandler, webSocketHandler } from '@/services/websocket'
import type { Element, Elements } from '@vue-flow/core'
import { triggerRef } from 'vue'
import type { Ref } from 'vue'

class GraphHandler {
  readonly _apiUrl: string
  readonly _webSocketHandler: WebSocketHandler
  readonly _elementsMap: Map<number | string, Element>
  readonly _refs: Set<Ref>
  _listening: boolean

  get elements(): Elements {
    return Array.from(this._elementsMap.values())
  }

  constructor(apiUrl: string, webSocketHandler: WebSocketHandler) {
    this._apiUrl = apiUrl
    this._webSocketHandler = webSocketHandler
    this._elementsMap = new Map<number | string, Element>()
    this._refs = new Set<Ref>()
    this._listening = false

    this._webSocketHandler.onMessage('graph', (obj: object) => {
      const data = obj as { action: string; elements?: Elements; ids?: (number | string)[] }

      switch (data.action!) {
        case 'add' || 'update':
          for (const el of data.elements!) this._elementsMap.set(el.id, el)
          break
        case 'remove':
          for (const id of data.ids!) this._elementsMap.delete(id)
      }
    })

    this._webSocketHandler.onOpen(() => {
      if (this._listening) this._startListening()
    })
  }

  addRef(ref: Ref) {
    this._refs.add(ref)

    if (!this._listening) this._startListening()
  }

  removeRef(ref: Ref) {
    this._refs.delete(ref)

    if (!this._refs.size) this._stopListening()
  }

  _startListening() {
    this._listening = true

    if (this._webSocketHandler.active) {
      this._webSocketHandler.send('subscribe', { action: 'subscribe', streams: ['graph'] })
      this._syncGraph()
    }
  }

  _stopListening() {
    this._listening = false

    if (this._webSocketHandler.active) {
      this._webSocketHandler.send('subscribe', { action: 'unsubscribe', streams: ['graph'] })
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

    console.log(components)

    const elements = await fetch(new URL('graph', this._apiUrl), {
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
      this._elementsMap.set(el.id, el.element)
    }

    for (const ref_ of this._refs) triggerRef(ref_)
  }
}

export const graphHandler = new GraphHandler(
  process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000/'
    : `${location.protocol}//${location.hostname}:${location.port}/api/v1/`,
  webSocketHandler
)
