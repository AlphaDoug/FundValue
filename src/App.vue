<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <router-view />
    <BottomNav />
  </div>
</template>

<script setup>
import BottomNav from './components/BottomNav.vue'
</script>

<style scoped>
</style>
