<template>
  <div class="search-page">
    <div class="header bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 sticky top-0 z-10">
      <h1 class="text-xl font-bold">基金估算</h1>
    </div>

    <div class="content p-4">
      <!-- 搜索框 -->
      <div class="search-box bg-white rounded-xl p-4 shadow-md mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">输入基金代码</label>
        <div class="flex gap-2">
          <input
            v-model="searchCode"
            type="text"
            placeholder="例如: 000001"
            class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @keyup.enter="handleSearch"
          />
          <button
            @click="handleSearch"
            :disabled="loading || !searchCode"
            class="px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? '查询中...' : '查询' }}
          </button>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-box bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
        <p class="text-red-600 text-sm">{{ error }}</p>
      </div>

      <!-- 查询结果 -->
      <div v-if="holdings.length > 0" class="results">
        <!-- 估算结果卡片 -->
        <div v-if="estimatedChange" class="result-card bg-white rounded-xl p-6 shadow-md mb-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-bold text-gray-800">估算结果</h2>
            <div class="text-xs text-gray-500">
              {{ autoRefresh ? '自动刷新中' : '已暂停' }}
              <button @click="toggleAutoRefresh" class="ml-2 px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs hover:bg-blue-200">
                {{ autoRefresh ? '停止' : '开启' }}
              </button>
            </div>
          </div>

          <!-- 估值走势图 -->
          <div class="chart-container mb-6">
            <canvas ref="chartCanvas" class="w-full h-48"></canvas>
          </div>

          <div class="flex items-center justify-center mb-6">
            <div :class="[
              'text-center p-6 rounded-2xl',
              estimatedChange.estimatedChangePercent >= 0
                ? 'bg-red-50'
                : 'bg-green-50'
            ]">
              <p class="text-sm text-gray-600 mb-2">估算涨跌幅</p>
              <p :class="[
                'text-4xl font-bold',
                estimatedChange.estimatedChangePercent >= 0
                  ? 'text-red-500'
                  : 'text-green-500'
              ]">
                {{ estimatedChange.estimatedChangePercent >= 0 ? '+' : '' }}{{ estimatedChange.estimatedChangePercent }}%
              </p>
              <p class="text-xs text-gray-400 mt-1">上次更新: {{ lastUpdateTime }}</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="info-item bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-500 mb-1">持仓总市值</p>
              <p class="text-lg font-semibold text-gray-800">
                ¥{{ formatNumber(estimatedChange.totalMarketValue) }}
              </p>
            </div>
            <div class="info-item bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-500 mb-1">预估变动额</p>
              <p :class="[
                'text-lg font-semibold',
                estimatedChange.totalChangeValue >= 0 ? 'text-red-500' : 'text-green-500'
              ]">
                {{ estimatedChange.totalChangeValue >= 0 ? '+' : '' }}¥{{ formatNumber(estimatedChange.totalChangeValue) }}
              </p>
            </div>
          </div>
        </div>

        <!-- 加载提示 -->
        <div v-else-if="loading" class="result-card bg-white rounded-xl p-6 shadow-md mb-6">
          <div class="text-center text-gray-500">
            <p>正在获取股票实时价格...</p>
          </div>
        </div>

        <!-- 无法获取价格提示 -->
        <div v-else class="result-card bg-white rounded-xl p-6 shadow-md mb-6">
          <div class="text-center text-gray-500">
            <p>暂无法获取股票实时价格，显示持仓明细</p>
          </div>
        </div>

        <!-- 持仓明细 -->
        <div class="holdings-card bg-white rounded-xl p-6 shadow-md">
          <h3 class="text-lg font-bold text-gray-800 mb-4">持仓明细</h3>

          <!-- 表头 -->
          <div class="grid grid-cols-4 gap-2 text-xs text-gray-500 mb-3 px-3">
            <div class="font-medium">股票名称</div>
            <div class="font-medium text-right">当前涨幅</div>
            <div class="font-medium text-right">持仓占比</div>
            <div class="font-medium text-right">较上期</div>
          </div>

          <!-- 持仓列表 -->
          <div v-if="holdings.length > 0" class="holdings-list space-y-2">
            <div
              v-for="holding in holdings"
              :key="holding.stockCode"
              class="holding-item grid grid-cols-4 gap-2 items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
            >
              <!-- 股票名称和代码 -->
              <div class="flex-1">
                <div class="flex items-center gap-1">
                  <p class="font-medium text-gray-800 text-sm">{{ holding.stockName }}</p>
                  <span v-if="holding.isNew" class="inline-block px-1.5 py-0.5 text-xs font-medium bg-blue-100 text-blue-600 rounded">新增</span>
                </div>
                <p class="text-xs text-gray-400">{{ holding.stockCode }}</p>
              </div>

              <!-- 当前涨幅 -->
              <div class="text-right">
                <p :class="[
                  'font-semibold text-sm',
                  getStockChangePercent(holding.stockCode) >= 0 ? 'text-red-500' : 'text-green-500'
                ]">
                  {{ getStockChangePercent(holding.stockCode) >= 0 ? '+' : '' }}{{ getStockChangePercent(holding.stockCode) }}%
                </p>
              </div>

              <!-- 持仓占比 -->
              <div class="text-right">
                <p class="font-semibold text-gray-800 text-sm">{{ holding.holdPercent || '-' }}%</p>
              </div>

              <!-- 较上期占比变化 -->
              <div class="text-right">
                <div v-if="holding.isNew" class="inline-flex items-center justify-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-600">
                  新增
                </div>
                <div v-else-if="holding.holdPercentChange !== undefined" :class="[
                  'inline-flex items-center justify-center px-2 py-1 rounded text-xs font-medium',
                  holding.holdPercentChange > 0
                    ? 'bg-red-100 text-red-600'
                    : holding.holdPercentChange < 0
                      ? 'bg-green-100 text-green-600'
                      : 'bg-gray-100 text-gray-600'
                ]">
                  <svg
                    v-if="holding.holdPercentChange > 0"
                    class="w-3 h-3 mr-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
                  </svg>
                  <svg
                    v-else-if="holding.holdPercentChange < 0"
                    class="w-3 h-3 mr-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                  </svg>
                  <span v-else class="mr-2">-</span>
                  {{ holding.holdPercentChange !== 0 ? Math.abs(holding.holdPercentChange).toFixed(2) + '%' : '-' }}
                </div>
                <div v-else class="inline-flex items-center justify-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-600">
                  -
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-500">
            暂无持仓数据
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useFundStore } from '../stores/fund'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { getFundValuationHistory } from '../api/jqdata'

