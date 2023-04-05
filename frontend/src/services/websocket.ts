export class WebSocketHandler extends EventTarget {
  websocket: WebSocket | null
  active: boolean

  _timer: NodeJS.Timer | null

  constructor() {
    super()

    this.websocket = null
    this.active = false

    this._timer = null

    this.connect()
  }

  connect() {
    console.log('Establishing WebSocket connection...')

    this.websocket = new WebSocket(
      import.meta.env.DEV
        ? 'ws://localhost:8000/ws'
        : `${location.protocol.includes('https') ? 'wss' : 'ws'}://${location.hostname}:${
            location.port
          }/api/v1/ws`
    )

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
    }, 1000)
  }

  async send(stream: string, data: object) {
    if (!this.websocket) throw new Error('Websocket not connected')

    this.websocket.send(JSON.stringify({ stream: stream, data: data }))
  }
}

export const webSocketHandler = new WebSocketHandler()
