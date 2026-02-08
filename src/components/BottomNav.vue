<template>
  <div class="bottom-nav fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg">
    <div class="flex justify-around items-center h-16">
      <router-link
        v-for="tab in tabs"
        :key="tab.path"
        :to="tab.path"
        :class="[
          'flex flex-col items-center justify-center flex-1 h-full transition-colors',
          isActive(tab.path) ? 'text-blue-500' : 'text-gray-400 hover:text-gray-600'
        ]"
      >
        <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path v-if="tab.icon === 'home'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          <path v-else-if="tab.icon === 'settings'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path v-else-if="tab.icon === 'settings'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
        </svg>
        <span class="text-xs font-medium">{{ tab.label }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const tabs = [
  { path: '/', label: '我的持仓', icon: 'home' },
  { path: '/settings', label: '设置', icon: 'settings' }
]

function isActive(path) {
  return route.path === path
}
</script>

<style scoped>
.bottom-nav {
  z-index: 50;
}

.router-link-active {
  color: #3b82f6;
}
</style>
