const express = require('express')
const cors = require('cors')
const axios = require('axios')
const { exec } = require('child_process')
const { promisify } = require('util')

const execAsync = promisify(exec)

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

    console.log(`查询基金持仓: ${fundCode}`)

    // 调用Python脚本获取持仓数据
    const scriptPath = path.join(__dirname, 'get_holdings.py')
    const { stdout, stderr } = await execAsync(`python "${scriptPath}" ${fundCode}`, {
      encoding: 'utf8',
      cwd: __dirname,
      shell: true
    })

    if (stderr) {
      console.error('Python脚本执行错误:', stderr)
    }

    const result = JSON.parse(stdout)

    if (!result.success) {
      throw new Error(result.error || '获取持仓数据失败')
    }

    console.log(`成功获取 ${result.holdings.length} 条持仓`)
    res.json({
      fundCode,
      holdings: result.holdings
    })
  } catch (error) {
    console.error('获取基金持仓失败:', error)
    res.status(500).json({ error: '获取基金持仓失败', details: error.message })
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

        console.log(`查询股票 ${code}, secid=${secid}`)

        const response = await axios.get(AKSHARE_API.stockQuote, {
          params: {
            secid: secid,
            fields: 'f43,f44,f45,f46,f47,f48,f60,f107,f116,f117,f162,f170,f169,f168,f51,f52',
            ut: 'fa5fd1943c7b386f172d6893dbfba10b'
          },
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/'
          },
          timeout: 5000
        })

        console.log(`股票 ${code} API响应:`, JSON.stringify(response.data))

        if (response.data && response.data.data) {
          const quote = response.data.data

          // 提取价格数据（东方财富API返回的价格需要除以100）
          const open = quote.f46 ? quote.f46 / 100 : 0  // 开盘价
          const close = quote.f43 ? quote.f43 / 100 : 0 // 最新价
          const high = quote.f44 ? quote.f44 / 100 : 0  // 最高价
          const low = quote.f45 ? quote.f45 / 100 : 0   // 最低价
          const preClose = quote.f60 ? quote.f60 / 100 : 0 // 昨收价
          const changePercent = quote.f170 ? quote.f170 / 100 : 0  // 涨跌幅
          const change = quote.f169 ? quote.f169 / 100 : 0  // 涨跌额

          prices[code] = {
            open,
            close,
            high,
            low,
            preClose,
            changePercent,
            change
          }
        } else {
          // API返回为空时，返回默认值并记录日志
          console.warn(`股票 ${code} API返回为空`)
          prices[code] = {
            open: 0,
            close: 0,
            high: 0,
            low: 0,
            preClose: 0,
            changePercent: 0,
            change: 0
          }
        }
      } catch (error) {
        console.error(`获取股票 ${code} 价格失败:`, error.message)
        // 返回默认值
        prices[code] = {
          open: 0,
          close: 0,
          high: 0,
          low: 0,
          preClose: 0,
          changePercent: 0,
          change: 0
        }
      }
    }

    res.json(prices)
  } catch (error) {
    console.error('获取股票价格失败:', error)
    res.status(500).json({ error: '获取股票价格失败', details: error.message })
  }
})

