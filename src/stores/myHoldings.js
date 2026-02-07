import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMyHoldingsStore = defineStore('myHoldings', () => {
  // 持仓列表
  const holdings = ref([])

  // 从localStorage加载数据
  function loadFromStorage() {
    const saved = localStorage.getItem('myHoldings')
    if (saved) {
      try {
        holdings.value = JSON.parse(saved)
      } catch (e) {
        console.error('加载持仓数据失败:', e)
        holdings.value = []
      }
    }
  }

  // 保存到localStorage
  function saveToStorage() {
    localStorage.setItem('myHoldings', JSON.stringify(holdings.value))
  }

  // 添加持仓
  function addHolding(holding) {
    const newHolding = {
      id: Date.now().toString(),
      fundCode: holding.fundCode,
      fundName: holding.fundName,
      amount: parseFloat(holding.amount), // 持仓金额
      initialProfit: parseFloat(holding.initialProfit), // 初始收益
      addTime: new Date().toISOString(),
      lastUpdateTime: new Date().toISOString()
    }
    holdings.value.push(newHolding)
    saveToStorage()
    return newHolding
  }

  // 删除持仓
  function removeHolding(id) {
    const index = holdings.value.findIndex(h => h.id === id)
    if (index > -1) {
      holdings.value.splice(index, 1)
      saveToStorage()
    }
  }

  // 更新持仓收益
  function updateHoldingProfit(id, currentProfit) {
    const holding = holdings.value.find(h => h.id === id)
    if (holding) {
      holding.currentProfit = parseFloat(currentProfit)
      holding.lastUpdateTime = new Date().toISOString()
      saveToStorage()
    }
  }

  // 计算总持仓金额
  const totalAmount = computed(() => {
    return holdings.value.reduce((sum, h) => sum + (h.amount || 0), 0)
  })

  // 计算总收益
  const totalProfit = computed(() => {
    return holdings.value.reduce((sum, h) => {
      const currentProfit = h.currentProfit !== undefined ? h.currentProfit : 0
      return sum + currentProfit
    }, 0)
  })

  // 计算收益率
  const profitRate = computed(() => {
    if (totalAmount.value === 0) return 0
    return (totalProfit.value / totalAmount.value) * 100
  })

  // 初始化时加载数据
  loadFromStorage()

  return {
    holdings,
    totalAmount,
    totalProfit,
    profitRate,
    addHolding,
    removeHolding,
    updateHoldingProfit,
    loadFromStorage,
    saveToStorage
  }
})
