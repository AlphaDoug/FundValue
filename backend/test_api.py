"""测试API接口"""
import akshare as ak
import pandas as pd
from datetime import datetime

print("=" * 60)
print("测试基金持仓API")
print("=" * 60)

fund_code = "005550"
current_year = datetime.now().year

print(f"\n基金代码: {fund_code}")
print(f"查询年份: {current_year}")

try:
    holdings_df = ak.fund_portfolio_hold_em(symbol=fund_code, date=str(current_year))
    print(f"\n成功获取 {len(holdings_df)} 条持仓记录")
    print("\n前5条记录:")
    print(holdings_df.head())
    print("\n列名:", holdings_df.columns.tolist())

except Exception as e:
    print(f"\n获取失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试股票行情API")
print("=" * 60)

try:
    stock_df = ak.stock_zh_a_spot_em()
    print(f"\n成功获取 {len(stock_df)} 只股票数据")
    print("\n前5条记录:")
    print(stock_df[['代码', '名称', '最新价', '涨跌幅']].head())

except Exception as e:
    print(f"\n获取失败: {str(e)}")
    import traceback
    traceback.print_exc()
