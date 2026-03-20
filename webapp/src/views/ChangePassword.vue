<template>
  <div class="page-container redirect-wrap">
    <p class="text-muted text-sm">正在跳转到设置…</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

onMounted(() => {
  router.replace({ path: '/settings/preferences', query: { tab: route.query.tab || 'security' } })
})
</script>

<style scoped>
.redirect-wrap { padding: 24px; text-align: center; }
</style>
