"""
测试单个股票价格获取接口
"""
import akshare as ak
import os


def get_single_stock_price(stock_code):
    """获取单个股票的实时价格"""
    try:
        # 设置 requests 的代理为空
        import requests
        original_proxies = requests.Session().proxies
        requests.Session().proxies = {}

        # 去除市场后缀
        code = stock_code.replace('.XSHE', '').replace('.XSHG', '').replace('.XBJE', '')

        print(f"查询股票 {code} 的五档行情...")

        # 使用stock_bid_ask_em接口
        df = ak.stock_bid_ask_em()

        if df.empty:
            print(f"  股票 {code} 未获取到数据")
            return None

        # 数据格式是item-value对，转换为字典
        price_dict = {}
        for _, row in df.iterrows():
            price_dict[row['item']] = row['value']

        # 提取关键价格数据
        result = {
            'code': code,
            'name': code,  # 这个接口不返回股票名称
            'open': float(price_dict.get('今开', 0)),
            'close': float(price_dict.get('最新', 0)),
            'high': float(price_dict.get('最高', 0)),
            'low': float(price_dict.get('最低', 0)),
            'preClose': float(price_dict.get('昨收', 0)),
            'change': float(price_dict.get('涨跌', 0)),
            'changePercent': float(price_dict.get('涨幅', 0)),
            'volume': int(price_dict.get('总手', 0)),
            'amount': int(price_dict.get('金额', 0))
        }

        # 如果涨幅字段是NaN，尝试用涨跌/昨收计算
        if result['preClose'] > 0:
            if result['changePercent'] == 0 and result['change'] != 0:
                result['changePercent'] = (result['change'] / result['preClose']) * 100
            elif result['changePercent'] == 0:
                result['change'] = result['close'] - result['preClose']
                result['changePercent'] = (result['change'] / result['preClose']) * 100

        print(f"  {code}: 最新={result['close']:.2f} 涨跌幅={result['changePercent']:.2f}%")

        return result

    except Exception as e:
        print(f"  查询股票 {code} 失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """测试函数"""
    print("=" * 60)
    print("测试单个股票价格接口")
    print("=" * 60 + "\n")

    # 从命令行参数获取股票代码
    import sys
    if len(sys.argv) > 1:
        stock_codes = sys.argv[1:]
        print(f"从命令行获取股票代码: {stock_codes}")
    else:
        print("使用: python test_single_stock.py <股票代码1> <股票代码2> ...")
        print("示例: python test_single_stock.py 000001 600000")
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
        result = get_single_stock_price(stock_code)
        if result:
            results.append(result)
            print(f"  股票代码: {result['code']}")
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
    print(f"失败数量: {len(stock_codes) - len(results)} 个")

    if results:
        print("\n成功获取的股票:")
        for r in results:
            print(f"  {r['code']}: {r['close']:.2f} ({r['changePercent']:+.2f}%)")

    print("\n测试完成！")

if __name__ == '__main__':
    main()
