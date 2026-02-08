# 基金价值估算系统

## 项目说明
这是一个移动端基金价值查询应用，可以根据基金持仓中的股票涨跌情况，估算出基金当前的涨跌幅。

## 技术栈
- **前端**: Vue 3 + Vite + Tailwind CSS
- **状态管理**: Pinia
- **路由**: Vue Router
- **后端**: Node.js + Express
- **数据源**: 聚宽(JQData) SDK

## 项目结构
```
FundValue/
├── src/                    # 前端源码
│   ├── api/               # API接口封装
│   │   └── jqdata.js      # 聚宽数据API
│   ├── stores/            # Pinia状态管理
│   │   └── fund.js        # 基金数据store
│   ├── views/             # 页面组件
│   │   ├── Home.vue       # 首页
│   │   └── Search.vue     # 基金查询页
│   ├── router/            # 路由配置
│   ├── App.vue            # 根组件
│   ├── main.js            # 入口文件
│   └── style.css          # 全局样式
├── backend/               # 后端服务
│   ├── start.js           # 服务器启动文件
│   └── package.json       # 后端依赖
├── index.html             # HTML模板
├── vite.config.js         # Vite配置
└── tailwind.config.js     # Tailwind配置
```

## 快速开始

### 1. 安装前端依赖
```bash
npm install
```

### 2. 安装后端依赖
```bash
cd backend
npm install express cors
cd ..
```

### 3. 启动后端服务（新终端）
```bash
cd backend
node start.js
```
后端服务将在 `http://localhost:8000` 运行

### 4. 启动前端开发服务器（原终端）
```bash
npm run dev
```
前端服务将在 `http://localhost:5173` 运行

## 功能说明

### 基金估算功能
1. 输入基金代码（如：000001）
2. 系统查询该基金的最新持仓情况
3. 获取持仓中各股票的实时价格和涨跌幅
4. 根据持仓比例计算基金估算涨跌幅
5. 展示估算结果和持仓明细

### 计算逻辑
```
基金估算涨跌幅 = Σ(持仓市值 × 个股涨跌幅) / 总持仓市值

其中：
- 持仓市值 = 持股数量 × 成本价
- 个股涨跌幅 = (当前价 - 开盘价) / 开盘价 × 100%
```

## API接口

### 后端接口

#### 1. 获取基金持仓
```
GET /api/fund/holdings?fundCode=000001

响应：
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

#### 2. 获取股票价格
```
POST /api/stock/prices
{
  "codes": ["000001.XSHE", "000002.XSHE"]
}

响应：
{
  "000001.XSHE": {
    "open": 12.50,
    "close": 12.80,
    "high": 12.90,
    "low": 12.40,
    "changePercent": 2.40
  }
}
```

#### 3. 健康检查
```
GET /api/health

响应：
{ "status": "ok" }
```

## 注意事项

1. **聚宽认证**：使用聚宽数据前需要先认证账户
   ```javascript
   auth(username, password)
   ```

2. **股票代码格式**：
   - 上海交易所：股票代码.XSHG（如：600000.XSHG）
   - 深圳交易所：股票代码.XSHE（如：000001.XSHE）


3. **数据来源**：使用akshare获取真实基金持仓数据，jqdatasdk获取股票实时价格数据

4. **交易时间**：股票价格数据仅在工作日的交易时段内实时更新


## 扩展功能

后续可以添加的功能：
- 基金历史净值查询
- 持仓变动追踪
- 收益率计算
- 数据图表展示
- 用户收藏管理
