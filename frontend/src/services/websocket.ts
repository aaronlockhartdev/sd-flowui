export class WebSocketHandler extends EventTarget {
  websocket: WebSocket | null
  active: boolean

  _timer: NodeJS.Timer | null
  readonly _url: string
  readonly _retrySec: number

  constructor(url: string, retrySec: number) {
    super()

    this.websocket = null
    this.active = false

    this._timer = null
    this._url = url
    this._retrySec = retrySec

    this.connect()
  }

  connect() {
    console.log('Establishing WebSocket connection...')

    this.websocket = new WebSocket(this._url)

    this.websocket.onopen = () => {
      this.active = true

      this.websocket!.onclose = () => {
        this.active = false

        super.dispatchEvent(new Event('close'))

        this._setTimer()
      }

      console.log('WebSocket connection established...')

      super.dispatchEvent(new Event('open'))
    }

    this.websocket.onclose = () => {
      this._setTimer()
    }

    this.websocket.onerror = () => {
      this.websocket?.close()
    }

    this.websocket.onmessage = (event) => {
      super.dispatchEvent(new CustomEvent('message', { detail: JSON.parse(event.data) }))
    }
  }

  _setTimer() {
    this._timer = setTimeout(() => {
      this.connect()
    }, this._retrySec)
  }

  async send(stream: string, data: object) {
    this.websocket!.send(JSON.stringify({ stream: stream, data: data }))
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
