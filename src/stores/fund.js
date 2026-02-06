import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getFundHoldings, getStockPrices, calculateFundEstimatedChange } from '../api/jqdata'

export const useFundStore = defineStore('fund', () => {
  // 状态
  const fundCode = ref('')
  const holdings = ref([])
  const stockPrices = ref({})
  const loading = ref(false)
  const error = ref(null)

  // 计算属性
  const estimatedChange = computed(() => {
    if (holdings.value.length === 0 || Object.keys(stockPrices.value).length === 0) {
      return null
    }
    return calculateFundEstimatedChange(holdings.value, stockPrices.value)
  })

  // 方法
  async function fetchFundHoldings(code) {
    loading.value = true
    error.value = null
    fundCode.value = code

    try {
      console.log('fetchFundHoldings 开始, code:', code)
      const data = await getFundHoldings(code)
      console.log('获取到持仓数据:', data)
      holdings.value = data.holdings || []
      console.log('设置持仓后, holdings.value:', holdings.value)

      // 获取持仓股票的代码列表
      const stockCodes = holdings.value.map(h => h.stockCode)
      console.log('股票代码列表:', stockCodes)

      if (stockCodes.length > 0) {
        const pricesData = await getStockPrices(stockCodes)
        console.log('获取到价格数据:', pricesData)
        stockPrices.value = pricesData || {}
        console.log('设置价格后, stockPrices.value:', stockPrices.value)
      }

      console.log('estimatedChange.value:', estimatedChange.value)
      return estimatedChange.value
    } catch (err) {
      console.error('fetchFundHoldings 错误:', err)
      error.value = err.message || '获取数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearData() {
    fundCode.value = ''
    holdings.value = []
    stockPrices.value = {}
    error.value = null
  }

  return {
    fundCode,
    holdings,
    stockPrices,
    loading,
    error,
    estimatedChange,
    fetchFundHoldings,
    clearData
  }
})
