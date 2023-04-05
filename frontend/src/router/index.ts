import { createRouter, createWebHistory } from 'vue-router'
import GraphView from '@/views/GraphView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'graph',
      component: GraphView
    },
    {
      path: '/browser',
      name: 'browser',
      component: () => import('@/views/BrowserView.vue')
    }
  ]
})

export default router
