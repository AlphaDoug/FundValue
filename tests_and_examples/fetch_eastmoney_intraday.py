#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
东方财富网股票分时数据爬虫
获取股票的分时数据（开盘价、最高价、最低价、收盘价、成交量等）
"""

import requests
import json
import datetime


class EastMoneyIntradaySpider:
    """东方财富股票分时数据爬虫"""

    def __init__(self):
        # 多个备用User-Agent
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        ]

        self.session = requests.Session()
        self._update_headers(0)

    def _update_headers(self, index):
        """更新请求头"""
        self.headers = {
            'User-Agent': self.user_agents[index % len(self.user_agents)],
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://quote.eastmoney.com/',
            'Cache-Control': 'no-cache',
        }
        self.session.headers.update(self.headers)

    def format_stock_code(self, code):
        """
        格式化股票代码，添加市场后缀
        Args:
            code: 股票代码 (6位数字)
        Returns:
            带市场后缀的代码，如 sz000001 或 sh600000
        """
        code = str(code).strip()

        # 如果已经有后缀，直接返回
        if '.' in code:
            return code.lower()

        # 判断市场
        if code.startswith('6'):
            return f'sh{code}'  # 上海证券交易所
        elif code.startswith('0') or code.startswith('3'):
            return f'sz{code}'  # 深圳证券交易所
        else:
            # 默认深圳
            return f'sz{code}'

    def get_intraday_data(self, code, scale=1, datalen=240):
        """
        获取股票分时数据
        Args:
            code: 股票代码
            scale: 时间周期，1=1分钟, 5=5分钟, 15=15分钟, 30=30分钟, 60=60分钟
            datalen: 数据条数，最多240条
        Returns:
            分时数据列表，每个元素包含时间、价格、成交量等信息
        """
        formatted_code = self.format_stock_code(code)

        # 构造API URL
        # 新浪分时数据接口
        api_url = f"https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol={formatted_code}&scale={scale}&ma=no&datalen={datalen}"

        try:
            print(f"正在获取股票 {code} 的分时数据...")
            response = self.session.get(api_url, timeout=10)

            if response.status_code == 200:
                content = response.text.strip()

                if content and content.startswith('['):
                    data = json.loads(content)

                    if data:
                        # 股票基本信息
                        result = {
                            '股票代码': code,
                            '时间周期': f"{scale}分钟",
                            '分时数据': []
                        }

                        # 解析分时数据
                        for item in data:
                            result['分时数据'].append({
                                '时间': item['day'],
                                '开盘价': float(item['open']),
                                '收盘价': float(item['close']),
                                '最高价': float(item['high']),
                                '最低价': float(item['low']),
                                '成交量': int(item['volume']),  # 股
                                '成交额': float(item['amount']),  # 元
                            })

                        return result
                    else:
                        print(f"未找到股票分时数据: {code}")
                        return None
                else:
                    print(f"返回数据格式错误: {code}")
                    return None
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return None

        except Exception as e:
            print(f"获取分时数据时出错: {e}")
            return None

    def print_intraday_data(self, intraday_data, show_all=False):
        """打印分时数据

        Args:
            intraday_data: 分时数据
            show_all: 是否显示全部数据，否则只显示部分
        """
        if not intraday_data:
            print("未获取到分时数据")
            return

        print(f"\n{'='*100}")
        print(f"股票代码: {intraday_data['股票代码']}")
        print(f"时间周期: {intraday_data['时间周期']}")
        print(f"{'='*100}")
        print(f"\n分时数据 ({len(intraday_data['分时数据'])} 条):")
        print(f"\n{'时间':<20} {'开盘价':<10} {'收盘价':<10} {'最高价':<10} {'最低价':<10} {'成交量(手)':<15} {'成交额(万)':<15}")
        print("-" * 100)

        # 显示数据
        data_list = intraday_data['分时数据']
        if not show_all and len(data_list) > 20:
            # 只显示前10条和后10条
            display_list = data_list[:10] + [{'时间': '...', '开盘价': 0, '收盘价': 0, '最高价': 0, '最低价': 0, '成交量': 0, '成交额': 0}] + data_list[-10:]
        else:
            display_list = data_list

        for item in display_list:
            if item['时间'] == '...':
                print(f"{'...':<100}")
            else:
                print(f"{item['时间']:<20} "
                      f"{item['开盘价']:<10.2f} "
                      f"{item['收盘价']:<10.2f} "
                      f"{item['最高价']:<10.2f} "
                      f"{item['最低价']:<10.2f} "
                      f"{item['成交量']/100:<15,.0f} "
                      f"{item['成交额']/10000:<15,.2f}")


def main():
    """主函数 - 测试示例"""
    spider = EastMoneyIntradaySpider()

    # 测试获取平安银行(000001)的分时数据
    print("测试获取股票分时数据...")
    intraday_data = spider.get_intraday_data('000001')

    if intraday_data:
        spider.print_intraday_data(intraday_data)

        # 保存为JSON文件
        with open('intraday_data.json', 'w', encoding='utf-8') as f:
            json.dump(intraday_data, f, ensure_ascii=False, indent=2)
        print(f"\n数据已保存到 intraday_data.json")
    else:
        print("获取分时数据失败")


if __name__ == '__main__':
    main()
