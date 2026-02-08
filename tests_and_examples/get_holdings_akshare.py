#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用akshare获取基金持仓数据
"""
import akshare as ak
import json
import sys

def get_fund_holdings(fund_code):
    """获取基金持仓"""
    try:
        print(f"正在获取基金 {fund_code} 的持仓数据...")
        
        # 使用akshare获取基金持仓
        # 方法1: 基金持仓 - 季报持仓
        try:
            df = ak.fund_portfolio_hold_em(fund=fund_code, symbol="A股持仓")
            print(f"获取到持仓数据，行数: {len(df)}")
            
            if len(df) > 0:
                holdings = []
                for _, row in df.iterrows():
                    holding = {
                        'stockCode': str(row.get('股票代码', '')),
                        'stockName': row.get('股票名称', ''),
                        'shares': int(row.get('持有数量', 0) or 0),
                        'marketValue': float(row.get('持仓市值', 0) or 0),
                        'holdPercent': float(row.get('占净值比', 0) or 0),
                        'isNew': False,
                        'holdPercentChange': 0
                    }
                    holdings.append(holding)
                
                print(f"成功解析 {len(holdings)} 条持仓")
                if len(holdings) > 0:
                    print("第一条持仓:", json.dumps(holdings[0], ensure_ascii=False, indent=2))
                
                return holdings
        except Exception as e:
            print(f"方法1失败: {e}")
        
        # 方法2: 尝试其他API
        try:
            df = ak.fund_em_hold_detail(fund=fund_code)
            print(f"方法2获取到持仓数据，行数: {len(df)}")
            
            if len(df) > 0:
                holdings = []
                for _, row in df.iterrows():
                    holding = {
                        'stockCode': str(row.get('股票代码', '')),
                        'stockName': row.get('股票名称', ''),
                        'shares': int(row.get('持有数量', 0) or 0),
                        'marketValue': float(row.get('持仓市值', 0) or 0),
                        'holdPercent': float(row.get('占净值比', 0) or 0),
                        'isNew': False,
                        'holdPercentChange': 0
                    }
                    holdings.append(holding)
                
                print(f"成功解析 {len(holdings)} 条持仓")
                return holdings
        except Exception as e:
            print(f"方法2失败: {e}")
        
        return []
        
    except Exception as e:
        print(f"获取持仓失败: {e}")
        return []

if __name__ == '__main__':
    fund_code = sys.argv[1] if len(sys.argv) > 1 else '000001'
    holdings = get_fund_holdings(fund_code)
    print(f"\n最终结果: {len(holdings)} 条持仓")
    print(json.dumps(holdings, ensure_ascii=False, indent=2))