const router = useRouter()
const fundStore = useFundStore()

const searchCode = ref('')
const autoRefresh = ref(false)
const lastUpdateTime = ref('')
const refreshInterval = ref(null)
const chartCanvas = ref(null)
const valuationHistory = ref([])

const { holdings, stockPrices, loading, error, estimatedChange } = storeToRefs(fundStore)

async function handleSearch() {
  console.log('点击查询按钮，基金代码:', searchCode.value)
  if (!searchCode.value.trim()) {
    console.log('基金代码为空，返回')
    return
  }

  try {
    // 获取估值历史数据
    console.log('获取估值历史...')
    const historyData = await getFundValuationHistory(searchCode.value.trim())
    valuationHistory.value = historyData.valuationHistory || []

    console.log('获取持仓和当前估值')
    const result = await fundStore.fetchFundHoldings(searchCode.value.trim())
    console.log('查询完成，结果:', result)

    // 添加当前估值点
    if (result && estimatedChange.value) {
      const now = new Date()
      const timeStr = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      valuationHistory.value.push({
        time: timeStr,
        changePercent: estimatedChange.value.estimatedChangePercent
      })
      lastUpdateTime.value = timeStr
    }

    // 自动开启刷新
    autoRefresh.value = true
    startAutoRefresh()

    // 绘制图表
    drawChart()
  } catch (err) {
    console.error('查询失败:', err)
  }
}

function addValuationPoint() {
  if (!estimatedChange.value) return

  const now = new Date()
  const timeStr = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  valuationHistory.value.push({
    time: timeStr,
    changePercent: estimatedChange.value.estimatedChangePercent
  })

  // 保留最近120个数据点（2小时）
  if (valuationHistory.value.length > 120) {
    valuationHistory.value.shift()
  }

  lastUpdateTime.value = timeStr
}

function startAutoRefresh() {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }

  refreshInterval.value = setInterval(async () => {
    if (searchCode.value.trim()) {
      console.log('自动刷新:', searchCode.value)
      await fundStore.fetchFundHoldings(searchCode.value.trim())
      addValuationPoint()
      drawChart()
    }
  }, 60000) // 1分钟刷新一次
}

