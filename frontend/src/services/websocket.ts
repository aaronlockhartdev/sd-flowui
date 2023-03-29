console.log('Establishing WebSocket connection')

function connect() {
  return new WebSocket(
    `${location.protocol.includes('https') ? 'wss' : 'ws'}://${location.hostname}:${
      process.env.NODE_ENV === 'development' ? 8000 : location.port
    }/api/v1/ws`
  )
}

let websocket = connect()
let retrier: NodeJS.Timer

const _on_message = new Map<string, ((data: object) => void)[]>()

websocket.onmessage = (event) => {
  for (const func of _on_message.get('*')!) {
    const data = JSON.parse(event.data)
    func(data)
  }
}

websocket.onopen = (event) => {
  clearInterval(retrier)
  console.log(event)
  console.log('Successfully established WebSocket connection...')
}

websocket.onclose = (event) => {
  retrier = setInterval(() => {
    websocket = connect()
  }, 1000)
}

window.websocket = websocket

export { websocket }
