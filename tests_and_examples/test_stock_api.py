"""
测试股票信息API接口
测试股票实时行情接口是否正常工作
"""
import requests
import json
from datetime import datetime

# API基础地址
BASE_URL = 'http://localhost:8000'

def test_health():
    """测试健康检查接口"""
    print("=" * 60)
    print("测试健康检查接口")
    print("=" * 60)
    try:
        response = requests.get(f'{BASE_URL}/api/health')
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print("✓ 健康检查通过\n")
        return True
    except Exception as e:
        print(f"✗ 健康检查失败: {str(e)}\n")
        return False

def test_fund_holdings(fund_code='005550'):
    """测试获取基金持仓接口"""
    print("=" * 60)
    print(f"测试获取基金持仓接口: {fund_code}")
    print("=" * 60)
    try:
        response = requests.get(f'{BASE_URL}/api/fund/holdings', params={'fundCode': fund_code})
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"基金代码: {data.get('fundCode', 'N/A')}")
        print(f"持仓数量: {len(data.get('holdings', []))}")

        if data.get('holdings'):
            print("\n前3个持仓:")
            for i, holding in enumerate(data['holdings'][:3], 1):
                print(f"  {i}. {holding['stockName']} ({holding['stockCode']})")
                print(f"     占比: {holding.get('holdPercent', 'N/A')}%")
                print(f"     上一期占比: {holding.get('prevHoldPercent', 'N/A')}%")
                print(f"     变化: {holding.get('holdPercentChange', 'N/A')}%")
                print(f"     是否新增: {'是' if holding.get('isNew') else '否'}")
        print("✓ 基金持仓接口正常\n")
        return data.get('holdings', [])
    except Exception as e:
        print(f"✗ 基金持仓接口失败: {str(e)}\n")
        return []

def test_stock_prices(stock_codes):
    """测试获取股票价格接口"""
    print("=" * 60)
    print(f"测试获取股票价格接口")
    print("=" * 60)
    print(f"测试股票数量: {len(stock_codes)}")

    try:
        response = requests.post(
            f'{BASE_URL}/api/stock/prices',
            json={'codes': stock_codes},
            headers={'Content-Type': 'application/json'}
        )
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"返回价格数量: {len(data)}")

        if data:
            print("\n前3个股票价格:")
            for i, (code, price) in enumerate(list(data.items())[:3], 1):
                print(f"  {i}. {code}")
                print(f"     最新价: {price.get('close', 'N/A')}")
                print(f"     涨跌幅: {price.get('changePercent', 'N/A')}%")
                print(f"     涨跌额: {price.get('change', 'N/A')}")

        print("✓ 股票价格接口正常\n")
        return data
    except Exception as e:
        print(f"✗ 股票价格接口失败: {str(e)}\n")
        return {}

def test_single_stock_price(stock_code):
    """测试单个股票查询"""
    print("=" * 60)
    print(f"测试单个股票查询: {stock_code}")
    print("=" * 60)
    try:
        import akshare as ak
        df = ak.stock_bid_ask_em(symbol=stock_code)
        if df.empty:
            print(f"✗ 股票 {stock_code} 无数据")
            return None

        price_dict = {row['item']: row['value'] for _, row in df.iterrows()}

        print(f"最新价: {price_dict.get('最新', 'N/A')}")
        print(f"涨跌幅: {price_dict.get('涨幅', 'N/A')}%")
        print(f"涨跌额: {price_dict.get('涨跌', 'N/A')}")
        print(f"今开: {price_dict.get('今开', 'N/A')}")
        print(f"昨收: {price_dict.get('昨收', 'N/A')}")
        print(f"最高: {price_dict.get('最高', 'N/A')}")
        print(f"最低: {price_dict.get('最低', 'N/A')}")

        print("✓ 单个股票查询正常\n")
        return price_dict
    except Exception as e:
        print(f"✗ 单个股票查询失败: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("股票信息API接口测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")

    # 1. 测试健康检查
    if not test_health():
        print("⚠ 后端服务未启动，请先运行: python backend/fund_api.py")
        return

    # 2. 测试基金持仓
    holdings = test_fund_holdings('005550')

    if not holdings:
        print("⚠ 未获取到基金持仓数据，跳过股票价格测试")
        return

    # 3. 测试股票价格
    stock_codes = [h['stockCode'] for h in holdings[:5]]  # 只测试前5个股票
    prices = test_stock_prices(stock_codes)

    # 4. 测试单个股票查询（使用第一个股票代码）
    if stock_codes:
        first_stock = stock_codes[0].replace('.XSHG', '').replace('.XSHE', '')
        test_single_stock_price(first_stock)

    # 5. 汇总测试结果
    print("=" * 60)
    print("测试汇总")
    print("=" * 60)
    print(f"✓ 健康检查: 通过")
    print(f"✓ 基金持仓: 获取到 {len(holdings)} 条数据")
    print(f"✓ 股票价格: 获取到 {len(prices)} 条数据")
    print("\n所有测试完成！\n")

if __name__ == '__main__':
    main()
