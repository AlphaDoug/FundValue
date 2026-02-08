# 东方财富网股票数据爬虫使用说明

## 功能说明

这个爬虫可以从东方财富网获取股票的实时数据，包括以下字段：

- **股票代码**: 6位股票代码
- **股票名称**: 股票中文名称
- **最新**: 最新价格
- **均价**: 平均价格
- **涨幅**: 涨跌幅（百分比）
- **涨跌**: 涨跌额（绝对值）
- **总手**: 成交总量（手）
- **金额**: 成交金额（亿元）
- **换手**: 换手率（百分比）
- **最高**: 最高价
- **最低**: 最低价
- **今开**: 今日开盘价
- **昨收**: 昨日收盘价
- **涨停**: 涨停价
- **跌停**: 跌停价

## 安装依赖

```bash
pip install requests beautifulsoup4
```

## 基本使用

### 单个股票查询

```python
from fetch_eastmoney_stock import EastMoneyStockSpider

# 创建爬虫实例
spider = EastMoneyStockSpider()

# 获取股票数据
stock_data = spider.get_stock_data('000001')

# 打印数据
spider.print_stock_data(stock_data)

# 访问具体字段
print(f"最新价: {stock_data['最新']}")
print(f"涨幅: {stock_data['涨幅']}%")
```

### 批量查询

```python
from fetch_eastmoney_stock import EastMoneyStockSpider

spider = EastMoneyStockSpider()

stocks = ['000001', '600519', '000858', '002594']

for code in stocks:
    data = spider.get_stock_data(code)
    if data:
        print(f"{code} {data['股票名称']}: {data['最新']} ({data['涨幅']}%)")
```

### 保存为JSON

```python
import json
from fetch_eastmoney_stock import EastMoneyStockSpider

spider = EastMoneyStockSpider()
data = spider.get_stock_data('000001')

with open('stock_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## 股票代码格式

爬虫会自动识别股票代码所属市场：

- **深圳股票**: 000xxx, 003xxx, 300xxx（创业板）
- **上海股票**: 600xxx, 601xxx, 603xxx, 605xxx

也可以直接指定市场后缀：
- `000001` 或 `sz000001` - 平安银行（深圳）
- `600519` 或 `sh600519` - 贵州茅台（上海）

## 返回数据格式

```json
{
  "股票代码": "000001",
  "股票名称": "平安银行",
  "最新": 11.05,
  "均价": 11.05,
  "涨幅": -0.36,
  "涨跌": -0.04,
  "总手": 727710.0,
  "金额": "8.04亿",
  "换手": 0.37,
  "最高": 11.14,
  "最低": 10.99,
  "今开": 11.08,
  "昨收": 11.09,
  "涨停": 12.2,
  "跌停": 9.98
}
```

## API说明

爬虫使用以下API接口（按优先级）：

1. **腾讯行情接口**: `https://qt.gtimg.cn/q={market}{code}`
   - 优点：响应快，数据完整
   - 包含：价格、成交量、成交额、换手率等

2. **新浪行情接口**: `https://hq.sinajs.cn/list={market}{code}`
   - 备用接口，某些环境下可能被限制

3. **东方财富API**: `https://push2.eastmoney.com/api/qt/stock/get`
   - 官方API，字段最全
   - 需要特定的请求参数

## 注意事项

1. **数据时效性**: 
   - 股票交易时间为工作日 9:30-11:30, 13:00-15:00
   - 非交易时间可能显示昨收数据或无数据

2. **单位说明**:
   - 价格单位：元
   - 成交量单位：手（1手=100股）
   - 成交额单位：亿元
   - 换手率、涨幅：百分比（已去除%符号）

3. **限流建议**:
   - 批量查询时建议添加延迟，避免被限流
   - 使用多个IP或代理可以提高并发数

4. **数据准确性**:
   - 建议在交易时间获取实时数据
   - 不同接口的数据可能略有差异

## 命令行使用

```bash
# 运行测试
python fetch_eastmoney_stock.py

# 测试多个股票
python test_multi_stocks.py
```

## 错误处理

如果获取失败，会自动尝试其他API接口。如果所有接口都失败，返回 `None`。

```python
data = spider.get_stock_data('000001')
if data:
    print(data)
else:
    print("获取数据失败")
```

## 示例输出

```
==================================================
股票代码: 000001
股票名称: 平安银行
==================================================
最新: 11.05
均价: 11.05
涨幅: -0.36
涨跌: -0.04
总手: 727710.0
金额: 8.04亿
换手: 0.37
最高: 11.14
最低: 10.99
今开: 11.08
昨收: 11.09
涨停: 12.2
跌停: 9.98
==================================================
```

## 扩展功能

### 获取指定字段

```python
# 只获取关心的字段
fields = ['最新', '涨幅', '成交额']
data = spider.get_stock_data('000001')
result = {k: data[k] for k in fields if k in data}
```

### 过滤条件

```python
# 找出涨幅大于5%的股票
stocks = ['000001', '600519', '000858', '002594']
for code in stocks:
    data = spider.get_stock_data(code)
    if data and data['涨幅'] > 5:
        print(f"{data['股票名称']}: 涨幅 {data['涨幅']}%")
```

## 许可说明

本工具仅供学习和研究使用，请勿用于商业用途。使用时请遵守相关网站的服务条款。
