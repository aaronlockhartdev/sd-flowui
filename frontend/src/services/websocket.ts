export class WebSocketHandler {
  websocket: WebSocket | null
  readonly _onMessage: Map<string, ((event: object) => void)[]>
  readonly _url: string
  _timer: NodeJS.Timer | null
  readonly _retrySec: number

  constructor(url: string, retrySec: number) {
    this.websocket = null
    this._onMessage = new Map<string, ((data: object) => void)[]>()
    this._onMessage.set('*', [console.log])
    this._url = url
    this._timer = null
    this._retrySec = retrySec

    this.init()
  }

  init() {
    console.log('Establishing WebSocket connection...')

    this.websocket = new WebSocket(this._url)

    this.websocket.onopen = (event) => {
      console.log(event)
      console.log('WebSocket connection successfully established...')
    }

    this.websocket.onclose = (event) => {
      console.log(event)
      this._timer = setTimeout(() => {
        this.init()
      }, this._retrySec)
    }

    this.websocket.onerror = (event) => {
      this.websocket?.close()
    }

    this.websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      for (const fn of this._onMessage.get('*')!) {
        fn(data.data)
      }
      if (this._onMessage.has(data.stream)) {
        for (const fn of this._onMessage.get(data.stream)!) {
          fn(data.data)
        }
      }
    }
  }

  send(stream: string, data: object) {
    this.websocket?.send(JSON.stringify({ stream: stream, data: data }))
  }

  onMessage(stream: string) {
    return (target: any, memberName: string, propertyDescriptor: PropertyDescriptor) => {
      if (this._onMessage.has(stream)) {
        this._onMessage.get(stream)!.push(propertyDescriptor.value)
      } else {
        this._onMessage.set(stream, [propertyDescriptor.value])
      }

      return propertyDescriptor
    }
  }
}

export const webSocketHandler = new WebSocketHandler(
  // process.env.NODE_ENV === 'development'
  //   ? 'ws://localhost:8000/ws'
  //   : `${location.protocol.includes('https') ? 'wss' : 'ws'}://${location.hostname}:${
  //       location.port
  //     }/api/v1/ws`,
  // 1000
  'ws://localhost:8000/api/v1/ws',
  1000
)
