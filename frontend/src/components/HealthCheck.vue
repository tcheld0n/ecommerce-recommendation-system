<template>
  <div>
    <h2>Health</h2>
    <div v-if="loading">Checking...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <div v-else>Service: {{ status }}</div>
    <button @click="check">Re-check</button>
  </div>
</template>

<script>
import axios from 'axios'
import { ref } from 'vue'

export default {
  setup() {
    const loading = ref(false)
    const status = ref('unknown')
    const error = ref(null)

    async function check() {
      loading.value = true
      error.value = null
      try {
        const res = await axios.get('/health')
        status.value = res.data.status
      } catch (e) {
        error.value = e.message
      } finally {
        loading.value = false
      }
    }

    check()

    return { loading, status, error, check }
  }
}
</script>
