"""检查时间序列"""
import json

with open('stock_minute_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 查看第一个股票的时间序列
stock_code = list(data.keys())[0]
prices = data[stock_code]['minute_prices']

print(f"股票: {stock_code}")
print(f"总数据点: {len(prices)}")
print("\n时间序列（每隔30个点）:")

for i in range(0, len(prices), 30):
    time = prices[i]['time']
    price = prices[i]['price']
    print(f"索引 {i:3d}: {time}  价格: {price:.2f}")

print(f"\n最后几个点:")
for i in range(len(prices) - 5, len(prices)):
    time = prices[i]['time']
    price = prices[i]['price']
    print(f"索引 {i:3d}: {time}  价格: {price:.2f}")

# 计算上午和下午的分界点
print("\n分界点分析:")
print(f"总点数: {len(prices)}")
print(f"09:30 索引: 0")
print(f"11:30 应该在索引: 120")
print(f"13:00 应该在索引: 121")
print(f"15:00 应该在索引: {len(prices)-1}")

print(f"\n实际:")
print(f"09:30: {prices[0]['time']}")
print(f"11:30: {prices[120]['time']}")
print(f"13:00: {prices[121]['time']}")
print(f"15:00: {prices[-1]['time']}")
