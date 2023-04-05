import { ref } from 'vue'
import type { Ref } from 'vue'
import { defineStore } from 'pinia'
import { webSocketHandler } from '@/services/websocket'

export const useFilesStore = defineStore('files', () => {
  const apiUrl = import.meta.env.DEV
    ? 'http://localhost:8000/'
    : `${location.protocol}//${location.hostname}:${location.port}/api/v1/`

  interface Directory {
    [key: string]: (string | Directory)[]
  }

  const fileStructure: Ref<Directory> = ref({})

  async function init() {
    webSocketHandler.send('subscribe', { action: 'subcribe', streams: ['files'] })

    fileStructure.value = await fetch(new URL('files/data/structure', apiUrl), {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json;charset=UTF-8'
      }
    }).then((res) => {
      return res.json()
    })
  }

  webSocketHandler.addEventListener('message', (event) => {
    const msg = (<CustomEvent>event).detail

    if (msg.stream != 'files') return

    fileStructure.value = msg.data as Directory
  })

  if (webSocketHandler.active) init()

  webSocketHandler.addEventListener('open', init)

  return { fileStructure }
})
