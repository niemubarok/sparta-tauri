<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <q-page class="flex flex-center">
    <div class="text-center">
      <div class="text-h4 q-mb-lg">Exit Gate System</div>
      
      <div class="q-gutter-md">
        <q-btn
          color="primary"
          size="lg"
          icon="output"
          label="Exit Gate"
          @click="router.push('/exit-gate')"
        />
        
        <q-btn
          color="secondary"
          size="lg"
          icon="settings"
          label="Settings"
          @click="router.push('/settings')"
        />
        
        <q-btn
          color="purple"
          size="lg"
          icon="science"
          label="Input Test"
          @click="router.push('/input-test')"
        />
        
        <q-btn
          color="orange"
          size="lg"
          icon="bug_report"
          label="Debug Test"
          @click="router.push('/exit-gate-test')"
        />
      </div>
    </div>
  </q-page>
</template>
