# 股票分时数据爬虫使用说明

## 功能说明

这个爬虫可以从新浪财经获取股票的分时数据（分钟K线），支持多种时间周期。

## 支持的时间周期

- **1分钟** (scale=1) - 最精细的分时数据
- **5分钟** (scale=5)
- **15分钟** (scale=15)
- **30分钟** (scale=30)
- **60分钟** (scale=60)

## 安装依赖

```bash
pip install requests
```

## 基本使用

### 获取1分钟分时数据

```python
from fetch_eastmoney_intraday import EastMoneyIntradaySpider

# 创建爬虫实例
spider = EastMoneyIntradaySpider()

# 获取1分钟分时数据（默认240条）
data = spider.get_intraday_data('000001', scale=1, datalen=240)

# 打印数据
spider.print_intraday_data(data, show_all=False)
```

### 获取5分钟分时数据

```python
# 获取5分钟分时数据
data = spider.get_intraday_data('000001', scale=5, datalen=100)
spider.print_intraday_data(data)
```

### 批量获取多只股票

```python
stocks = ['000001', '600519', '000858']

for code in stocks:
    data = spider.get_intraday_data(code, scale=1, datalen=240)
    if data:
        print(f"\n{code}: 获取 {len(data['分时数据'])} 条数据")
```

## API说明

### 新浪财经分时数据接口

**URL**: `https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData`

**参数**:
- `symbol`: 股票代码，格式为 sz000001 或 sh600519
- `scale`: 时间周期，1=1分钟, 5=5分钟, 15=15分钟, 30=30分钟, 60=60分钟
- `ma`: 是否显示均线，no=不显示
- `datalen`: 数据条数，最多240条

**返回数据格式**:

```json
[
  {
    "day": "2026-02-06 09:31:00",
    "open": "11.08",
    "high": "11.11",
    "low": "11.06",
    "close": "11.10",
    "volume": "4125200",
    "amount": "45702714.3579"
  }
]
```

## 返回数据格式

```json
{
  "股票代码": "000001",
  "时间周期": "1分钟",
  "分时数据": [
    {
      "时间": "2026-02-06 09:31:00",
      "开盘价": 11.08,
      "收盘价": 11.10,
      "最高价": 11.11,
      "最低价": 11.06,
      "成交量": 4125200,
      "成交额": 45702714.3579
    }
  ]
}
```

## 字段说明

| 字段 | 说明 | 单位 |
|-----|------|------|
| 时间 | K线时间点 | - |
| 开盘价 | 该周期开盘价 | 元 |
| 收盘价 | 该周期收盘价 | 元 |
| 最高价 | 该周期最高价 | 元 |
| 最低价 | 该周期最低价 | 元 |
| 成交量 | 该周期成交量 | 股 |
| 成交额 | 该周期成交额 | 元 |

## 示例输出

```
====================================================================================================
股票代码: 000001
时间周期: 1分钟
====================================================================================================

分时数据 (240 条):

时间                   开盘价        收盘价        最高价        最低价        成交量(手)          成交额(万)
----------------------------------------------------------------------------------------------------
2026-02-06 09:31:00  11.08      11.10      11.11      11.06      41,252          4,570.27
2026-02-06 09:32:00  11.11      11.10      11.14      11.09      25,756          2,863.85
2026-02-06 09:33:00  11.09      11.08      11.10      11.08      7,003           776.52
...
2026-02-06 15:00:00  11.05      11.05      11.05      11.05      5,988           661.72
```

## 高级用法

### 数据分析

```python
import numpy as np

# 获取分时数据
data = spider.get_intraday_data('000001', scale=1, datalen=240)

# 提取价格序列
prices = [item['收盘价'] for item in data['分时数据']]
volumes = [item['成交量'] for item in data['分时数据']]

# 计算统计指标
print(f"最高价: {max(prices):.2f}")
print(f"最低价: {min(prices):.2f}")
print(f"平均价: {np.mean(prices):.2f}")
print(f"价格波动: {max(prices) - min(prices):.2f}")
print(f"总成交量: {sum(volumes)/100:,.0f} 手")
```

### 保存为CSV

```python
import csv

data = spider.get_intraday_data('000001', scale=1, datalen=240)

with open('intraday_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['时间', '开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额'])

    for item in data['分时数据']:
        writer.writerow([
            item['时间'],
            item['开盘价'],
            item['收盘价'],
            item['最高价'],
            item['最低价'],
            item['成交量'],
            item['成交额']
        ])
```

## 注意事项

1. **数据时效性**:
   - 交易时间内数据实时更新
   - 非交易时间显示的是最近交易日的数据
   - 交易时间：工作日 9:30-11:30, 13:00-15:00

2. **数据限制**:
   - 最多获取240条数据
   - 1分钟数据可以覆盖最近的4个交易日
   - 更长时间周期可以获取更久的历史数据

3. **单位说明**:
   - 价格单位：元
   - 成交量单位：股（程序中会转换为手显示）
   - 成交额单位：元（程序中会转换为万元显示）

4. **使用建议**:
   - 实时监控使用1分钟数据
   - 短线分析使用5分钟或15分钟数据
   - 中线分析使用30分钟或60分钟数据

## 命令行使用

```bash
# 运行示例
python example_intraday.py

# 运行测试
python fetch_eastmoney_intraday.py
```

## 错误处理

```python
data = spider.get_intraday_data('000001', scale=1, datalen=240)
if data:
    print(f"成功获取 {len(data['分时数据'])} 条数据")
else:
    print("获取数据失败")
```

## 示例应用场景

1. **实时监控**: 每1分钟获取最新价格变化
2. **技术分析**: 计算均线、MACD等技术指标
3. **量价分析**: 分析成交量与价格的关系
4. **波动分析**: 计算价格波动率和振幅
5. **数据存储**: 定时抓取存储到数据库

## 许可说明

本工具仅供学习和研究使用，请勿用于商业用途。使用时请遵守相关网站的服务条款。
