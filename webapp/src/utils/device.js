import { ref, onMounted, onUnmounted } from 'vue'

export function useDevice() {
  const isMobile = ref(false)
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

  return { isMobile, screenWidth }
}
