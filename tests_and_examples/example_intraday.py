#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
股票分时数据查询示例
演示如何获取股票的分时数据
"""

from fetch_eastmoney_intraday import EastMoneyIntradaySpider
import json


def main():
    """主函数"""
    spider = EastMoneyIntradaySpider()

    print("=" * 100)
    print("股票分时数据查询工具")
    print("=" * 100)

    # 示例1: 获取1分钟分时数据（默认）
    print("\n【示例1】获取平安银行(000001)的1分钟分时数据")
    data_1m = spider.get_intraday_data('000001', scale=1, datalen=240)
    if data_1m:
        spider.print_intraday_data(data_1m, show_all=False)

    # 示例2: 获取5分钟分时数据
    print("\n" + "=" * 100)
    print("\n【示例2】获取平安银行(000001)的5分钟分时数据")
    data_5m = spider.get_intraday_data('000001', scale=5, datalen=240)
    if data_5m:
        spider.print_intraday_data(data_5m, show_all=True)

    # 示例3: 获取15分钟分时数据
    print("\n" + "=" * 100)
    print("\n【示例3】获取贵州茅台(600519)的15分钟分时数据")
    data_15m = spider.get_intraday_data('600519', scale=15, datalen=100)
    if data_15m:
        spider.print_intraday_data(data_15m, show_all=True)

    # 示例4: 保存为JSON
    if data_1m:
        print("\n" + "=" * 100)
        print("\n保存数据到文件...")
        with open('intraday_example.json', 'w', encoding='utf-8') as f:
            json.dump(data_1m, f, ensure_ascii=False, indent=2)
        print("数据已保存到 intraday_example.json")

    # 统计信息
    if data_1m:
        print("\n" + "=" * 100)
        print("\n【统计信息】")
        total_volume = sum(item['成交量'] for item in data_1m['分时数据'])
        total_amount = sum(item['成交额'] for item in data_1m['分时数据'])
        prices = [item['收盘价'] for item in data_1m['分时数据']]

        print(f"  总成交量: {total_volume/100:,.0f} 手")
        print(f"  总成交额: {total_amount/100000000:,.2f} 亿元")
        print(f"  最高价格: {max(prices):.2f} 元")
        print(f"  最低价格: {min(prices):.2f} 元")
        print(f"  价格波动: {max(prices) - min(prices):.2f} 元")
        print(f"  平均价格: {sum(prices)/len(prices):.2f} 元")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
