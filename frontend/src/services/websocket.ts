export class WebSocketHandler {
  websocket: WebSocket | null
  _timer: NodeJS.Timer | null
  active: boolean
  readonly _url: string
  readonly _retrySec: number
  readonly _onMessage: Map<string, ((data: object) => void)[]>
  readonly _onClose: Function[]
  readonly _onOpen: Function[]

  constructor(url: string, retrySec: number) {
    this.websocket = null
    this._timer = null
    this.active = false
    this._url = url
    this._retrySec = retrySec

    this._onMessage = new Map<string, ((data: object) => void)[]>()
    this._onClose = []
    this._onOpen = []

    this.init()
  }

  init() {
    console.log('Establishing WebSocket connection...')

    this.websocket = new WebSocket(this._url)

    this.websocket.onopen = (event) => {
      this.active = true

      console.log('WebSocket connection established...')

      for (const fn of this._onOpen) fn()

      this.websocket!.onclose = (event) => {
        this.active = false

        for (const fn of this._onClose) fn()

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

  async send(stream: string, data: object) {
    this.websocket!.send(JSON.stringify({ stream: stream, data: data }))
  }

  onMessage(stream: string, func: (data: object) => void) {
    if (this._onMessage.has(stream)) {
      this._onMessage.get(stream)!.push(func)
    } else {
      this._onMessage.set(stream, [func])
    }
  }

  onClose(func: Function) {
    this._onClose.push(func)
  }

  onOpen(func: Function) {
    this._onOpen.push(func)
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
