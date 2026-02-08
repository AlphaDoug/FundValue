#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试akshare基金持仓API
"""
import akshare as ak
import inspect

# 查找基金相关的函数
fund_functions = [name for name in dir(ak) if 'fund' in name.lower() and 'hold' in name.lower()]

print("akshare中包含fund和hold的函数:")
for func_name in fund_functions:
    func = getattr(ak, func_name)
    try:
        sig = inspect.signature(func)
        print(f"\n{func_name}{sig}")
    except:
        print(f"\n{func_name}")

# 测试一个具体的函数
print("\n\n测试fund_portfolio_hold_em函数:")
try:
    df = ak.fund_portfolio_hold_em(symbol="A股持仓")
    print(f"成功获取数据，列名: {list(df.columns)}")
    print(f"数据行数: {len(df)}")
    if len(df) > 0:
        print("第一行数据:")
        print(df.iloc[0])
except Exception as e:
    print(f"错误: {e}")
