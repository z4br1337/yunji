import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import './styles/global.css'
import * as api from './api/index.js'

const app = createApp(App)
app.use(router)
app.mount('#app')

if (typeof window !== 'undefined') {
  const idle = window.requestIdleCallback || ((cb) => window.setTimeout(cb, 1200))
  idle(() => {
    void api.getPosts({ page: 1, pageSize: 12, excludeEmotion: true, category: 'all' }).catch(() => {})
    void api.getHotTopics().catch(() => {})
    void api.getHotPostSnippets().catch(() => {})
    void api.listPublicActivityCampaigns().catch(() => {})
  })
}
