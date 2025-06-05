import { defineStore } from 'pinia'
import ls from 'localstorage-slim'
import { useQuasar } from 'quasar'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDark: ls.get('darkMode') || false
  }),
  
  actions: {
    toggleDarkMode() {
      this.isDark = !this.isDark
      ls.set('darkMode', this.isDark)
      document.body.classList.toggle('body--dark', this.isDark)
      
      
      
      useQuasar()?.dark.set(this.isDark)
    },
    
    initDarkMode() {
      const savedMode = ls.get('darkMode')
      if (savedMode !== null) {
        this.isDark = savedMode
        document.body.classList.toggle('body--dark', this.isDark)
        
        
        useQuasar().dark.set(this.isDark)
      }
    }
  }
})