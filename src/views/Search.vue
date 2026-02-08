<template>
  <div class="search-page">
    <div class="header bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 sticky top-0 z-10 flex items-center">
      <button @click="router.back()" class="mr-4">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
      </button>
      <h1 class="text-xl font-bold">基金估算</h1>
    </div>

    <div class="content p-4">
      <!-- 搜索框：只有当没有路由参数时才显示 -->
      <div v-if="!route.query.fundCode" class="search-box bg-white rounded-xl p-4 shadow-md mb-6">
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

      <!-- 基金名称：从路由参数传入时显示 -->
      <div v-if="route.query.fundName" class="fund-name-card bg-white rounded-xl p-4 shadow-md mb-6">
        <h2 class="text-lg font-semibold text-gray-800">{{ route.query.fundName }}</h2>
        <p class="text-sm text-gray-500 mt-1">{{ route.query.fundCode }}</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-box bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
        <p class="text-red-600 text-sm">{{ error }}</p>
      </div>

      <!-- 查询结果 -->
      <div v-if="holdings.length > 0" class="results">
        <!-- 估算结果卡片 -->
        <div v-if="loading && !userEstimatedChange && !estimatedChange" class="result-card bg-white rounded-xl p-6 shadow-md mb-6">
          <div class="text-center">
            <p class="text-lg font-semibold text-gray-600 mb-2">查询中</p>
            <p class="text-sm text-gray-400">正在获取股票实时价格...</p>
          </div>
        </div>
        <div v-else-if="userEstimatedChange || estimatedChange" class="result-card bg-white rounded-xl p-6 shadow-md mb-6">
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
              (userEstimatedChange || estimatedChange).estimatedChangePercent >= 0
                ? 'bg-red-50'
                : 'bg-green-50'
            ]">
              <p class="text-sm text-gray-600 mb-2">估算涨跌幅</p>
              <p :class="[
                'text-4xl font-bold',
                (userEstimatedChange || estimatedChange).estimatedChangePercent >= 0
                  ? 'text-red-500'
                  : 'text-green-500'
              ]">
                {{ (userEstimatedChange || estimatedChange).estimatedChangePercent >= 0 ? '+' : '' }}{{ formatNumber((userEstimatedChange || estimatedChange).estimatedChangePercent) }}%
              </p>
              <p class="text-xs text-gray-400 mt-1">上次更新: {{ lastUpdateTime }}</p>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div class="info-item bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-500 mb-1">总资产</p>
              <p class="text-lg font-semibold text-gray-800">
                ¥{{ formatNumber((userEstimatedChange || estimatedChange).totalMarketValue + (userEstimatedChange || estimatedChange).totalChangeValue) }}
              </p>
            </div>
            <div class="info-item bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-500 mb-1">收益</p>
              <p :class="[
                'text-lg font-semibold',
                (userEstimatedChange || estimatedChange).totalChangeValue >= 0 ? 'text-red-500' : 'text-green-500'
              ]">
                {{ (userEstimatedChange || estimatedChange).totalChangeValue >= 0 ? '+' : '' }}¥{{ formatNumber((userEstimatedChange || estimatedChange).totalChangeValue) }}
              </p>
            </div>
            <div class="info-item bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-500 mb-1">收益率</p>
              <p :class="[
                'text-lg font-semibold',
                (userEstimatedChange || estimatedChange).estimatedChangePercent >= 0 ? 'text-red-500' : 'text-green-500'
              ]">
                {{ (userEstimatedChange || estimatedChange).estimatedChangePercent >= 0 ? '+' : '' }}{{ formatNumber((userEstimatedChange || estimatedChange).estimatedChangePercent) }}%
              </p>
            </div>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useFundStore } from '../stores/fund'
import { useMyHoldingsStore } from '../stores/myHoldings'
import { storeToRefs } from 'pinia'
import { useRouter, useRoute } from 'vue-router'
import { getFundValuationHistory, getFundHoldings, getStockPrices, calculateFundEstimatedChange } from '../api/jqdata'

const router = useRouter()
const fundStore = useFundStore()
const myHoldings = useMyHoldingsStore()

// 从路由参数获取基金代码和名称
const route = useRoute()
const searchCode = ref(route.query.fundCode || '')
const holdingAmount = ref(parseFloat(route.query.amount) || 0) // 用户输入的持仓金额
const autoRefresh = ref(false)
const lastUpdateTime = ref('')
const refreshInterval = ref(null)
const chartCanvas = ref(null)
const valuationHistory = ref([])
const hoverInfo = ref(null) // 鼠标悬浮信息

const { holdings, stockPrices, loading, error, estimatedChange } = storeToRefs(fundStore)