function stopAutoRefresh() {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

function toggleAutoRefresh() {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

function drawChart() {
  if (!chartCanvas.value || valuationHistory.value.length === 0) return

  const canvas = chartCanvas.value
  const ctx = canvas.getContext('2d')

  // 设置canvas尺寸
  const rect = canvas.getBoundingClientRect()
  canvas.width = rect.width * 2
  canvas.height = rect.height * 2
  ctx.scale(2, 2)

  const width = rect.width
  const height = rect.height
  const padding = { top: 20, right: 20, bottom: 30, left: 50 }

  // 清空画布
  ctx.clearRect(0, 0, width, height)

  // 计算数据范围
  const changes = valuationHistory.value.map(v => v.changePercent)
  const minChange = Math.min(...changes)
  const maxChange = Math.max(...changes)
  const range = maxChange - minChange || 1

  // 绘制坐标轴
  ctx.strokeStyle = '#e5e7eb'
  ctx.lineWidth = 1

  // Y轴
  ctx.beginPath()
  ctx.moveTo(padding.left, padding.top)
  ctx.lineTo(padding.left, height - padding.bottom)
  ctx.stroke()

  // X轴
  ctx.beginPath()
  ctx.moveTo(padding.left, height - padding.bottom)
  ctx.lineTo(width - padding.right, height - padding.bottom)
  ctx.stroke()

  // 绘制Y轴刻度
  ctx.fillStyle = '#9ca3af'
  ctx.font = '10px sans-serif'
  ctx.textAlign = 'right'

  for (let i = 0; i <= 4; i++) {
    const value = minChange + (range * i) / 4
    const y = height - padding.bottom - ((value - minChange) / range) * (height - padding.top - padding.bottom)

    // 刻度线
    ctx.strokeStyle = '#f3f4f6'
    ctx.beginPath()
    ctx.moveTo(padding.left, y)
    ctx.lineTo(width - padding.right, y)
    ctx.stroke()

    // 刻度值
    ctx.fillText(value.toFixed(2) + '%', padding.left - 5, y + 3)
  }

  // 绘制走势线
  if (valuationHistory.value.length > 1) {
    const dataAreaWidth = width - padding.left - padding.right
    const dataAreaHeight = height - padding.top - padding.bottom
    const xStep = dataAreaWidth / (valuationHistory.value.length - 1)

    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 2
    ctx.beginPath()

    valuationHistory.value.forEach((point, index) => {
      const x = padding.left + index * xStep
      const y = height - padding.bottom - ((point.changePercent - minChange) / range) * dataAreaHeight

      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // 绘制数据点
    valuationHistory.value.forEach((point, index) => {
      const x = padding.left + index * xStep
      const y = height - padding.bottom - ((point.changePercent - minChange) / range) * dataAreaHeight

      ctx.fillStyle = '#3b82f6'
      ctx.beginPath()
      ctx.arc(x, y, 3, 0, Math.PI * 2)
      ctx.fill()
    })
  }

  // 绘制X轴时间标签（每隔15分钟显示一次）
  ctx.fillStyle = '#9ca3af'
  ctx.textAlign = 'center'

  const dataAreaWidth = width - padding.left - padding.right
  const xStep = dataAreaWidth / (valuationHistory.value.length - 1 || 1)

  valuationHistory.value.forEach((point, index) => {
    if (index % 15 === 0 || index === valuationHistory.value.length - 1) {
      const x = padding.left + index * xStep
      ctx.fillText(point.time, x, height - 10)
    }
  })
}

function getStockChangePercent(stockCode) {
  const price = stockPrices.value[stockCode]
  return price ? price.changePercent.toFixed(2) : '0.00'
}

function getHoldPercentChange(holding) {
  // 暂时返回0，因为AkShare API不提供上期持仓占比数据
  // 如需此功能，需要额外获取历史持仓数据
  return 0
}

function formatNumber(num) {
  return Number(num).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.search-page {
  min-height: 100vh;
  background-color: #f9fafb;
}

.chart-container {
  position: relative;
  background: #f9fafb;
  border-radius: 8px;
  padding: 10px;
}

canvas {
  display: block;
}
</style>
