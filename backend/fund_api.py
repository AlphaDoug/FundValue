"""
使用AkShare获取基金数据的服务
需要安装: pip install akshare
"""
import akshare as ak
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
CORS(app)

# 加载分钟级模拟数据
def load_minute_data():
    """加载股票分钟级涨跌幅数据"""
    try:
        data_file = os.path.join(os.path.dirname(__file__), '..', 'stock_minute_data.json')
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载分钟数据失败: {str(e)}")
        return {}

minute_data_cache = load_minute_data()

def calculate_valuation_at_time(current_time, holdings):
    """计算指定时间的基金估值"""
    time_str = current_time.strftime('%H:%M')
    current_hour = current_time.hour
    current_minute = current_time.minute

    # 跳过11:31-12:59之间的非交易时间
    if time_str > "11:30" and time_str < "13:00":
        return []

    # 判断是否在开盘时间内（包含11:30和15:00作为收盘时刻）
    # 交易时间：9:30-11:30, 13:00-15:00
    is_trading_time = (
        (9 < current_hour < 11) or
        (current_hour == 9 and current_minute >= 30) or
        (current_hour == 11 and current_minute >= 0 and current_minute <= 30) or
        (13 <= current_hour < 15) or
        (current_hour == 15 and current_minute == 0)
    )

    # 计算当前时间的基金估值
    total_market_value = 0
    weighted_change = 0

    for holding in holdings:
        stock_code_simple = holding['stockCode'].replace('.XSHE', '').replace('.XSHG', '').replace('.XBJE', '')
        market_value = holding['marketValue']
        hold_percent = holding['holdPercent']

        # 从分钟数据获取该时间点的价格
        stock_data = minute_data_cache.get(stock_code_simple, {})
        minute_prices = stock_data.get('minute_prices', [])
        open_price = stock_data.get('open_price', stock_data.get('base_price', 100.0))
        base_price = stock_data.get('base_price', open_price)

        current_price = open_price
        current_change = 0
        if minute_prices:
            if is_trading_time:
                # 交易时间内，使用当前时间对应的最新价格
                for price_data in minute_prices:
                    if price_data['time'] <= time_str:
                        current_price = price_data['price']
            else:
                # 不在交易时间（如晚上8点），使用当天15:00的收盘价格
                for price_data in minute_prices:
                    if price_data['time'] <= "15:00":
                        current_price = price_data['price']

        # 计算涨跌幅：
        # 始终使用：(最新价格 - 开盘价) / 开盘价 * 100
        # 最新价格在交易时间内是当前时间价格，非交易时间是15:00收盘价
        if open_price > 0:
            current_change = (current_price - open_price) / open_price * 100

        # 加权计算
        total_market_value += market_value
        weighted_change += market_value * current_change

    if total_market_value > 0:
        estimated_change = weighted_change / total_market_value
        return [{'time': time_str, 'changePercent': round(estimated_change, 2)}]
    return []

# 缓存股票实时行情，避免频繁请求
stock_cache = {}
cache_time = None

def get_stock_market_code(stock_code):
    """将股票代码转换为市场代码"""
    if stock_code.startswith('6') or stock_code.startswith('5'):
        return 'XSHG'
    else:
        return 'XSHE'

def get_cached_stock_prices():
    """获取缓存的股票实时行情"""
    global stock_cache, cache_time

    import time
    current_time = time.time()

    # 缓存5分钟内有效
    if cache_time and (current_time - cache_time) < 300 and stock_cache:
        print(f"使用缓存数据，{len(stock_cache)}只股票")
        return stock_cache

    try:
        print("使用单个股票查询接口获取实时行情...")
        # 使用stock_bid_ask_em接口逐个查询股票
        # 这个接口更稳定，不容易出现代理问题

        # 由于需要逐个查询，这里先返回空，在实际使用时再查询
        stock_cache = {}
        cache_time = current_time
        print("准备实时查询")
        return stock_cache

    except Exception as e:
        print(f"准备股票行情失败: {str(e)}")
        return {}


