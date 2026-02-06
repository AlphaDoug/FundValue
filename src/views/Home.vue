<template>
  <div class="home-page">
    <div class="header bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-b-3xl shadow-lg">
      <h1 class="text-2xl font-bold mb-2">基金价值查询</h1>
      <p class="text-blue-100 text-sm">实时查询基金净值与收益</p>
    </div>

    <div class="content p-4">
      <div class="welcome-card bg-white rounded-2xl p-6 shadow-md mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-3">欢迎使用</h2>
        <p class="text-gray-600 text-sm leading-relaxed">
          这是一个移动端基金价值查询应用，您可以实时查看基金净值、收益率等信息。
        </p>
      </div>

      <div class="feature-grid grid grid-cols-2 gap-4">
        <div class="feature-card bg-white rounded-xl p-4 shadow-md text-center" @click="goToSearch">
          <div class="icon bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
            <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <h3 class="text-sm font-medium text-gray-800">基金估算</h3>
        </div>

        <div class="feature-card bg-white rounded-xl p-4 shadow-md text-center">
          <div class="icon bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
            <svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <h3 class="text-sm font-medium text-gray-800">实时数据</h3>
        </div>

        <div class="feature-card bg-white rounded-xl p-4 shadow-md text-center">
          <div class="icon bg-orange-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
            <svg class="w-6 h-6 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <h3 class="text-sm font-medium text-gray-800">历史记录</h3>
        </div>

        <div class="feature-card bg-white rounded-xl p-4 shadow-md text-center">
          <div class="icon bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
            <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
          </div>
          <h3 class="text-sm font-medium text-gray-800">持仓管理</h3>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goToSearch() {
  router.push('/search')
}
</script>

<style scoped>
.home-page {
  width: 100%;
  min-height: 100vh;
}
</style>
