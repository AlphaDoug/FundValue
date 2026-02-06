const express = require('express')
const cors = require('cors')
const axios = require('axios')

const app = express()
const PORT = 8000

app.use(cors())
app.use(express.json())

// 东方财富网API接口
const AKSHARE_API = {
  // 基金持仓接口
  fundHoldings: 'https://fund.eastmoney.com/000001.html',
  // 股票实时行情接口
  stockQuote: 'http://push2.eastmoney.com/api/qt/stock/get',
  // 基金实时净值接口
  fundQuote: 'http://fundgz.eastmoney.com/js/000001.js'
}

// 获取基金持仓
app.get('/api/fund/holdings', async (req, res) => {
  try {
    const { fundCode } = req.query

    if (!fundCode) {
      return res.status(400).json({ error: '基金代码不能为空' })
    }

    // 使用东方财富网的基金持仓API
    const response = await axios.get(`https://fund.eastmoney.com/${fundCode}.html`, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    })

    // 解析HTML页面获取持仓数据（这里使用模拟数据）
    // 实际生产环境需要使用Python的AkShare库或cheerio解析HTML
    const mockHoldings = {
      '000001': [
        { stockCode: '000001.XSHE', stockName: '平安银行', shares: 10000, costPrice: 12.50 },
        { stockCode: '000002.XSHE', stockName: '万科A', shares: 5000, costPrice: 25.80 },
        { stockCode: '600000.XSHG', stockName: '浦发银行', shares: 8000, costPrice: 8.90 }
      ],
      '000002': [
        { stockCode: '600036.XSHG', stockName: '招商银行', shares: 15000, costPrice: 35.20 },
        { stockCode: '000858.XSHE', stockName: '五粮液', shares: 3000, costPrice: 180.50 }
      ]
    }

    const holdings = mockHoldings[fundCode] || []

    res.json({
      fundCode,
      holdings
    })
  } catch (error) {
    console.error('获取基金持仓失败:', error)
    res.status(500).json({ error: '获取基金持仓失败' })
  }
})

// 获取股票价格
app.post('/api/stock/prices', async (req, res) => {
  try {
    const { codes } = req.body

    if (!codes || !Array.isArray(codes) || codes.length === 0) {
      return res.status(400).json({ error: '股票代码列表不能为空' })
    }

    // 使用东方财富网的实时行情API
    const prices = {}

    for (const code of codes) {
      try {
        // 解析股票代码（去除.XSHG或.XSHE后缀）
        const stockCode = code.replace('.XSHG', '').replace('.XSHE', '')

        // 判断市场（上海或深圳）
        const market = code.includes('XSHG') ? '1' : '0'
        const secid = `${market}.${stockCode}`

        const response = await axios.get(AKSHARE_API.stockQuote, {
          params: {
            secid: secid,
            fields: 'f43,f44,f45,f46,f47,f48,f60,f107,f116,f117,f162',
            ut: 'fa5fd1943c7b386f172d6893dbfba10b'
          },
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/'
          }
        })

        if (response.data && response.data.data) {
          const stockData = response.data.data
          const quote = stockData?.quote || {}

          // 提取价格数据
          const open = quote.f46 || 0  // 开盘价
          const close = quote.f43 || 0 // 最新价
          const high = quote.f44 || 0  // 最高价
          const low = quote.f45 || 0   // 最低价
          const preClose = quote.f60 || 0 // 昨收价

          // 计算涨跌幅
          const changePercent = preClose > 0 ? ((close - preClose) / preClose) * 100 : 0

          prices[code] = {
            open,
            close,
            high,
            low,
            preClose,
            changePercent
          }
        } else {
          // 使用模拟数据
          prices[code] = {
            open: 10.0,
            close: 10.0,
            high: 10.0,
            low: 10.0,
            preClose: 10.0,
            changePercent: 0
          }
        }
      } catch (error) {
        console.error(`获取股票 ${code} 价格失败:`, error.message)
        // 返回默认值
        prices[code] = {
          open: 10.0,
          close: 10.0,
          high: 10.0,
          low: 10.0,
          preClose: 10.0,
          changePercent: 0
        }
      }
    }

    res.json(prices)
  } catch (error) {
    console.error('获取股票价格失败:', error)
    res.status(500).json({ error: '获取股票价格失败' })
  }
})

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' })
})

app.listen(PORT, () => {
  console.log(`后端服务运行在 http://localhost:${PORT}`)
})
