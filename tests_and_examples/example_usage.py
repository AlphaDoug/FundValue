#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
东方财富股票爬虫使用示例
演示如何输入股票代码获取股票数据
"""

from fetch_eastmoney_stock import EastMoneyStockSpider
import sys


def get_stock_info(stock_code):
    """
    获取股票信息
    Args:
        stock_code: 股票代码（6位数字）
    Returns:
        股票数据字典
    """
    spider = EastMoneyStockSpider()
    return spider.get_stock_data(stock_code)


def main():
    """主函数 - 交互式输入股票代码"""
    print("=" * 60)
    print("东方财富股票数据查询工具")
    print("=" * 60)
    print()

    # 命令行参数模式
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
    else:
        # 交互式输入模式
        stock_code = input("请输入股票代码（例如：000001）：").strip()

    if not stock_code:
        print("股票代码不能为空！")
        return

    print(f"\n正在获取股票 {stock_code} 的数据...\n")

    # 获取数据
    data = get_stock_info(stock_code)

    if data:
        # 打印格式化的数据
        spider = EastMoneyStockSpider()
        spider.print_stock_data(data)

        # 显示关键指标
        print("关键指标:")
        print(f"  - 股票名称: {data['股票名称']}")
        print(f"  - 最新价格: {data['最新']} 元")
        print(f"  - 涨跌幅度: {data['涨幅']}%")
        print(f"  - 成交金额: {data['金额']}")
        print(f"  - 换手率: {data['换手']}%")

        # 判断涨跌
        if data['涨幅'] > 0:
            print(f"\n[涨] {data['股票名称']} 上涨 {data['涨幅']}%")
        elif data['涨幅'] < 0:
            print(f"\n[跌] {data['股票名称']} 下跌 {abs(data['涨幅'])}%")
        else:
            print(f"\n[平] {data['股票名称']} 平盘")

    else:
        print(f"❌ 无法获取股票 {stock_code} 的数据")
        print("可能原因：")
        print("  1. 股票代码不存在")
        print("  2. 网络连接问题")
        print("  3. 非交易时间，数据未更新")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n发生错误：{e}")
