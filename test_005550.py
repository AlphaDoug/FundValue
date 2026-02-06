"""测试005550基金持仓"""
import akshare as ak
from datetime import datetime

fund_code = '005550'
current_year = datetime.now().year

print("=" * 60)
print(f"测试基金 {fund_code} 持仓数据")
print("=" * 60)
print(f"当前年份: {current_year}")
print()

# 尝试不同年份
for year in [str(current_year), str(current_year - 1), str(current_year - 2)]:
    print(f"\n{'=' * 40}")
    print(f"尝试获取 {year} 年持仓数据...")
    print(f"{'=' * 40}")

    try:
        df = ak.fund_portfolio_hold_em(symbol=fund_code, date=year)

        if df is None:
            print(f"返回结果: None")
        elif df.empty:
            print(f"返回结果: 空DataFrame")
            print(f"列名: {df.columns.tolist()}")
        else:
            print(f"[OK] 成功获取 {len(df)} 条持仓记录")
            print(f"列名: {df.columns.tolist()}")
            print(f"\n前5条记录:")
            print(df.head())
            break  # 成功获取数据后退出

    except Exception as e:
        print(f"[FAIL] 失败: {str(e)}")
        import traceback
        traceback.print_exc()
