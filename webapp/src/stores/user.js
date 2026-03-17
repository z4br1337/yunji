import { reactive, readonly } from 'vue'
import * as api from '../api/index.js'

const state = reactive({
  userInfo: null,
  isLoggedIn: false,
  isAdmin: false,
  profileCompleted: false
})

export function useUserStore() {
  async function login(username, password) {
    const user = await api.login(username, password)
    state.userInfo = user
    state.isLoggedIn = true
    state.isAdmin = user.role === 'admin'
    state.profileCompleted = !!user.profileCompleted
    localStorage.setItem('userInfo', JSON.stringify(user))
    return user
  }

  async function refreshProfile() {
    const user = await api.getProfile()
    state.userInfo = user
    state.isAdmin = user.role === 'admin'
    state.profileCompleted = !!user.profileCompleted
    localStorage.setItem('userInfo', JSON.stringify(user))
    return user
  }

  function restoreSession() {
    const stored = localStorage.getItem('userInfo')
    if (stored) {
      try {
        const user = JSON.parse(stored)
        state.userInfo = user
        state.isLoggedIn = true
        state.isAdmin = user.role === 'admin'
        state.profileCompleted = !!user.profileCompleted
      } catch { /* ignore */ }
    }
  }

  function logout() {
    state.userInfo = null
    state.isLoggedIn = false
    state.isAdmin = false
    state.profileCompleted = false
    localStorage.removeItem('userInfo')
    localStorage.removeItem('token')
  }

  function updateLocal(patch) {
    if (state.userInfo) {
      Object.assign(state.userInfo, patch)
      localStorage.setItem('userInfo', JSON.stringify(state.userInfo))
    }
  }

  return {
    state: readonly(state),
    login, refreshProfile, restoreSession, logout, updateLocal
  }
}
