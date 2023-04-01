import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Initialize services
import '@/services/websocket'
// import '@/services/graph.ts.bak'

// Initialize app
import App from './App.vue'
import router from './router'

// import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
