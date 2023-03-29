<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { webSocketHandler } from '@/services/websocket'
import { VueFlow } from '@vue-flow/core'

onMounted(() => {
  webSocketHandler.send('subscribe', { streams: ['graph'] })
})

onUnmounted(() => {
  webSocketHandler.send('unsubscribe', { streams: ['graph'] })
})

const elements =
</script>
