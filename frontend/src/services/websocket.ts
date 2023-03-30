export class WebSocketHandler {
  websocket: WebSocket | null
  _timer: NodeJS.Timer | null
  active: boolean
  readonly _url: string
  readonly _retrySec: number
  readonly _onMessage: Map<string, ((event: object) => void)[]>
  readonly _onClose: ((..._: any) => void)[]
  readonly _onOpen: ((..._: any) => void)[]

  constructor(url: string, retrySec: number) {
    this.websocket = null
    this._timer = null
    this.active = false
    this._url = url
    this._retrySec = retrySec

    this._onMessage = new Map<string, ((data: object) => void)[]>()
    this._onClose = Array<(..._: any) => void>()
    this._onOpen = Array<(..._: any) => void>()

    this.init()
  }

  init() {
    console.log('Establishing WebSocket connection...')

    this.websocket = new WebSocket(this._url)

    this.websocket.onopen = (event) => {
      this.active = true

      for (const fn of this._onOpen) {
        fn()
      }

      this.websocket!.onclose = (event) => {
        this.active = false

        for (const fn of this._onClose) {
          fn()
        }
        this._setTimer()
      }
    }

    this.websocket.onclose = (event) => {
      this._setTimer()
    }

    this.websocket.onerror = (event) => {
      this.websocket?.close()
    }

    this.websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (this._onMessage.has(data.stream)) {
        for (const fn of this._onMessage.get(data.stream)!) {
          fn(data.data)
        }
      }
    }
  }

  _setTimer() {
    this._timer = setTimeout(() => {
      this.init()
    }, this._retrySec)
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

  onClose(target: any, memberName: string, propertyDescriptor: PropertyDescriptor) {
    this._onClose.push(propertyDescriptor.value)
  }

  onOpen(target: any, memberName: string, propertyDescriptor: PropertyDescriptor) {
    this._onOpen.push(propertyDescriptor.value)
  }
}

export const webSocketHandler = new WebSocketHandler(
  process.env.NODE_ENV === 'development'
    ? 'ws://localhost:8000/ws'
    : `${location.protocol.includes('https') ? 'wss' : 'ws'}://${location.hostname}:${
        location.port
      }/api/v1/ws`,
  1000
)
