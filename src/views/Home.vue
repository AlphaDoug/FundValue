<template>
  <div class="home-page">
    <div class="header bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-b-3xl shadow-lg">
      <h1 class="text-2xl font-bold mb-2">我的持仓</h1>
      <p class="text-blue-100 text-sm">实时监控基金收益</p>
    </div>

    <div class="content p-4">
      <!-- 总览卡片 -->
      <div class="summary-card bg-white rounded-2xl p-6 shadow-md mb-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-800">总资产概览</h2>
          <span class="text-xs text-gray-500">{{ lastUpdateTime }}</span>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <div class="text-center">
            <p class="text-xs text-gray-500 mb-1">总资产</p>
            <p class="text-lg font-bold text-gray-800">¥{{ formatNumber(myHoldings.totalAmount + myHoldings.totalProfit) }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs text-gray-500 mb-1">收益</p>
            <p :class="['text-lg font-bold', myHoldings.totalProfit >= 0 ? 'text-red-500' : 'text-green-500']">
              {{ myHoldings.totalProfit >= 0 ? '+' : '' }}¥{{ formatNumber(myHoldings.totalProfit) }}
            </p>
          </div>
          <div class="text-center">
            <p class="text-xs text-gray-500 mb-1">收益率</p>
            <p :class="['text-lg font-bold', myHoldings.profitRate >= 0 ? 'text-red-500' : 'text-green-500']">
              {{ myHoldings.profitRate >= 0 ? '+' : '' }}{{ formatNumber(myHoldings.profitRate) }}%
            </p>
          </div>
        </div>
      </div>

      <!-- 添加按钮 -->
      <button
        @click="showAddDialog = true"
        class="w-full mb-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl font-medium shadow-md hover:shadow-lg transition-all"
      >
        + 添加持仓基金
      </button>

      <!-- 持仓列表 -->
      <div v-if="myHoldings.holdings.length === 0" class="empty-state text-center py-12">
        <div class="text-gray-400 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
        </div>
        <p class="text-gray-500 text-sm">暂无持仓基金</p>
        <p class="text-gray-400 text-xs mt-2">点击上方按钮添加</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="holding in myHoldings.holdings"
          :key="holding.id"
          @click="viewFundDetail(holding)"
          class="holding-card bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        >
          <div class="flex justify-between items-start mb-3">
            <div>
              <h3 class="font-semibold text-gray-800">{{ holding.fundName }}</h3>
              <p class="text-xs text-gray-500 mt-1">{{ holding.fundCode }}</p>
            </div>
            <button
              @click="removeHolding(holding.id)"
              class="text-gray-400 hover:text-red-500 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>

          <div class="flex justify-between items-end">
            <div>
              <p class="text-xs text-gray-500">资产</p>
              <p class="text-lg font-bold text-gray-800">¥{{ formatNumber(holding.amount + (holding.currentProfit || holding.initialProfit || 0)) }}</p>
            </div>
            <div class="text-right">
              <p class="text-xs text-gray-500">收益</p>
              <p :class="['text-lg font-bold', (holding.currentProfit || holding.initialProfit || 0) >= 0 ? 'text-red-500' : 'text-green-500']">
                {{ (holding.currentProfit || holding.initialProfit || 0) >= 0 ? '+' : '' }}¥{{ formatNumber(holding.currentProfit || holding.initialProfit || 0) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加持仓对话框 -->
    <AddHoldingDialog
      :show="showAddDialog"
      @confirm="handleAddHolding"
      @cancel="showAddDialog = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMyHoldingsStore } from '../stores/myHoldings'
import AddHoldingDialog from '../components/AddHoldingDialog.vue'
import { getFundHoldings, getStockPrices, calculateFundEstimatedChange } from '../api/jqdata'

const router = useRouter()
const myHoldings = useMyHoldingsStore()

const showAddDialog = ref(false)
const autoRefresh = ref(true)
const refreshInterval = ref(30000) // 默认30秒
const lastUpdateTime = ref('')
let updateTimer = null

// 从localStorage加载设置
function loadSettings() {
  const saved = localStorage.getItem('appSettings')
  if (saved) {
    try {
      const settings = JSON.parse(saved)
      autoRefresh.value = settings.autoRefresh ?? true
      refreshInterval.value = settings.refreshInterval ?? 30000
    } catch (e) {
      console.error('加载设置失败:', e)
    }
  }
}

function formatNumber(num) {
  if (num === undefined || num === null) return '0.00'
  return num.toFixed(2)
}

function formatTime(date) {
  return new Date(date).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

async function handleAddHolding(formData) {
  myHoldings.addHolding(formData)
  showAddDialog.value = false
  // 立即更新一次收益
  await updateAllProfits()
}

function removeHolding(id) {
  if (confirm('确定要删除这个持仓吗？')) {
    myHoldings.removeHolding(id)
  }
}

function viewFundDetail(holding) {
  router.push({
    path: '/search',
    query: {
      fundCode: holding.fundCode,
      fundName: holding.fundName,
      amount: holding.amount,
      initialProfit: holding.initialProfit || 0
    }
  })
}

// 应用自动刷新设置
function applyAutoRefreshSettings() {
  // 清除现有定时器
  if (updateTimer) {
    clearInterval(updateTimer)
    updateTimer = null
  }

  if (autoRefresh.value) {
    // 开启自动刷新
    updateAllProfits()
    updateTimer = setInterval(() => {
      if (myHoldings.holdings.length > 0) {
        updateAllProfits()
      }
    }, refreshInterval.value)
  }
}

// 设置变化处理函数
const handleSettingsChanged = (event) => {
  const newSettings = event.detail
  autoRefresh.value = newSettings.autoRefresh
  refreshInterval.value = newSettings.refreshInterval
  applyAutoRefreshSettings()
}

// 更新所有持仓的收益
async function updateAllProfits() {
  lastUpdateTime.value = formatTime(new Date())

  for (const holding of myHoldings.holdings) {
    try {
      // 获取基金的持仓信息
      const data = await getFundHoldings(holding.fundCode)
      const fundHoldings = data.holdings || []

      if (fundHoldings.length > 0) {
        // 获取股票价格
        const stockCodes = fundHoldings.map(h => h.stockCode)
        const pricesData = await getStockPrices(stockCodes)

        // 计算基金估算涨跌幅
        const estimatedChange = calculateFundEstimatedChange(fundHoldings, pricesData)

        // 计算当前收益 = 持仓金额 × (估算涨跌幅 / 100)
        const currentProfit = holding.amount * (estimatedChange.estimatedChangePercent / 100)

        // 更新持仓收益
        myHoldings.updateHoldingProfit(holding.id, currentProfit)
      }
    } catch (error) {
      console.error(`更新基金 ${holding.fundCode} 收益失败:`, error)
    }
  }
}

onMounted(() => {
  // 加载设置
  loadSettings()

  // 从存储加载数据
  myHoldings.loadFromStorage()

  // 立即更新一次
  if (myHoldings.holdings.length > 0) {
    updateAllProfits()
  }

  // 应用自动刷新设置
  applyAutoRefreshSettings()

  // 监听设置变化
  window.addEventListener('settings-changed', handleSettingsChanged)
})

onUnmounted(() => {
  // 清除定时器
  if (updateTimer) {
    clearInterval(updateTimer)
    updateTimer = null
  }

  // 移除设置变化监听
  window.removeEventListener('settings-changed', handleSettingsChanged)
})
</script>

<style scoped>
.home-page {
  width: 100%;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 80px; /* 为底部导航留出空间 */
}

.holding-card:active {
  transform: scale(0.98);
}
</style>