// 获取基金估值历史（基于持仓股票计算）
app.get('/api/fund/valuation-history', async (req, res) => {
  try {
    const { fundCode } = req.query

    if (!fundCode) {
      return res.status(400).json({ error: '基金代码不能为空' })
    }

    // 先获取基金持仓数据
    const holdingsResponse = await axios.get(`http://localhost:${PORT}/api/fund/holdings`, {
      params: { fundCode }
    })

    const fundHoldings = holdingsResponse.data.holdings || []

    if (fundHoldings.length === 0) {
      return res.json({
        fundCode,
        currentChangePercent: 0,
        valuationHistory: []
      })
    }

    // 获取持仓股票的价格数据
    const stockCodes = fundHoldings.map(h => h.stockCode)
    const pricesResponse = await axios.post(`http://localhost:${PORT}/api/stock/prices`, {
      codes: stockCodes
    })

    const stockPrices = pricesResponse.data || {}

    // 计算基金的估算涨跌幅（使用加权平均）
    let totalMarketValue = 0
    let weightedChangePercent = 0

    fundHoldings.forEach(holding => {
      const stockPrice = stockPrices[holding.stockCode]
      if (stockPrice && holding.marketValue) {
        const marketValue = holding.marketValue
        totalMarketValue += marketValue
        weightedChangePercent += marketValue * stockPrice.changePercent
      }
    })

    const currentChangePercent = totalMarketValue > 0 ? weightedChangePercent / totalMarketValue : 0

    // 返回当前估算值，不生成历史曲线
    // 历史曲线需要调用专门的分钟级股票数据接口
    res.json({
      fundCode,
      currentChangePercent: parseFloat(currentChangePercent.toFixed(2)),
      valuationHistory: []
    })
  } catch (error) {
    console.error('获取基金估值历史失败:', error)
    // 返回空的历史数据而不是500错误，让前端能够继续运行
    res.json({
      fundCode: req.query.fundCode,
      currentChangePercent: 0,
      valuationHistory: []
    })
  }
})

// 获取基金名称
app.get('/api/fund/name', async (req, res) => {
  try {
    const { fundCode } = req.query

    if (!fundCode) {
      return res.status(400).json({ error: '基金代码不能为空' })
    }

    // 使用东方财富网的基金API获取基金信息
    const response = await axios.get(`https://fund.eastmoney.com/${fundCode}.html`, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    })

    // 解析HTML页面获取基金名称
    const html = response.data

    // 使用正则表达式提取基金名称
    // 优先从title标签中提取（更可靠）
    const titleRegex = /<title>(.*?)<\/title>/
    const titleMatch = html.match(titleRegex)

    let fundName = ''

    if (titleMatch && titleMatch[1]) {
      const titleText = titleMatch[1]
      // 提取基金名称（去掉括号后的内容）
      // title格式: "华夏成长混合(000001)基金净值_估值_行情走势—天天基金网"
      fundName = titleText.split('(')[0].split('（')[0].trim()

      // 验证名称是否有效（不为空且不是"基金品种"）
      if (!fundName || fundName === '基金品种' || fundName.length < 2) {
        fundName = ''
      }
    }

    // 如果title提取失败，尝试从h1标签提取（但跳过包含"基金品种"的内容）
    if (!fundName) {
      const h1Regex = /<h1[^>]*>(.*?)<\/h1>/gi
      let h1Match
      while ((h1Match = h1Regex.exec(html)) !== null) {
        const h1Text = h1Match[1].replace(/<[^>]*>/g, '').trim()
        // 跳过包含"基金品种"的h1标签（广告文字）
        if (h1Text && !h1Text.includes('基金品种') && h1Text.length >= 2) {
          fundName = h1Text
          break
        }
      }
    }

    // 如果还是无法获取，尝试从meta标签提取
    if (!fundName) {
      const keywordsRegex = /<meta[^>]*name="keywords"[^>]*content="([^"]+)"/i
      const keywordsMatch = html.match(keywordsRegex)
      if (keywordsMatch && keywordsMatch[1]) {
        // keywords格式: "华夏成长混合,000001,华夏成长混合净值,华夏成长混合估值"
        const keywords = keywordsMatch[1].split(',')[0].trim()
        if (keywords && keywords.length >= 2) {
          fundName = keywords
        }
      }
    }

    // 如果所有方法都失败，返回基金代码
    if (!fundName) {
      fundName = fundCode
    }

    res.json({
      fundCode,
      fundName
    })
  } catch (error) {
    console.error('获取基金名称失败:', error)
    // 发生错误时，返回基金代码作为名称
    res.json({
      fundCode,
      fundName: fundCode
    })
  }
})

// 健康检查
app.get('/api/health', (_, res) => {
  res.json({ status: 'ok' })
})

app.listen(PORT, () => {
  console.log(`后端服务运行在 http://localhost:${PORT}`)
})
