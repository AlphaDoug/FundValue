// 聚宽数据API封装
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api' // 后端服务地址

// 根据基金代码查询最新持仓
export async function getFundHoldings(fundCode) {
  console.log('开始获取基金持仓:', fundCode)
  try {
    const response = await axios.get(`${API_BASE}/fund/holdings`, {
      params: { fundCode }
    })
    console.log('基金持仓数据:', response.data)
    return response.data
  } catch (error) {
    console.error('获取基金持仓失败:', error)
    throw error
  }
}

// 根据股票代码列表查询最新价格和涨跌幅
export async function getStockPrices(stockCodes) {
  console.log('开始获取股票价格:', stockCodes)
  try {
    const response = await axios.post(`${API_BASE}/stock/prices`, {
      codes: stockCodes
    })
    console.log('股票价格数据:', response.data)
    return response.data
  } catch (error) {
    console.error('获取股票价格失败:', error)
    throw error
  }
}

// 计算基金估算涨跌幅
export function calculateFundEstimatedChange(holdings, stockPrices) {
  let totalMarketValue = 0
  let weightedChangePercent = 0

  holdings.forEach(holding => {
    const stockPrice = stockPrices[holding.stockCode]
    if (stockPrice && holding.marketValue) {
      // 使用持仓市值和股票涨跌幅加权计算
      const marketValue = holding.marketValue
      totalMarketValue += marketValue

      // 加权平均: (持仓占比 × 股票涨跌幅)
      const weight = marketValue
      weightedChangePercent += weight * stockPrice.changePercent
    }
  })

  if (totalMarketValue === 0) return 0

  // 计算加权平均涨跌幅
  const estimatedChangePercent = weightedChangePercent / totalMarketValue
  const totalChangeValue = totalMarketValue * (estimatedChangePercent / 100)

  return {
    estimatedChangePercent: parseFloat(estimatedChangePercent.toFixed(2)),
    totalMarketValue: parseFloat(totalMarketValue.toFixed(2)),
    totalChangeValue: parseFloat(totalChangeValue.toFixed(2))
  }
}

// 获取基金估值历史走势
export async function getFundValuationHistory(fundCode) {
  console.log('开始获取基金估值历史:', fundCode)
  try {
    const response = await axios.get(`${API_BASE}/fund/valuation-history`, {
      params: { fundCode }
    })
    console.log('估值历史数据:', response.data)
    return response.data
  } catch (error) {
    console.error('获取估值历史失败:', error)
    throw error
  }
}

// 获取基金名称
export async function getFundName(fundCode) {
  console.log('开始获取基金名称:', fundCode)
  try {
    const response = await axios.get(`${API_BASE}/fund/name`, {
      params: { fundCode }
    })
    console.log('基金名称:', response.data)
    return response.data
  } catch (error) {
    console.error('获取基金名称失败:', error)
    throw error
  }
}

