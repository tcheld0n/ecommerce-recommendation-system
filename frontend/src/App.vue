<template>
  <div>
    <h1>Ecommerce Recommender</h1>
    <HealthCheck />
    <Recommendations />
  </div>
</template>

<script>
import HealthCheck from './components/HealthCheck.vue'
import Recommendations from './components/Recommendations.vue'

export default {
  components: { HealthCheck, Recommendations }
}
</script>
