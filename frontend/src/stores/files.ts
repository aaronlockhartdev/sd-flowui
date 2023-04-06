import { ref } from 'vue'
import type { Ref } from 'vue'
import { defineStore } from 'pinia'

import { app } from '@/main'

import { webSocketHandler } from '@/services/websocket'

export interface Directory {
  [key: string]: Directory | null
}

export const useFilesStore = defineStore('files', () => {
  const fileStructure: Ref<Directory> = ref({})

  async function startListening() {
    webSocketHandler.send('streams', { action: 'subscribe', streams: ['files'] })

    fileStructure.value = await fetch(
      new URL('files/data/structure', app.config.globalProperties.apiURL),
      {
        method: 'GET',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json;charset=UTF-8'
        }
      }
    ).then((res) => {
      return res.json()
    })
  }

  webSocketHandler.addEventListener('message', (event) => {
    const msg = (<CustomEvent>event).detail

    if (msg.stream != 'files') return

    fileStructure.value = msg.data as Directory
  })

  if (webSocketHandler.active) startListening()

  webSocketHandler.addEventListener('open', startListening)

  function getSubStructure(path: string[]) {
    let subStructure = fileStructure.value

    for (const dir of path) {
      const subSubStructure = subStructure[dir]

      if (!subSubStructure) return {}

      subStructure = subSubStructure
    }

    return subStructure
  }

  return { fileStructure, getSubStructure }
})
