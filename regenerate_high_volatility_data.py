"""
增大股票模拟数据的波动幅度
"""
import json
import random

# 加载现有数据
print("加载现有数据...")
with open('stock_minute_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"共 {len(data)} 只股票")

# 为每只股票增大波动幅度
for stock_code, stock_info in data.items():
    base_price = stock_info.get('base_price', 50.0)
    open_price = stock_info.get('open_price', base_price * random.uniform(0.98, 1.02))
    trend = stock_info.get('trend', '震荡')

    print(f"\n处理股票 {stock_code}: {stock_info.get('name', stock_code)}")
    print(f"  基准价: {base_price:.2f}, 开盘价: {open_price:.2f}, 趋势: {trend}")

    # 生成新的分钟价格数据
    minute_prices = []

    # 时间范围：上午9:30-11:30 (121分钟) + 下午13:00-15:00 (121分钟) = 242分钟
    morning_times = []
    for hour in range(9, 12):
        for minute in range(0, 60):
            if hour == 9 and minute < 30:
                continue
            if hour == 11 and minute > 30:
                continue
            morning_times.append(f"{hour:02d}:{minute:02d}")

    afternoon_times = []
    for hour in range(13, 16):  # 13, 14, 15
        for minute in range(0, 60):
            # 只包含13:00-15:00的时间段
            if hour == 15 and minute > 0:
                break
            afternoon_times.append(f"{hour:02d}:{minute:02d}")

    all_times = morning_times + afternoon_times

    # 根据趋势设置目标涨跌幅（限制在±10%范围内）
    if trend == "震荡上行":
        target_change = random.uniform(2, 5)  # 2%到5%的上涨
    elif trend == "震荡下行":
        target_change = random.uniform(-5, -2)  # -5%到-2%的下跌
    elif trend == "箱体震荡":
        target_change = random.uniform(-3, 3)  # -3%到3%的震荡
    elif trend == "快速拉升":
        target_change = random.uniform(5, 10)  # 5%到10%的上涨
    elif trend == "瞬间拉升":
        target_change = random.uniform(5, 10)  # 5%到10%的上涨
    elif trend == "快速下跌":
        target_change = random.uniform(-10, -5)  # -10%到-5%的下跌
    elif trend == "瞬间下跌":
        target_change = random.uniform(-10, -5)  # -10%到-5%的下跌
    else:
        target_change = random.uniform(-5, 5)  # -5%到5%的随机

    print(f"  目标涨跌幅: {target_change:.2f}%")

    current_price = open_price
    price_history = [open_price]

    # 为每分钟生成价格（增大波动）
    for i, time_str in enumerate(all_times):
        # 进度比例（0到1）
        progress = i / len(all_times)

        # 目标价格
        target_price = open_price * (1 + target_change / 100)

        # 基础波动（0.3%到1%）
        base_volatility = random.uniform(-1.0, 1.0)

        # 趋势倾向
        trend_force = (target_price - current_price) * 0.08  # 趋势拉力

        # 偶尔的突发波动（5%概率，幅度减小）
        if random.random() < 0.05:
            sudden_change = random.uniform(-1.5, 1.5)  # -1.5%到1.5%的突发波动
        else:
            sudden_change = 0

        # 计算新价格
        price_change_percent = base_volatility + trend_force / open_price * 100 + sudden_change
        current_price = current_price * (1 + price_change_percent / 100)

        # 确保价格在±10%范围内
        current_price = max(current_price, base_price * 0.9)  # 最多下跌10%
        current_price = min(current_price, base_price * 1.1)  # 最多上涨10%

        minute_prices.append({
            "time": time_str,
            "price": round(current_price, 2)
        })

        price_history.append(current_price)

    # 更新数据
    stock_info['open_price'] = open_price
    stock_info['minute_prices'] = minute_prices

    # 计算实际涨跌幅
    actual_change = (minute_prices[-1]['price'] - open_price) / open_price * 100
    print(f"  实际涨跌幅: {actual_change:.2f}%")
    print(f"  价格范围: {min(p['price'] for p in minute_prices):.2f} - {max(p['price'] for p in minute_prices):.2f}")

# 保存新数据
print("\n保存新数据...")
with open('stock_minute_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("完成！")
