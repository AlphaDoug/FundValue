"""
测试修改后的股票涨跌幅计算逻辑
"""
import sys
sys.path.append('backend')
from datetime import datetime
from backend.fund_api import get_single_stock_price

print("=" * 60)
print("测试股票涨跌幅计算逻辑（使用模拟数据）")
print("=" * 60)

# 测试不同的时间点
test_times = [
    datetime(2026, 2, 7, 9, 0),    # 交易时间前
    datetime(2026, 2, 7, 9, 30),   # 开盘时刻
    datetime(2026, 2, 7, 10, 30),  # 交易中（上午）
    datetime(2026, 2, 7, 11, 30),  # 上午收盘
    datetime(2026, 2, 7, 12, 0),   # 午休
    datetime(2026, 2, 7, 13, 0),   # 下午开盘
    datetime(2026, 2, 7, 14, 0),   # 下午交易中
    datetime(2026, 2, 7, 15, 0),   # 下午收盘
    datetime(2026, 2, 7, 16, 0),   # 交易时间后
]

test_stock = "002025"

for test_time in test_times:
    print(f"\n{'=' * 60}")
    print(f"测试时间: {test_time.strftime('%H:%M')} - {test_time.strftime('%A')}")
    print(f"{'=' * 60}")
    result = get_single_stock_price(test_stock, current_time=test_time)
    if result:
        print(f"股票: {result['name']} ({result['code']})")
        print(f"开盘价: {result['open']:.2f}")
        print(f"昨收价: {result['preClose']:.2f}")
        print(f"当前价: {result['close']:.2f}")
        print(f"涨跌额: {result['change']:.2f}")
        print(f"涨跌幅: {result['changePercent']:.2f}%")
    else:
        print("查询失败")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
