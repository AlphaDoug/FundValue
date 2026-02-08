<template>
  <div class="settings-page">
    <div class="header bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-b-3xl shadow-lg">
      <h1 class="text-2xl font-bold mb-2">设置</h1>
      <p class="text-blue-100 text-sm">配置应用参数</p>
    </div>

    <div class="content p-4">
      <!-- 自动刷新设置 -->
      <div class="setting-card bg-white rounded-xl p-6 shadow-md mb-6">
        <h2 class="text-lg font-bold text-gray-800 mb-4">自动刷新设置</h2>

        <!-- 自动刷新开关 -->
        <div class="setting-item flex justify-between items-center mb-6">
          <div>
            <p class="font-medium text-gray-800">启用自动刷新</p>
            <p class="text-xs text-gray-500 mt-1">自动更新持仓收益数据</p>
          </div>
          <button
            @click="toggleAutoRefresh"
            :class="[
              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
              settings.autoRefresh ? 'bg-blue-500' : 'bg-gray-200'
            ]"
          >
            <span
              :class="[
                'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                settings.autoRefresh ? 'translate-x-6' : 'translate-x-1'
              ]"
            />
          </button>
        </div>

        <!-- 刷新间隔选择 -->
        <div v-if="settings.autoRefresh" class="refresh-interval">
          <p class="font-medium text-gray-800 mb-3">刷新间隔</p>
          <div class="grid grid-cols-3 gap-3">
            <button
              v-for="interval in refreshIntervals"
              :key="interval.value"
              @click="setRefreshInterval(interval.value)"
              :class="[
                'py-3 px-4 rounded-lg text-center font-medium transition-colors',
                settings.refreshInterval === interval.value
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              {{ interval.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- 当前设置信息 -->
      <div class="info-card bg-white rounded-xl p-6 shadow-md">
        <h2 class="text-lg font-bold text-gray-800 mb-4">当前设置</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-500">自动刷新</span>
            <span :class="settings.autoRefresh ? 'text-blue-500' : 'text-gray-400'">
              {{ settings.autoRefresh ? '已开启' : '已关闭' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">刷新间隔</span>
            <span class="text-gray-800">
              {{ getRefreshIntervalLabel(settings.refreshInterval) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useMyHoldingsStore } from '../stores/myHoldings'

const myHoldings = useMyHoldingsStore()

// 设置数据
const settings = ref({
  autoRefresh: true,
  refreshInterval: 30000 // 默认30秒
})

// 刷新间隔选项
const refreshIntervals = [
  { value: 10000, label: '10秒' },
  { value: 30000, label: '30秒' },
  { value: 60000, label: '60秒' }
]

// 从localStorage加载设置
function loadSettings() {
  const saved = localStorage.getItem('appSettings')
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      settings.value = {
        autoRefresh: parsed.autoRefresh ?? true,
        refreshInterval: parsed.refreshInterval ?? 30000
      }
    } catch (e) {
      console.error('加载设置失败:', e)
    }
  }
}

// 保存设置到localStorage
function saveSettings() {
  localStorage.setItem('appSettings', JSON.stringify(settings.value))
}

// 切换自动刷新
function toggleAutoRefresh() {
  settings.value.autoRefresh = !settings.value.autoRefresh
  saveSettings()
}

// 设置刷新间隔
function setRefreshInterval(interval) {
  settings.value.refreshInterval = interval
  saveSettings()
}

// 获取刷新间隔标签
function getRefreshIntervalLabel(interval) {
  const item = refreshIntervals.find(i => i.value === interval)
  return item ? item.label : '30秒'
}

// 监听设置变化，通知Home组件
watch(() => settings.value, (newSettings) => {
  // 通过自定义事件通知Home组件
  window.dispatchEvent(new CustomEvent('settings-changed', {
    detail: newSettings
  }))
}, { deep: true })

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 80px; /* 为底部导航留出空间 */
}

.setting-card,
.info-card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.setting-item {
  padding-bottom: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.setting-item:last-child {
  padding-bottom: 0;
  border-bottom: none;
}
</style>
