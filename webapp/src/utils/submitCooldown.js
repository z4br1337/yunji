import { ref, computed, onMounted, onUnmounted } from 'vue'

const STORAGE_KEY = 'yunji_publish_cooldown_until'
const COOLDOWN_MS = 3000

function readUntil() {
  const value = Number(localStorage.getItem(STORAGE_KEY) || 0)
  return Number.isFinite(value) ? value : 0
}

function startGlobalPublishCooldown() {
  localStorage.setItem(STORAGE_KEY, String(Date.now() + COOLDOWN_MS))
  window.dispatchEvent(new CustomEvent('yunji:publish-cooldown'))
}

export function useSubmitCooldown() {
  const remainingMs = ref(Math.max(0, readUntil() - Date.now()))
  let timer

  const isCoolingDown = computed(() => remainingMs.value > 0)
  const remainingSeconds = computed(() => Math.ceil(remainingMs.value / 1000))

  function sync() {
    remainingMs.value = Math.max(0, readUntil() - Date.now())
  }

  function start() {
    startGlobalPublishCooldown()
    sync()
  }

  function onCooldownStarted() {
    sync()
  }

  onMounted(() => {
    sync()
    window.addEventListener('yunji:publish-cooldown', onCooldownStarted)
    timer = window.setInterval(sync, 100)
  })

  onUnmounted(() => {
    window.removeEventListener('yunji:publish-cooldown', onCooldownStarted)
    window.clearInterval(timer)
  })

  return { isCoolingDown, remainingSeconds, start }
}
