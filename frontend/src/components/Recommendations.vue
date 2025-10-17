<template>
  <div>
    <h2>Recommendations</h2>
    <input v-model="userId" placeholder="User ID" />
    <input v-model.number="limit" type="number" min="1" />
    <button @click="fetchRecommendations">Get</button>

    <div v-if="loading">Loading...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <ul v-else>
      <li v-for="rec in recommendations" :key="rec.product_id">
        {{ rec.product_id }} - score: {{ rec.score }}
      </li>
    </ul>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  setup() {
    const userId = ref('1')
    const limit = ref(5)
    const recommendations = ref([])
    const loading = ref(false)
    const error = ref(null)

    async function fetchRecommendations() {
      loading.value = true
      error.value = null
      try {
        const res = await axios.get(`/api/recommendations/${userId.value}?limit=${limit.value}`)
        recommendations.value = res.data.recommendations
      } catch (e) {
        error.value = e.message
      } finally {
        loading.value = false
      }
    }

    return { userId, limit, recommendations, loading, error, fetchRecommendations }
  }
}
</script>
