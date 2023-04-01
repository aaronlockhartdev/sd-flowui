import { resolve } from 'path'

export class WebSocketHandler {
  websocket: WebSocket | null
  active: boolean
  readonly open: Promise<void>
  readonly close: Promise<void>
  readonly _messageCallbacks: Map<
    string,
    { promise: Promise<object>; res: (value: object) => void }
  >
  _openRes: () => void = () => {}
  _closeRes: () => void = () => {}
  _timer: NodeJS.Timer | null
  readonly _url: string
  readonly _retrySec: number

  constructor(url: string, retrySec: number) {
    this.websocket = null
    this._timer = null
    this.active = false
    this._url = url
    this._retrySec = retrySec

    this.open = new Promise((res, _) => {
      this._openRes = res
    })
    this.close = new Promise((res, _) => {
      this._closeRes = res
    })
    this._messageCallbacks = new Map()

    this.connect()
  }

  connect() {
    console.log('Establishing WebSocket connection...')

    this.websocket = new WebSocket(this._url)

    this.websocket.onopen = (event) => {
      this.active = true

      console.log('WebSocket connection established...')

      this._openRes()

      this.websocket!.onclose = (event) => {
        this.active = false

        this._closeRes()

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
      const msg = JSON.parse(event.data)
      if (this._messageCallbacks.has(msg.stream)) {
        this._messageCallbacks.get(msg.stream)?.res(msg.data)
      }
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

  message(stream: string): Promise<object> {
    if (!this._messageCallbacks.has(stream)) {
      let res_: (value: object) => void
      const promise = new Promise<object>((res, _) => {
        res_ = res
      })
      this._messageCallbacks.set(stream, { promise: promise, res: res_! })
    }

    return this._messageCallbacks.get(stream)?.promise!
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
