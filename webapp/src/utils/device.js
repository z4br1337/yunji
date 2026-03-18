import { ref, onMounted, onUnmounted } from 'vue'

/** 检测是否为 Windows 系统（Chrome/Edge 在 Windows 上渲染性能较差，需简化动画） */
export function isWindowsOS() {
  const ua = navigator.userAgent.toLowerCase()
  const plat = (navigator.platform || '').toLowerCase()
  return /win|windows/.test(ua) || plat === 'win32' || plat === 'windows'
}

export function useDevice() {
  const isMobile = ref(false)
  const isWindows = ref(isWindowsOS())
  const screenWidth = ref(window.innerWidth)

  function update() {
    screenWidth.value = window.innerWidth
    const ua = navigator.userAgent.toLowerCase()
    const mobileUA = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini|mobile/.test(ua)
    isMobile.value = mobileUA || window.innerWidth < 768
  }

  onMounted(() => {
    update()
    window.addEventListener('resize', update)
  })
  onUnmounted(() => window.removeEventListener('resize', update))

  return { isMobile, isWindows, screenWidth }
}
