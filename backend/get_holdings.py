#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通过命令行获取基金持仓数据
"""
import sys
import json
import pandas as pd
import akshare as ak
from datetime import datetime
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_fund_holdings(fund_code):
    """获取基金持仓数据"""
    try:
        # 获取当前年份
        current_year = datetime.now().year
        
        # 尝试获取当年和前几年的数据
        for year in [str(current_year), str(current_year - 1), str(current_year - 2)]:
            try:
                df = ak.fund_portfolio_hold_em(symbol=fund_code, date=year)
                if df is not None and not df.empty:
                    # 获取最新季度数据和上一季度数据
                    latest_quarter_holdings = None
                    previous_quarter_holdings = None
                    
                    if '季度' in df.columns:
                        # 获取所有季度并排序
                        quarters = sorted(df['季度'].unique())
                        
                        # 找出最新的季度和上一季度
                        if len(quarters) > 0:
                            latest_quarter = quarters[-1]
                            latest_quarter_holdings = df[df['季度'] == latest_quarter].copy()
                        
                        if len(quarters) > 1:
                            previous_quarter = quarters[-2]
                            previous_quarter_holdings = df[df['季度'] == previous_quarter].copy()
                    
                    # 如果没有最新季度数据，使用全部数据
                    if latest_quarter_holdings is None:
                        latest_quarter_holdings = df
                    
                    # 创建上一季度的持仓占比字典（股票代码 -> 占净值比例）
                    prev_hold_percent_map = {}
                    if previous_quarter_holdings is not None:
                        for _, row in previous_quarter_holdings.iterrows():
                            stock_code = str(row['股票代码']).zfill(6)
                            prev_hold_percent_map[stock_code] = row['占净值比例'] if pd.notna(row['占净值比例']) else 0
                    
                    # 转换为JSON格式
                    holdings = []
                    for _, row in latest_quarter_holdings.iterrows():
                        stock_code = str(row['股票代码']).zfill(6)
                        
                        # 判断市场
                        if stock_code.startswith('6'):
                            market = 'XSHG'
                        else:
                            market = 'XSHE'
                        
                        current_hold_percent = row['占净值比例'] if pd.notna(row['占净值比例']) else 0
                        prev_hold_percent = prev_hold_percent_map.get(stock_code, 0)
                        
                        # 计算变化和是否新增
                        hold_percent_change = current_hold_percent - prev_hold_percent
                        is_new = stock_code not in prev_hold_percent_map
                        
                        holdings.append({
                            'stockCode': f"{stock_code}.{market}",
                            'stockName': row['股票名称'],
                            'shares': float(row['持股数']) if pd.notna(row['持股数']) else 0,
                            'marketValue': float(row['持仓市值']) if pd.notna(row['持仓市值']) else 0,
                            'holdPercent': current_hold_percent,
                            'quarter': row['季度'] if '季度' in row else '',
                            'prevHoldPercent': prev_hold_percent,
                            'holdPercentChange': hold_percent_change,
                            'isNew': is_new
                        })
                    
                    return {
                        'success': True,
                        'fundCode': fund_code,
                        'holdings': holdings
                    }
            except Exception as e:
                continue
        
        # 如果所有年份都失败
        return {
            'success': True,
            'fundCode': fund_code,
            'holdings': []
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': '缺少基金代码'}))
        sys.exit(1)
    
    fund_code = sys.argv[1].zfill(6)
    result = get_fund_holdings(fund_code)
    # 输出JSON，确保不使用ASCII转义，只输出JSON不要有任何其他输出
    print(json.dumps(result, ensure_ascii=False))
