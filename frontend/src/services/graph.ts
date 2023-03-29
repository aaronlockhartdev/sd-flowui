import { webSocketHandler } from '@/services/websocket'
import type {  Elements } from '@vue-flow/core'

class GraphHandler {
  readonly _apiUrl: string
  elements: Elements

  constructor(apiUrl: string) {
    this._apiUrl = apiUrl
    this.elements = []
  }

  startListening() {
    webSocketHandler.send('subscribe', { streams: ['graph'] })
    this._syncGraph().then((data) => {
      this.elements = data
    })
  }

  stopListening() {
    webSocketHandler.send('unsubscribe', { streams: ['graph'] })
  }

  @webSocketHandler.onMessage('graph/node')
  _applyNodeUpdate(data: {
    id: string
    type: string
    data: object
    position: { x: number; y: number }
  }) {
    if (data.type === 'add') {
      this.elements.push({
        id: data.id,
        data: data.data,
        position: data.position
      })
    } else if (data.type === 'remove') {
      this.elements.
    }
  }

  async _syncGraph() {
    const data = (
      await fetch(new URL('graph/', this._apiUrl), {
        method: 'GET',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json;charset=UTF-8'
        }
      })
    ).json()

    console.log(data)

    return data
  }
}

export const graphHandler = new GraphHandler(
  process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000/'
    : `${location.protocol}//${location.hostname}:${location.port}/api/v1/`
)

graphHandler._syncGraph()
