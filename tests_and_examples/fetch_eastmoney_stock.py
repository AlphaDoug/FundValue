#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
东方财富网股票数据爬虫
获取股票的详细信息：最新价、均价、涨幅、涨跌、总手、金额、换手、最高、最低、今开、昨收、涨停、跌停
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time


class EastMoneyStockSpider:
    """东方财富股票数据爬虫"""
    
    def __init__(self):
        # 多个备用User-Agent
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
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
    
    def get_stock_data_api(self, code):
        """
        通过API接口获取股票数据（推荐方法）
        Args:
            code: 股票代码
        Returns:
            股票数据字典
        """
        formatted_code = self.format_stock_code(code)
        market, stock_code = formatted_code[:2], formatted_code[2:]

        # 多个备用API接口
        api_urls = [
            # 接口1：腾讯接口
            f"https://qt.gtimg.cn/q={market}{stock_code}",
            # 接口2：新浪接口
            f"https://hq.sinajs.cn/list={market}{stock_code}",
            # 接口3：东方财富API
            f"https://push2.eastmoney.com/api/qt/stock/get?ut=fa5fd1943c7b386f172d6893dbfba10b&invt=2&fltt=2&fields=f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60,f107,f116,f117,f152,f162,f168,f169,f170,f174,f175,f184,f204,f205,f208,f209,f210,f211,f212,f213,f214,f215&secid={market}.{stock_code}",
        ]

        for idx, api_url in enumerate(api_urls):
            # 每个接口使用不同的User-Agent
            self._update_headers(idx)

            try:
                print(f"尝试接口 {idx + 1}...")
                response = self.session.get(api_url, timeout=10)

                if response.status_code == 200:
                    # 处理不同的接口格式
                    if 'push2.eastmoney.com' in api_url:
                        # 东方财富API
                        data = response.json()

                        if data and 'data' in data and data['data']:
                            stock_info = data['data']

                            result = {
                                '股票代码': stock_code,
                                '股票名称': stock_info.get('f58', '-'),  # 股票名称
                                '最新': stock_info.get('f43', '-'),  # 最新价
                                '今开': stock_info.get('f46', '-'),  # 开盘价
                                '昨收': stock_info.get('f60', '-'),  # 昨收价
                                '最高': stock_info.get('f44', '-'),  # 最高价
                                '最低': stock_info.get('f45', '-'),  # 最低价
                                '成交量': stock_info.get('f47', '-'),  # 成交量（手）
                                '成交额': stock_info.get('f48', '-'),  # 成交额（元）
                                '涨幅': stock_info.get('f170', '-'),  # 涨跌幅
                                '涨跌': stock_info.get('f169', '-'),  # 涨跌额
                                '换手': stock_info.get('f168', '-'),  # 换手率
                                '均价': stock_info.get('f117', '-'),  # 均价
                                '涨停': stock_info.get('f51', '-'),  # 涨停价
                                '跌停': stock_info.get('f52', '-'),  # 跌停价
                                '总手': stock_info.get('f47', '-'),  # 总手
                                '金额': stock_info.get('f48', '-'),  # 金额
                            }

                            return self._format_result(result)

                    elif 'gtimg.cn' in api_url:
                        # 腾讯接口
                        content = response.text.strip()
                        if content and '=' in content:
                            data_str = content.split('=')[1].strip('";')
                            if data_str and '~' in data_str:
                                values = data_str.split('~')
                                # 腾讯接口字段索引说明：
                                # 0: 股票ID, 1: 股票名称, 2: 股票代码, 3: 最新价, 4: 昨收, 5: 今开, 6: 成交量(股)
                                # 31: 涨跌, 32: 涨幅(%), 33: 最高, 34: 最低
                                # 35: 格式为"最新价/成交量/成交额"或空
                                # 36: 成交量, 37: 成交额(万元), 38: 换手率(%)
                                if len(values) > 40 and values[3]:  # 确保有价格数据
                                    latest_price = float(values[3])
                                    pre_close = float(values[4]) if values[4] else latest_price
                                    volume = float(values[6]) if values[6] else 0

                                    # 解析成交额 - 从索引35或索引57
                                    amount = 0
                                    if values[35] and '/' in values[35]:
                                        parts = values[35].split('/')
                                        if len(parts) >= 3:
                                            amount = float(parts[2]) if parts[2] else 0
                                    elif values[57]:
                                        amount = float(values[57]) * 10000 if values[57] else 0  # 转换为元

                                    # 计算均价
                                    avg_price = round(amount / volume / 100, 2) if volume > 0 and amount > 0 else latest_price

                                    result = {
                                        '股票代码': stock_code,
                                        '股票名称': values[1],
                                        '最新': latest_price,
                                        '今开': float(values[5]) if values[5] else '-',
                                        '昨收': pre_close,
                                        '最高': float(values[33]) if values[33] else '-',
                                        '最低': float(values[34]) if values[34] else '-',
                                        '成交量': volume,
                                        '成交额': amount,
                                        '涨幅': float(values[32]) if values[32] and values[32] != '' else '-',
                                        '涨跌': round(latest_price - pre_close, 2),
                                        '换手': float(values[38]) if values[38] and values[38] != '' else '-',
                                        '均价': avg_price,
                                        '涨停': round(pre_close * 1.1, 2),
                                        '跌停': round(pre_close * 0.9, 2),
                                        '总手': volume,
                                        '金额': f"{amount / 100000000:.2f}亿" if amount > 0 else '0.00亿',
                                    }
                                    return result

                    elif 'sinajs.cn' in api_url:
                        # 新浪接口
                        content = response.text.strip()
                        if content and '=' in content:
                            # 去除空行和空格
                            content = content.replace('\r\n', '').replace('\n', '')
                            if '"' in content:
                                data_str = content.split('"')[1]
                                if data_str and ',' in data_str:
                                    values = data_str.split(',')
                                    # 新浪接口字段索引：
                                    # 0: 股票名称, 1: 开盘价, 2: 昨收价, 3: 最新价, 4: 最高价, 5: 最低价,
                                    # 6: 买一, 7: 卖一, 8: 成交量(股), 9: 成交额(元)
                                    if len(values) > 30 and values[3]:
                                        try:
                                            latest_price = float(values[3])
                                            pre_close = float(values[2]) if values[2] else latest_price
                                            volume = float(values[8]) if values[8] else 0
                                            amount = float(values[9]) if values[9] else 0

                                            # 计算均价
                                            avg_price = round(amount / (volume / 100) / 10000, 2) if volume > 0 and amount > 0 else latest_price

                                            result = {
                                                '股票代码': stock_code,
                                                '股票名称': values[0],
                                                '最新': latest_price,
                                                '今开': float(values[1]) if values[1] else '-',
                                                '昨收': pre_close,
                                                '最高': float(values[4]) if values[4] else '-',
                                                '最低': float(values[5]) if values[5] else '-',
                                                '成交量': volume / 100,  # 转换为手
                                                '成交额': amount,
                                                '涨幅': round((latest_price - pre_close) / pre_close * 100, 2) if pre_close > 0 else '-',
                                                '涨跌': round(latest_price - pre_close, 2),
                                                '换手': '-',
                                                '均价': avg_price,
                                                '涨停': round(pre_close * 1.1, 2),
                                                '跌停': round(pre_close * 0.9, 2),
                                                '总手': volume / 100,
                                                '金额': f"{amount / 100000000:.2f}亿" if amount > 0 else '0.00亿',
                                            }
                                            return result
                                        except ValueError as e:
                                            print(f"解析新浪数据出错: {e}")
                                            continue

            except Exception as e:
                print(f"接口 {idx + 1} 出错: {e}")
                continue

        print("所有接口都尝试失败")
        return None

    def _format_result(self, result):
        """格式化返回结果"""
        # 转换单位和格式
        if result['最新'] != '-':
            result['最新'] = round(result['最新'] / 100, 2)
        if result['今开'] != '-':
            result['今开'] = round(result['今开'] / 100, 2)
        if result['昨收'] != '-':
            result['昨收'] = round(result['昨收'] / 100, 2)
        if result['最高'] != '-':
            result['最高'] = round(result['最高'] / 100, 2)
        if result['最低'] != '-':
            result['最低'] = round(result['最低'] / 100, 2)
        if result['均价'] != '-':
            result['均价'] = round(result['均价'] / 100, 2)
        if result['涨停'] != '-':
            result['涨停'] = round(result['涨停'] / 100, 2)
        if result['跌停'] != '-':
            result['跌停'] = round(result['跌停'] / 100, 2)
        if result['涨跌'] != '-':
            result['涨跌'] = round(result['涨跌'] / 100, 2)
        if result['涨幅'] != '-':
            result['涨幅'] = round(result['涨幅'] / 100, 2)
        if result['换手'] != '-':
            result['换手'] = round(result['换手'] / 100, 2)

        # 转换成交额单位
        if result['成交额'] != '-':
            amount = result['成交额'] / 100000000  # 转换为亿元
            result['金额'] = f"{amount:.2f}亿"

        return result
    
    def get_stock_data_html(self, code):
        """
        通过HTML解析获取股票数据（备用方法）
        Args:
            code: 股票代码
        Returns:
            股票数据字典
        """
        formatted_code = self.format_stock_code(code)
        url = f"https://quote.eastmoney.com/{formatted_code}.html"
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 尝试从script标签中提取JSON数据
                script_tags = soup.find_all('script')
                for script in script_tags:
                    script_content = script.string
                    if script_content and 'quote' in script_content and 'lastPrice' in script_content:
                        try:
                            # 提取JSON数据
                            json_match = re.search(r'var\s+\w+\s*=\s*({.*?});', script_content)
                            if json_match:
                                data = json.loads(json_match.group(1))
                                return self.parse_json_data(data)
                        except:
                            continue
                
                # 如果JSON提取失败，尝试HTML解析
                return self.parse_html_data(soup, code)
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"获取数据时出错: {e}")
            return None
    
    def parse_json_data(self, data):
        """解析JSON格式的股票数据"""
        result = {}

        # 根据实际返回的字段映射
        field_mapping = {
            'lastPrice': '最新',
            'avgPrice': '均价',
            'changePercent': '涨幅',
            'change': '涨跌',
            'volume': '总手',
            'amount': '金额',
            'turnoverRate': '换手',
            'high': '最高',
            'low': '最低',
            'open': '今开',
            'preClose': '昨收',
            'limitUp': '涨停',
            'limitDown': '跌停',
        }

        for key, name in field_mapping.items():
            result[name] = data.get(key, '-')

        return result
    
    def parse_html_data(self, soup, code):
        """解析HTML格式的股票数据"""
        result = {
            '股票代码': code,
        }
        
        # 这里需要根据实际HTML结构来解析
        # 由于HTML结构可能变化，建议使用API方法
        
        return result
    
    def get_stock_data(self, code, method='api'):
        """
        获取股票数据
        Args:
            code: 股票代码
            method: 获取方法，'api' 或 'html'
        Returns:
            股票数据字典
        """
        if method == 'api':
            return self.get_stock_data_api(code)
        else:
            return self.get_stock_data_html(code)
    
    def print_stock_data(self, stock_data):
        """打印股票数据"""
        if not stock_data:
            print("未获取到股票数据")
            return

        print(f"\n{'='*50}")
        print(f"股票代码: {stock_data.get('股票代码', '-')}")
        print(f"股票名称: {stock_data.get('股票名称', '-')}")
        print(f"{'='*50}")
        print(f"最新: {stock_data.get('最新', '-')}")
        print(f"均价: {stock_data.get('均价', '-')}")
        print(f"涨幅: {stock_data.get('涨幅', '-')}")
        print(f"涨跌: {stock_data.get('涨跌', '-')}")
        print(f"总手: {stock_data.get('总手', '-')}")
        print(f"金额: {stock_data.get('金额', '-')}")
        print(f"换手: {stock_data.get('换手', '-')}")
        print(f"最高: {stock_data.get('最高', '-')}")
        print(f"最低: {stock_data.get('最低', '-')}")
        print(f"今开: {stock_data.get('今开', '-')}")
        print(f"昨收: {stock_data.get('昨收', '-')}")
        print(f"涨停: {stock_data.get('涨停', '-')}")
        print(f"跌停: {stock_data.get('跌停', '-')}")
        print(f"{'='*50}\n")


def main():
    """主函数 - 测试示例"""
    spider = EastMoneyStockSpider()
    
    # 测试获取平安银行(000001)的数据
    print("测试获取股票数据...")
    stock_data = spider.get_stock_data('000001')
    
    if stock_data:
        spider.print_stock_data(stock_data)
        
        # 保存为JSON文件
        with open('stock_data.json', 'w', encoding='utf-8') as f:
            json.dump(stock_data, f, ensure_ascii=False, indent=2)
        print("数据已保存到 stock_data.json")
    else:
        print("获取数据失败")


if __name__ == '__main__':
    main()