// 计算用户的预估变动金额（使用用户输入的持仓金额）
const userEstimatedChange = computed(() => {
  if (!estimatedChange.value || holdingAmount.value === 0) return null
  const changePercent = estimatedChange.value.estimatedChangePercent
  const changeAmount = holdingAmount.value * (changePercent / 100)
  return {
    estimatedChangePercent: changePercent,
    totalMarketValue: holdingAmount.value,
    totalChangeValue: changeAmount
  }
})

async function handleSearch() {
  console.log('点击查询按钮，基金代码:', searchCode.value)
  if (!searchCode.value.trim()) {
    console.log('基金代码为空，返回')
    return
  }

  // 清除旧数据
  fundStore.clearData()
  console.log('已清除旧数据')

  try {
    // 获取估值历史数据
    console.log('获取估值历史...')
    const historyData = await getFundValuationHistory(searchCode.value.trim())
    valuationHistory.value = historyData.valuationHistory || []

    console.log('获取持仓和当前估值')
    const result = await fundStore.fetchFundHoldings(searchCode.value.trim())
    console.log('查询完成，结果:', result)

    // 更新最后时间（不添加额外点，后端已返回完整走势）
    if (valuationHistory.value.length > 0) {
      const lastPoint = valuationHistory.value[valuationHistory.value.length - 1]
      lastUpdateTime.value = lastPoint.time
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

// 更新所有持仓的收益
async function updateAllProfits() {
  console.log('开始更新所有持仓收益，共', myHoldings.holdings.length, '个基金')

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

        console.log(`基金 ${holding.fundCode} 更新完成，当前收益: ${currentProfit}`)
      }
    } catch (error) {
      console.error(`更新基金 ${holding.fundCode} 收益失败:`, error)
    }
  }

  console.log('所有持仓收益更新完成')
}

function startAutoRefresh() {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }

  refreshInterval.value = setInterval(async () => {
    // 先更新所有持仓基金的收益
    await updateAllProfits()

    // 如果当前有查看的基金，也刷新当前基金的数据
    if (searchCode.value.trim()) {
      console.log('自动刷新当前查看的基金:', searchCode.value)
      await fundStore.fetchFundHoldings(searchCode.value.trim())

      // 只在交易时间内才添加新点
      const now = new Date()
      const hour = now.getHours()
      const minute = now.getMinutes()
      const isTradingTime = (
        (hour > 9 && hour < 11) ||
        (hour === 9 && minute >= 30) ||
        (hour === 11 && minute < 30) ||
        (hour >= 13 && hour < 15)
      )

      if (isTradingTime) {
        addValuationPoint()
      }

      drawChart()
    }
  }, 30000) // 改为30秒刷新一次，与Home页面保持一致
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

  // 绘制0%横线（用于区分正负值）
  const dataAreaHeight = height - padding.top - padding.bottom
  const zeroY = height - padding.bottom - ((0 - minChange) / range) * dataAreaHeight

  // 只在0%在数据范围内时绘制
  if (minChange <= 0 && maxChange >= 0) {
    ctx.strokeStyle = '#9ca3af'
    ctx.lineWidth = 1.5
    ctx.setLineDash([3, 3]) // 虚线
    ctx.beginPath()
    ctx.moveTo(padding.left, zeroY)
    ctx.lineTo(width - padding.right, zeroY)
    ctx.stroke()
    ctx.setLineDash([]) // 恢复实线
    ctx.lineWidth = 1
  }

  // 绘制走势线
  const dataAreaWidth = width - padding.left - padding.right
  const xStep = dataAreaWidth / (valuationHistory.value.length - 1)

  if (valuationHistory.value.length > 1) {
    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 1
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
  }

  // 绘制X轴时间标签（在关键时间点显示）
  ctx.fillStyle = '#9ca3af'
  ctx.textAlign = 'center'

  // 关键时间点索引：9:30(0), 10:00(30), 10:30(60), 11:00(90), 11:30(120), 13:00(121), 13:30(151), 14:00(181), 14:30(211), 15:00(241)
  const keyTimeIndices = [0, 30, 60, 90, 120, 121, 151, 181, 211]
  if (valuationHistory.value.length > 240) {
    keyTimeIndices.push(241) // 15:00
  }

  keyTimeIndices.forEach(index => {
    if (index < valuationHistory.value.length) {
      const point = valuationHistory.value[index]
      const x = padding.left + index * xStep
      ctx.fillText(point.time, x, height - 10)
    }
  })

  // 绘制悬浮竖线和提示
  if (hoverInfo.value) {
    const { x, point } = hoverInfo.value

    // 绘制竖线
    ctx.strokeStyle = '#9ca3af'
    ctx.lineWidth = 1
    ctx.setLineDash([5, 5])
    ctx.beginPath()
    ctx.moveTo(x, padding.top)
    ctx.lineTo(x, height - padding.bottom)
    ctx.stroke()
    ctx.setLineDash([])

    // 绘制数据点
    ctx.fillStyle = '#3b82f6'
    ctx.beginPath()
    ctx.arc(x, height - padding.bottom - ((point.changePercent - minChange) / range) * dataAreaHeight, 4, 0, Math.PI * 2)
    ctx.fill()

    // 绘制提示框
    const tooltipText = `${point.time}: ${point.changePercent >= 0 ? '+' : ''}${point.changePercent.toFixed(2)}%`
    ctx.font = '12px sans-serif'
    const textWidth = ctx.measureText(tooltipText).width
    const tooltipPadding = 8
    const tooltipWidth = textWidth + tooltipPadding * 2
    const tooltipHeight = 24

    let tooltipX = x + 10
    if (tooltipX + tooltipWidth > width) {
      tooltipX = x - tooltipWidth - 10
    }
    const tooltipY = padding.top + 10

    // 提示框背景
    ctx.fillStyle = 'rgba(0, 0, 0, 0.75)'
    ctx.beginPath()
    ctx.roundRect(tooltipX, tooltipY, tooltipWidth, tooltipHeight, 4)
    ctx.fill()

    // 提示框文字
    ctx.fillStyle = '#fff'
    ctx.textAlign = 'left'
    ctx.fillText(tooltipText, tooltipX + tooltipPadding, tooltipY + tooltipHeight / 2 + 4)
  }
}

