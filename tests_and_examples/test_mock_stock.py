"""
测试股票数据 - 使用模拟数据
不依赖外部API，用于测试前端功能
"""

def get_single_stock_price_mock(stock_code):
    """获取单个股票的模拟价格数据"""
    # 常见股票的模拟数据
    mock_data = {
        '000001': {'close': 12.50, 'open': 12.30, 'preClose': 12.20, 'high': 12.60, 'low': 12.25, 'changePercent': 2.46},
        '000002': {'close': 8.50, 'open': 8.40, 'preClose': 8.45, 'high': 8.55, 'low': 8.35, 'changePercent': 0.59},
        '600000': {'close': 9.20, 'open': 9.10, 'preClose': 9.15, 'high': 9.30, 'low': 9.05, 'changePercent': 0.55},
        '300394': {'close': 158.30, 'open': 156.00, 'preClose': 155.50, 'high': 159.00, 'low': 155.80, 'changePercent': 1.80},
        '300308': {'close': 162.50, 'open': 160.00, 'preClose': 159.80, 'high': 163.00, 'low': 159.50, 'changePercent': 1.69},
        '002463': {'close': 29.80, 'open': 30.00, 'preClose': 30.10, 'high': 30.20, 'low': 29.70, 'changePercent': -1.00},
        '002371': {'close': 310.00, 'open': 308.00, 'preClose': 305.50, 'high': 312.00, 'low': 307.00, 'changePercent': 1.47},
        '300476': {'close': 25.00, 'open': 24.50, 'preClose': 24.60, 'high': 25.20, 'low': 24.40, 'changePercent': 1.63},
        '300502': {'close': 98.50, 'open': 97.00, 'preClose': 96.80, 'high': 99.00, 'low': 96.50, 'changePercent': 1.76},
        '601138': {'close': 25.80, 'open': 25.50, 'preClose': 25.30, 'high': 26.00, 'low': 25.40, 'changePercent': 1.98},
    }

    # 返回模拟数据或生成随机数据
    if stock_code in mock_data:
        data = mock_data[stock_code].copy()
    else:
        import random
        base_price = random.uniform(10, 200)
        data = {
            'close': base_price,
            'open': base_price * random.uniform(0.98, 1.02),
            'preClose': base_price * random.uniform(0.98, 1.02),
            'high': base_price * random.uniform(1.00, 1.03),
            'low': base_price * random.uniform(0.97, 1.00),
            'changePercent': random.uniform(-5, 5)
        }

    # 计算涨跌额
    data['change'] = data['close'] - data['preClose']
    data['volume'] = int(random.uniform(100000, 10000000))
    data['amount'] = int(data['volume'] * data['close'])

    return data

def main():
    """测试函数"""
    print("=" * 60)
    print("测试股票价格接口（使用模拟数据）")
    print("=" * 60 + "\n")

    # 从命令行参数获取股票代码
    import sys
    if len(sys.argv) > 1:
        stock_codes = sys.argv[1:]
        print(f"从命令行获取股票代码: {stock_codes}")
    else:
        print("使用: python test_mock_stock.py <股票代码1> <股票代码2> ...")
        print("示例: python test_mock_stock.py 000001 600000")
        print("\n请输入要查询的股票代码（多个用空格分隔）:")
        user_input = input("> ").strip()
        if not user_input:
            print("未输入股票代码，退出")
            return
        stock_codes = user_input.split()

    results = []

    for stock_code in stock_codes:
        print(f"\n测试股票: {stock_code}")
        print("-" * 40)
        result = get_single_stock_price_mock(stock_code)
        if result:
            results.append(result)
            print(f"  股票代码: {result.get('code', stock_code)}")
            print(f"  最新价: {result['close']:.2f}")
            print(f"  今开: {result['open']:.2f}")
            print(f"  昨收: {result['preClose']:.2f}")
            print(f"  最高: {result['high']:.2f}")
            print(f"  最低: {result['low']:.2f}")
            print(f"  涨跌额: {result['change']:.2f}")
            print(f"  涨跌幅: {result['changePercent']:.2f}%")
            print(f"  成交量: {result['volume']}手")
            print(f"  成交额: {result['amount']}元")

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    print(f"成功获取: {len(results)}/{len(stock_codes)} 个股票数据")

    if results:
        print("\n成功获取的股票:")
        for r in results:
            print(f"  {r.get('code', stock_codes[results.index(r)])}: {r['close']:.2f} ({r['changePercent']:+.2f}%)")

    print("\n测试完成！")
    print("\n提示: 如需使用真实数据，请解决网络代理问题或使用其他数据源")

if __name__ == '__main__':
    main()
