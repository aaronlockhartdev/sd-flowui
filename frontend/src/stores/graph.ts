import { defineStore } from 'pinia'
import { webSocketHandler } from '@/services/websocket'

export const useGraphStore = defineStore('graph', () => {
  const apiUrl = import.meta.env.DEV
    ? 'http://localhost:8000/'
    : `${location.protocol}//${location.hostname}:${location.port}/api/v1/`
})