// 鼠标悬浮处理
function handleChartMouseMove(e) {
  if (!chartCanvas.value || valuationHistory.value.length === 0) return

  const canvas = chartCanvas.value
  const ctx = canvas.getContext('2d')
  const rect = canvas.getBoundingClientRect()
  const mouseX = e.clientX - rect.left
  const mouseY = e.clientY - rect.top

  const width = rect.width
  const height = rect.height
  const padding = { top: 20, right: 20, bottom: 30, left: 50 }

  const dataAreaWidth = width - padding.left - padding.right
  const xStep = dataAreaWidth / (valuationHistory.value.length - 1 || 1)

  if (mouseX >= padding.left && mouseX <= width - padding.right) {
    const index = Math.round((mouseX - padding.left) / xStep)
    if (index >= 0 && index < valuationHistory.value.length) {
      const point = valuationHistory.value[index]
      hoverInfo.value = {
        x: padding.left + index * xStep,
        point: point
      }
      drawChart()
    }
  }
}

function handleChartMouseLeave() {
  hoverInfo.value = null
  if (chartCanvas.value) {
    drawChart()
  }
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

// 监听路由参数变化，当基金代码变化时自动重新查询
watch(() => route.query.fundCode, async (newFundCode, oldFundCode) => {
  if (newFundCode && newFundCode !== oldFundCode) {
    console.log('路由参数变化，旧基金:', oldFundCode, '新基金:', newFundCode)

    // 停止旧的自动刷新
    stopAutoRefresh()

    // 清除旧数据
    fundStore.clearData()
    valuationHistory.value = []
    lastUpdateTime.value = ''

    // 更新搜索代码和持仓金额
    searchCode.value = newFundCode
    holdingAmount.value = parseFloat(route.query.amount) || 0

    // 重新查询
    await handleSearch()
  }
})

onMounted(async () => {
  // 从存储加载持仓数据
  myHoldings.loadFromStorage()

  // 如果有路由参数，自动查询基金
  if (route.query.fundCode) {
    // 清除旧数据，防止显示上一个基金的脏数据
    fundStore.clearData()
    valuationHistory.value = []
    lastUpdateTime.value = ''

    searchCode.value = route.query.fundCode
    await handleSearch()
  }

  // 设置图表鼠标事件
  if (chartCanvas.value) {
    chartCanvas.value.addEventListener('mousemove', handleChartMouseMove)
    chartCanvas.value.addEventListener('mouseleave', handleChartMouseLeave)
  }
})

onUnmounted(() => {
  stopAutoRefresh()
  // 移除图表鼠标事件
  if (chartCanvas.value) {
    chartCanvas.value.removeEventListener('mousemove', handleChartMouseMove)
    chartCanvas.value.removeEventListener('mouseleave', handleChartMouseLeave)
  }
})
</script>

<style scoped>
.search-page {
  min-height: 100vh;
  background-color: #f9fafb;
  padding-bottom: 80px; /* 为底部导航留出空间 */
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
