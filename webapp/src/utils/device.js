import { ref, onMounted, onUnmounted } from 'vue'

/** 检测是否为 Windows 系统（Chrome/Edge 在 Windows 上渲染性能较差，需简化动画） */
export function isWindowsOS() {
  const ua = navigator.userAgent.toLowerCase()
  const plat = (navigator.platform || '').toLowerCase()
  return /win|windows/.test(ua) || plat === 'win32' || plat === 'windows'
}

export function isAndroidOS() {
  return /android/.test(navigator.userAgent.toLowerCase())
}

export function isIOS() {
  return /iphone|ipad|ipod/.test(navigator.userAgent.toLowerCase())
}

export function useDevice() {
  const isMobile = ref(false)
  const screenWidth = ref(window.innerWidth)
  const isWindows = ref(false)
  const isAndroid = ref(false)
  const isIOS = ref(false)

  function update() {
    screenWidth.value = window.innerWidth
    const ua = navigator.userAgent.toLowerCase()
    const p = (navigator.platform || '').toLowerCase()
    const mobileUA = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini|mobile/.test(ua)
    isMobile.value = mobileUA || window.innerWidth < 768
    isWindows.value = /win|windows/.test(ua) || p === 'win32' || p === 'windows'
    isAndroid.value = /android/.test(ua)
    isIOS.value = /iphone|ipad|ipod/.test(ua)
  }

  onMounted(() => {
    update()
    window.addEventListener('resize', update)
  })
  onUnmounted(() => window.removeEventListener('resize', update))

  return { isMobile, screenWidth, isWindows, isAndroid, isIOS }
}
