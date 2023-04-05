import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Initialize services
import '@/services/websocket'

// Initialize app
import App from './App.vue'
import router from './router'

import './assets/main.css'

export const app = createApp(App)

app.use(createPinia())
app.use(router)

app.config.globalProperties.apiURL = import.meta.env.PROD
  ? `${location.protocol}//${location.hostname}:${location.port}/api/v1/`
  : 'http://localhost:8000/'

app.mount('#app')