def get_single_stock_price(stock_code, current_time=None):
    """获取单个股票的实时价格（使用分钟级模拟数据）"""
    try:
        # 去除市场后缀
        code = stock_code.replace('.XSHE', '').replace('.XSHG', '').replace('.XBJE', '')

        # 获取当前时间
        if current_time is None:
            current_time = datetime.now()
        time_str = current_time.strftime('%H:%M')
        current_hour = current_time.hour
        current_minute = current_time.minute

        print(f"查询股票 {code} 在 {time_str} 的行情...")

        # 从分钟数据中获取该时间的价格
        stock_data = minute_data_cache.get(code, {})
        minute_prices = stock_data.get('minute_prices', [])
        open_price = stock_data.get('open_price', stock_data.get('base_price', 50.0))
        base_price = stock_data.get('base_price', open_price)

        # 判断是否在开盘时间内（包含11:30和15:00作为收盘时刻）
        # 交易时间：9:30-11:30, 13:00-15:00
        is_trading_time = (
            (9 < current_hour < 11) or
            (current_hour == 9 and current_minute >= 30) or
            (current_hour == 11 and current_minute >= 0 and current_minute <= 30) or
            (13 <= current_hour < 15) or
            (current_hour == 15 and current_minute == 0)
        )

        # 找到最接近当前时间的价格
        current_price = open_price
        if minute_prices:
            if is_trading_time:
                # 交易时间内，使用当前时间对应的最新价格
                for price_data in minute_prices:
                    if price_data['time'] <= time_str:
                        current_price = price_data['price']
            else:
                # 不在交易时间（如晚上8点），使用当天15:00的收盘价格
                for price_data in minute_prices:
                    if price_data['time'] <= "15:00":
                        current_price = price_data['price']

        # 计算涨跌幅：
        # 始终使用：(最新价格 - 开盘价) / 开盘价 * 100
        # 最新价格在交易时间内是当前时间价格，非交易时间是15:00收盘价
        if open_price > 0:
            change_value = current_price - base_price
            change_percent = (current_price - open_price) / open_price * 100

        # 估算最高价和最低价
        high = max(current_price, open_price) * 1.02
        low = min(current_price, open_price) * 0.98

        result = {
            'code': code,
            'name': stock_data.get('name', code),
            'open': open_price,
            'close': current_price,
            'high': round(high, 2),
            'low': round(low, 2),
            'preClose': base_price,
            'change': round(change_value, 2),
            'changePercent': round(change_percent, 2),
            'volume': 1000000,
            'amount': int(current_price * 1000000)
        }

        print(f"  {code}: 最新={result['close']:.2f} 涨跌幅={result['changePercent']:.2f}% (开盘价={open_price:.2f}, 昨收={base_price:.2f}, 交易中={is_trading_time})")

        return result

    except Exception as e:
        print(f"  查询股票 {code} 失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


@app.route('/api/fund/holdings')
def get_fund_holdings():
    """获取基金持仓数据"""
    try:
        fund_code = request.args.get('fundCode')

        if not fund_code:
            return jsonify({'error': '基金代码不能为空'}), 400

        # 格式化基金代码为6位
        fund_code = fund_code.zfill(6)

        print(f"查询基金持仓: {fund_code}")

        # 获取当前年份和前一年
        current_year = datetime.now().year

        try:
            # 尝试获取当年数据，如果没有则获取前一年数据
            holdings_df = None

            for year in [str(current_year), str(current_year - 1), str(current_year - 2)]:
                print(f"尝试获取 {year} 年持仓数据...")
                try:
                    holdings_df = ak.fund_portfolio_hold_em(symbol=fund_code, date=year)
                    if holdings_df is not None and not holdings_df.empty:
                        print(f"成功获取 {year} 年持仓数据，共 {len(holdings_df)} 条")
                        break
                    else:
                        print(f"{year} 年数据为空")
                except Exception as e:
                    print(f"获取 {year} 年数据失败: {str(e)}")
                    continue

            # 检查是否获取到数据
            if holdings_df is None or holdings_df.empty:
                print(f"基金 {fund_code} 暂无持仓数据")
                return jsonify({
                    'fundCode': fund_code,
                    'holdings': []
                })

            print(f"获取到 {len(holdings_df)} 条持仓记录")
            print(holdings_df.head())

            # 获取最新一期和上一期的季度数据
            latest_quarter_holdings = None
            previous_quarter_holdings = None

            if '季度' in holdings_df.columns:
                # 获取所有季度并排序
                quarters = sorted(holdings_df['季度'].unique())
                print(f"共 {len(quarters)} 个季度的数据: {quarters}")

                # 找出最新的季度和上一季度
                if len(quarters) > 0:
                    latest_quarter = quarters[-1]
                    print(f"最新季度: {latest_quarter}")
                    latest_quarter_holdings = holdings_df[holdings_df['季度'] == latest_quarter].copy()
                    print(f"最新季度持仓数量: {len(latest_quarter_holdings)}")

                if len(quarters) > 1:
                    previous_quarter = quarters[-2]
                    print(f"上一季度: {previous_quarter}")
                    previous_quarter_holdings = holdings_df[holdings_df['季度'] == previous_quarter].copy()
                    print(f"上一季度持仓数量: {len(previous_quarter_holdings)}")

            # 如果没有最新季度数据，使用全部数据
            if latest_quarter_holdings is None:
                latest_quarter_holdings = holdings_df

            # 创建上一季度的持仓占比字典（股票代码 -> 占净值比例）
            prev_hold_percent_map = {}
            if previous_quarter_holdings is not None:
                for _, row in previous_quarter_holdings.iterrows():
                    stock_code = str(row['股票代码']).zfill(6)
                    prev_hold_percent_map[stock_code] = row['占净值比例'] if pd.notna(row['占净值比例']) else 0

            # 转换为API需要的格式
            holdings = []
            for _, row in latest_quarter_holdings.iterrows():
                stock_code = str(row['股票代码']).zfill(6)
                market = get_stock_market_code(stock_code)
                full_code = f"{stock_code}.{market}"

                current_hold_percent = row['占净值比例'] if pd.notna(row['占净值比例']) else 0
                prev_hold_percent = prev_hold_percent_map.get(stock_code, 0)

                # 计算变化和是否新增
                hold_percent_change = current_hold_percent - prev_hold_percent
                is_new = stock_code not in prev_hold_percent_map

                holdings.append({
                    'stockCode': full_code,
                    'stockName': row['股票名称'],
                    'shares': row['持股数'] if pd.notna(row['持股数']) else 0,
                    'costPrice': 0,  # AkShare不提供成本价，需要计算
                    'holdPercent': current_hold_percent,
                    'marketValue': row['持仓市值'] if pd.notna(row['持仓市值']) else 0,
                    'quarter': row['季度'] if '季度' in row else '',
                    'prevHoldPercent': prev_hold_percent,
                    'holdPercentChange': hold_percent_change,
                    'isNew': is_new
                })

            print(f"转换后的持仓数据: {len(holdings)} 条")
            return jsonify({
                'fundCode': fund_code,
                'holdings': holdings
            })

        except Exception as e:
            print(f"AkShare获取持仓失败: {str(e)}")
            return jsonify({'error': f'获取基金持仓失败: {str(e)}'}), 500

    except Exception as e:
        print(f"获取基金持仓失败: {str(e)}")
        return jsonify({'error': f'获取基金持仓失败: {str(e)}'}), 500


@app.route('/api/stock/prices', methods=['POST'])
def get_stock_prices():
    """获取股票实时价格"""
    try:
        data = request.get_json()
        codes = data.get('codes', [])

        if not codes or not isinstance(codes, list):
            return jsonify({'error': '股票代码列表不能为空'}), 400

        print(f"查询股票价格: {codes}")

        prices = {}

        for code in codes:
            # 解析股票代码（去除.XSHG或.XSHE后缀）
            stock_code = code.replace('.XSHG', '').replace('.XSHE', '')

            # 首先尝试使用单个股票接口查询
            stock_data = get_single_stock_price(code)

            if stock_data:
                prices[code] = {
                    'open': stock_data['open'],
                    'close': stock_data['close'],
                    'high': stock_data['high'],
                    'low': stock_data['low'],
                    'preClose': stock_data['preClose'],
                    'changePercent': stock_data['changePercent'],
                    'change': stock_data['change'],
                    'volume': stock_data['volume'],
                    'amount': stock_data['amount'],
                    'pe': 0,  # stock_bid_ask_em不提供
                    'pb': 0   # stock_bid_ask_em不提供
                }
            else:
                # 未找到该股票，返回默认值
                print(f"  {code}: 未找到数据，使用默认值")
                prices[code] = {
                    'open': 0.0,
                    'close': 0.0,
                    'high': 0.0,
                    'low': 0.0,
                    'preClose': 0.0,
                    'changePercent': 0.0,
                    'change': 0.0,
                    'volume': 0,
                    'amount': 0,
                    'pe': 0,
                    'pb': 0
                }

        return jsonify(prices)

    except Exception as e:
        print(f"获取股票价格失败: {str(e)}")
        return jsonify({'error': f'获取股票价格失败: {str(e)}'}), 500


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/fund/valuation-history')
def get_fund_valuation_history():
    """获取基金估值历史走势（从开盘到当前）"""
    try:
        fund_code = request.args.get('fundCode')

        if not fund_code:
            return jsonify({'error': '基金代码不能为空'}), 400

        # 格式化基金代码为6位
        fund_code = fund_code.zfill(6)

        print(f"查询基金估值历史: {fund_code}")

        # 先获取持仓数据
        holdings_result = None
        current_year = datetime.now().year

        for year in [str(current_year), str(current_year - 1), str(current_year - 2)]:
            try:
                holdings_df = ak.fund_portfolio_hold_em(symbol=fund_code, date=year)
                if holdings_df is not None and not holdings_df.empty:
                    # 获取最新季度数据
                    if '季度' in holdings_df.columns:
                        quarters = sorted(holdings_df['季度'].unique())
                        if len(quarters) > 0:
                            latest_quarter = quarters[-1]
                            holdings_df = holdings_df[holdings_df['季度'] == latest_quarter]
                    holdings_result = holdings_df
                    break
            except Exception as e:
                print(f"获取 {year} 年数据失败: {str(e)}")
                continue

        if holdings_result is None or holdings_result.empty:
            return jsonify({'error': '暂无持仓数据'}), 400

        # 解析持仓
        holdings = []
        for _, row in holdings_result.iterrows():
            stock_code = str(row['股票代码']).zfill(6)
            market = get_stock_market_code(stock_code)
            full_code = f"{stock_code}.{market}"

            holdings.append({
                'stockCode': full_code,
                'stockName': row['股票名称'],
                'marketValue': row['持仓市值'] if pd.notna(row['持仓市值']) else 0,
                'holdPercent': row['占净值比例'] if pd.notna(row['占净值比例']) else 0
            })

        # 判断当前是否在开盘时间内
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute

        # 开盘时间判断：
        # 上午：9:30-11:30
        # 下午：13:00-15:00
        is_trading_time = (
            (9 < current_hour < 11) or
            (current_hour == 9 and current_minute >= 30) or
            (current_hour == 11 and current_minute < 30) or
            (13 <= current_hour < 15)
        )

        # 判断当前是上午还是下午
        is_morning_session = (current_hour < 12)

        # 如果不在开盘时间，显示当天完整的走势（上午+下午）
        if not is_trading_time:
            print(f"当前不在开盘时间 ({now.strftime('%H:%M')})，显示全天完整走势")
            # 生成上午9:30-11:30和下午13:00-15:00的所有时间点
            valuation_history = []
            start_time_morning = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
            end_time_morning = datetime.now().replace(hour=11, minute=30, second=0, microsecond=0)
            start_time_afternoon = datetime.now().replace(hour=13, minute=0, second=0, microsecond=0)
            end_time_afternoon = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)

            # 生成上午数据
            current_time = start_time_morning
            while current_time <= end_time_morning:
                valuation_history.extend(calculate_valuation_at_time(current_time, holdings))
                current_time = current_time + timedelta(minutes=1)

            # 生成下午数据
            current_time = start_time_afternoon
            while current_time <= end_time_afternoon:
                valuation_history.extend(calculate_valuation_at_time(current_time, holdings))
                current_time = current_time + timedelta(minutes=1)
        else:
            # 在开盘时间内，显示从开盘到现在的走势
            print(f"当前在开盘时间 ({now.strftime('%H:%M')})，显示从开盘到现在的走势")
            start_time = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
            end_time = now

            valuation_history = []
            current_time = start_time
            while current_time <= end_time:
                valuation_history.extend(calculate_valuation_at_time(current_time, holdings))
                current_time = current_time + timedelta(minutes=1)

        return jsonify({
            'fundCode': fund_code,
            'valuationHistory': valuation_history
        })

    except Exception as e:
        print(f"获取估值历史失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取估值历史失败: {str(e)}'}), 500


@app.route('/api/test/005550')
def test_fund_005550():
    """测试接口：返回005550基金的完整数据"""
    test_data = {
        'fundCode': '005550',
        'fundName': '金信稳健策略灵活配置',
        'holdings': [
            {
                'stockCode': '300394.XSHE',
                'stockName': '天孚通信',
                'shares': 620000,
                'costPrice': 151.00,
                'holdPercent': 8.90,
                'marketValue': 93620000
            },
            {
                'stockCode': '300308.XSHE',
                'stockName': '中际旭创',
                'shares': 550000,
                'costPrice': 156.50,
                'holdPercent': 8.17,
                'marketValue': 86110000
            },
            {
                'stockCode': '002463.XSHE',
                'stockName': '沪电股份',
                'shares': 2840000,
                'costPrice': 30.15,
                'holdPercent': 8.14,
                'marketValue': 85626000
            },
            {
                'stockCode': '002371.XSHE',
                'stockName': '北方华创',
                'shares': 270000,
                'costPrice': 305.20,
                'holdPercent': 7.83,
                'marketValue': 82404000
            },
            {
                'stockCode': '300476.XSHE',
                'stockName': '胜宏科技',
                'shares': 2350000,
                'costPrice': 24.25,
                'holdPercent': 5.40,
                'marketValue': 56917500
            }
        ],
        'summary': {
            'totalHoldings': 75,
            'top5Holdings': 5,
            'totalMarketValue': 404577000
        }
    }
    return jsonify(test_data)


@app.route('/api/fund/name', methods=['GET'])
def get_fund_name():
    """获取基金名称"""
    fund_code = request.args.get('fundCode')
    if not fund_code:
        return jsonify({'error': '缺少基金代码'}), 400

    try:
        print(f"查询基金名称: {fund_code}")
        fund_info = ak.fund_individual_basic_info_xq(symbol=fund_code)
        
        if fund_info is None or fund_info.empty:
            return jsonify({'error': '未找到基金信息'}), 404
        
        # 打印列名用于调试
        print(f"返回的列名: {fund_info.columns.tolist()}")
        print(f"返回的数据:\n{fund_info}")
        
        # 获取基金名称
        # DataFrame是转置格式，包含item和value两列
        fund_name = ''
        
        # 方法1：从item列查找"基金名称"对应的value
        if 'item' in fund_info.columns and 'value' in fund_info.columns:
            fund_name_row = fund_info[fund_info['item'] == '基金名称']
            if not fund_name_row.empty:
                fund_name = fund_name_row.iloc[0]['value']
        
        # 方法2：直接从原始JSON获取（如果有access）
        if not fund_name and hasattr(fund_info, '_data'):
            # 尝试其他获取方式
            pass
        
        print(f"基金名称: {fund_name}")
        return jsonify({
            'fundCode': fund_code,
            'fundName': fund_name
        })
    except Exception as e:
        print(f"获取基金名称失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("启动基金API服务...")
    print("=" * 50)
    print("服务地址: http://127.0.0.1:8001")
    print("API文档: 请查看 backend/README.md")
    print("=" * 50)
    app.run(host='127.0.0.1', port=8001, debug=True)
