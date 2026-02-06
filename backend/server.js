const express = require('express')
const cors = require('cors')
const { auth, get_price, get_fundamentals } = require('jqdatasdk')

const app = express()
const PORT = 8000

app.use(cors())
app.use(express.json())

// 聚宽认证配置
const JQ_USERNAME = '13469982083'
const JQ_PASSWORD = 'M19950729a.'

// 认证聚宽账户
function authenticateJQData() {
  return new Promise((resolve, reject) => {
    auth(JQ_USERNAME, JQ_PASSWORD, (err) => {
      if (err) {
        console.error('聚宽认证失败:', err)
        reject(err)
      } else {
        console.log('聚宽认证成功')
        resolve()
      }
    })
  })
}

// 获取基金持仓
app.get('/api/fund/holdings', async (req, res) => {
  try {
    const { fundCode } = req.query

    if (!fundCode) {
      return res.status(400).json({ error: '基金代码不能为空' })
    }

    // 这里需要调用实际的基金持仓查询API
    // 由于聚宽主要提供股票数据，基金持仓数据需要从其他渠道获取
    // 这里返回模拟数据用于演示
    const mockHoldings = [
      {
        stockCode: '000001.XSHE',
        stockName: '平安银行',
        shares: 10000,
        costPrice: 12.50
      },
      {
        stockCode: '000002.XSHE',
        stockName: '万科A',
        shares: 5000,
        costPrice: 25.80
      },
      {
        stockCode: '600000.XSHG',
        stockName: '浦发银行',
        shares: 8000,
        costPrice: 8.90
      }
    ]

    res.json({
      fundCode,
      holdings: mockHoldings
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

    // 确保已认证
    await authenticateJQData()

    // 获取最新的股票价格数据
    const prices = {}

    for (const code of codes) {
      try {
        const priceData = await new Promise((resolve, reject) => {
          get_price(code, end_date='2025-01-30 15:00:00', count=1, frequency='daily',
            fields=['open', 'close', 'high', 'low', 'volume', 'money'],
            fq='pre',
            callback=(err, data) => {
              if (err) reject(err)
              else resolve(data)
            }
          )
        })

        if (priceData && priceData.length > 0) {
          const latest = priceData.iloc[0]
          const changePercent = ((latest.close - latest.open) / latest.open) * 100

          prices[code] = {
            open: latest.open,
            close: latest.close,
            high: latest.high,
            low: latest.low,
            changePercent: changePercent
          }
        }
      } catch (error) {
        console.error(`获取股票 ${code} 价格失败:`, error)
        // 返回默认值
        prices[code] = {
          open: 10.0,
          close: 10.0,
          high: 10.0,
          low: 10.0,
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
