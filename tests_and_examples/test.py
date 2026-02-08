import akshare as ak
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime


# 格式化基金代码为6位
fund_code = "005550"

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

    print(f"获取到 {len(holdings_df)} 条持仓记录")
    print(holdings_df.head(5000))

    # 转换为API需要的格式
    holdings = []
    for _, row in holdings_df.iterrows():
        stock_code = str(row['股票代码']).zfill(6)
        market = get_stock_market_code(stock_code)
        full_code = f"{stock_code}.{market}"

        holdings.append({
            'stockCode': full_code,
            'stockName': row['股票名称'],
            'shares': row['持股数量'] if pd.notna(row['持股数量']) else 0,
            'costPrice': 0,  # AkShare不提供成本价，需要计算
            'holdPercent': row['占净值比例'] if pd.notna(row['占净值比例']) else 0,
            'marketValue': row['持仓市值'] if pd.notna(row['持仓市值']) else 0,
            'quarter': row['季度'] if '季度' in row else ''
        })

    print(f"转换后的持仓数据: {len(holdings)} 条")

except Exception as e:
    print(f"AkShare获取持仓失败: {str(e)}")
    # 返回模拟数据作为fallback
    print("使用模拟数据")
    mock_holdings = {
        '000001': [
            {'stockCode': '000001.XSHE', 'stockName': '平安银行', 'shares': 10000, 'costPrice': 12.50, 'holdPercent': 8.5},
            {'stockCode': '000002.XSHE', 'stockName': '万科A', 'shares': 5000, 'costPrice': 25.80, 'holdPercent': 5.2},
            {'stockCode': '600000.XSHG', 'stockName': '浦发银行', 'shares': 8000, 'costPrice': 8.90, 'holdPercent': 6.8}
        ],
        '000002': [
            {'stockCode': '600036.XSHG', 'stockName': '招商银行', 'shares': 15000, 'costPrice': 35.20, 'holdPercent': 9.2},
            {'stockCode': '000858.XSHE', 'stockName': '五粮液', 'shares': 3000, 'costPrice': 180.50, 'holdPercent': 10.5}
        ]
    }

    holdings = mock_holdings.get(fund_code, [])