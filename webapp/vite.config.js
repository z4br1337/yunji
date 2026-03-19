import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
        // 缓存静态资源，首次访问后二次加载更快
        maximumFileSizeToCacheInBytes: 3 * 1024 * 1024
      },
      manifest: {
        name: '云迹',
        short_name: '云迹',
        description: '哲法er交流学习平台',
        theme_color: '#4A90D9',
        background_color: '#F5F7FA',
        display: 'standalone',
        icons: [
          { src: '/favicon.ico', sizes: '48x48', type: 'image/x-icon' }
        ]
      }
    })
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    target: 'es2020',
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router']
        }
      }
    }
  }
})
