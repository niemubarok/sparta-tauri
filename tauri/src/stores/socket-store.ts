import { defineStore } from 'pinia'
import { ref } from 'vue'
import { io, Socket } from 'socket.io-client'
import ls from 'localstorage-slim'

export const useSocketStore = defineStore('socket', () => {
  const socket = ref<Socket | null>(null)
  const isConnected = ref(false)
  const connectionError = ref<string | null>(null)

  function initSocket() {
    const socketUrl = ls.get("WS_URL") || "http://127.0.0.1:3333"
    
    const socketOptions = {
      reconnectionAttempts: 3,
      reconnectionDelay: 1000,
      timeout: 5000,
      autoConnect: false
    }

    socket.value = io(socketUrl, socketOptions)

    socket.value.on('connect', () => {
      isConnected.value = true
      connectionError.value = null
    })

    socket.value.on('connect_error', (error) => {
      isConnected.value = false
      connectionError.value = error.message
      console.warn('Socket connection error:', error)
    })

    // Coba connect secara async
    setTimeout(() => {
      socket.value?.connect()
    }, 0)
  }

  return {
    socket,
    isConnected,
    connectionError,
    initSocket
  }
})