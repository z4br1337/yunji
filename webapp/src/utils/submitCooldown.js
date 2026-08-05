import { ref, computed, onMounted, onUnmounted } from 'vue'

const STORAGE_KEY = 'yunji_publish_cooldown_until'
const COOLDOWN_MS = 3000
const LOCK_MESSAGE = '发布太快啦，请稍后再试'

function readUntil() {
  const value = Number(localStorage.getItem(STORAGE_KEY) || 0)
  return Number.isFinite(value) ? value : 0
}

function writeUntil(ts) {
  localStorage.setItem(STORAGE_KEY, String(ts))
}

function emitCooldownEvent() {
  window.dispatchEvent(new CustomEvent('yunji:publish-cooldown'))
}

function startGlobalPublishCooldown() {
  writeUntil(Date.now() + COOLDOWN_MS)
  emitCooldownEvent()
}

export function useSubmitCooldown() {
  const remainingMs = ref(Math.max(0, readUntil() - Date.now()))
  let timer

  const isCoolingDown = computed(() => remainingMs.value > 0)
  const remainingSeconds = computed(() => Math.ceil(remainingMs.value / 1000))
  const cooldownMessage = computed(() =>
    isCoolingDown.value ? `${remainingSeconds.value} 秒后可再次发布` : ''
  )

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

  function guardSubmit() {
    sync()
    return !isCoolingDown.value
  }

  function getBlockedMessage() {
    return isCoolingDown.value ? cooldownMessage.value : LOCK_MESSAGE
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

  return { isCoolingDown, remainingSeconds, cooldownMessage, start, guardSubmit, getBlockedMessage }
}
