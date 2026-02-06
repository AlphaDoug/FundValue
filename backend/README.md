# 基金数据后端服务

## 说明
本服务提供基金持仓查询和股票价格查询API，支持两种运行方式：
1. Node.js版（使用东方财富网API）
2. Python版（使用AkShare库，推荐）

## 方式一：Node.js版（简单版）

### 安装依赖
```bash
cd backend
npm install express cors axios
```

### 启动服务
```bash
node start.js
```

服务将在 http://localhost:8000 运行

## 方式二：Python版（推荐，数据更完整）

### 安装Python依赖
```bash
pip install akshare flask flask-cors
```

### 启动服务
```bash
cd backend
python fund_api.py
```

服务将在 http://localhost:8000 运行

## API接口

### 1. 获取基金持仓
```
GET /api/fund/holdings?fundCode=000001
```

响应示例：
```json
{
  "fundCode": "000001",
  "holdings": [
    {
      "stockCode": "000001.XSHE",
      "stockName": "平安银行",
      "shares": 10000,
      "costPrice": 12.50
    }
  ]
}
```

### 2. 获取股票价格
```
POST /api/stock/prices
Content-Type: application/json

{
  "codes": ["000001.XSHE", "000002.XSHE"]
}
```

响应示例：
```json
{
  "000001.XSHE": {
    "open": 12.50,
    "close": 12.80,
    "high": 12.90,
    "low": 12.40,
    "preClose": 12.40,
    "changePercent": 2.40
  }
}
```

### 3. 健康检查
```
GET /api/health
```

## 数据源说明

### AkShare（Python版）
- 基金持仓：使用东方财富网数据
- 股票价格：使用东方财富网实时行情
- 数据更完整，更新更及时
- 支持更多功能（历史数据、财务数据等）

### 东方财富API（Node.js版）
- 直接调用东方财富网公开API
- 响应速度快
- 适合快速开发测试

## 前端配置

前端已配置好API地址：`http://localhost:8000/api`

## 测试

使用curl测试API：
```bash
# 测试健康检查
curl http://localhost:8000/api/health

# 测试基金持仓
curl "http://localhost:8000/api/fund/holdings?fundCode=000001"

# 测试股票价格
curl -X POST http://localhost:8000/api/stock/prices \
  -H "Content-Type: application/json" \
  -d '{"codes": ["000001.XSHE", "000002.XSHE"]}'
```

## 注意事项

1. **交易时间限制**：股票价格数据仅在交易时间内实时更新
2. **缓存策略**：建议对频繁查询的数据进行缓存
3. **频率限制**：避免过于频繁的请求，以免被限流
4. **错误处理**：前端应妥善处理API错误情况

## AkShare常用函数

### 基金相关
```python
# 获取基金持仓
ak.fund_portfolio_hold_em(fund="000001", date="20241231", symbol="股票持仓")

# 获取基金基本信息
ak.fund_em_info(fund="000001")

# 获取基金净值
ak.fund_etf_hist_sina(symbol="sh510300")
```

### 股票相关
```python
# 获取A股实时行情
ak.stock_zh_a_spot_em()

# 获取股票历史数据
ak.stock_zh_a_hist(symbol="000001", period="daily")

# 获取股票基本信息
ak.stock_individual_info_em(symbol="000001")
```

更多信息请参考：https://akshare.akfamily.xyz/
