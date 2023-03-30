import { webSocketHandler } from '@/services/websocket'
import type { Element, Elements } from '@vue-flow/core'
import { triggerRef, ref } from 'vue'
import type { Ref } from 'vue'

class GraphHandler {
  readonly _apiUrl: string
  readonly _elementsMap: Map<number | string, Element>
  readonly elementsRef: Ref<Elements>
  listening: boolean
  _interrupted: boolean

  get _elements(): Elements {
    return Array.from(this._elementsMap.values())
  }

  constructor(apiUrl: string) {
    this._apiUrl = apiUrl
    this._elementsMap = new Map<number | string, Element>()
    this.elementsRef = ref(this._elements)
    this.listening = false
    this._interrupted = false
  }

  startListening() {
    this.listening = true

    if (!webSocketHandler.active) return

    webSocketHandler.send('subscribe', { streams: ['graph'] })
    this._syncGraph()
  }

  stopListening() {
    this.listening = false

    if (!webSocketHandler.active) return

    webSocketHandler.send('unsubscribe', { streams: ['graph'] })
  }

  @webSocketHandler.onOpen
  _restartListening() {
    if (this.listening) this.startListening()
  }

  @webSocketHandler.onMessage('graph')
  _applyUpdate(data: { action: string; elements?: Elements; ids?: (number | string)[] }) {
    switch (data.action) {
      case 'add' || 'update':
        for (const el of data.elements!) {
          this._elementsMap.set(el.id, el)
        }
        break
      case 'remove':
        for (const id of data.ids!) {
          this._elementsMap.delete(id)
        }
    }

    triggerRef(this.elementsRef)
  }

  async _syncGraph() {
    const msg = await fetch(new URL('graph/', this._apiUrl), {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json;charset=UTF-8'
      }
    }).then((res) => {
      return res.json()
    })

    this._elementsMap.clear()
    for (const el of msg) {
      this._elementsMap.set(el.id, el.element)
    }

    triggerRef(this.elementsRef)
  }
}

export const graphHandler = new GraphHandler(
  process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000/'
    : `${location.protocol}//${location.hostname}:${location.port}/api/v1/`
)

graphHandler._syncGraph()
