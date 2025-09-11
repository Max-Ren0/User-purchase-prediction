#!/usr/bin/env python3
"""
快速测试 - 模拟notebook的数据加载过程
"""

import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
from collections import defaultdict, Counter
import gc
import warnings
warnings.filterwarnings('ignore')

def test_data_loading():
    """测试数据加载过程"""
    print("🚀 测试数据加载过程...")
    
    OUTDIR = 'x'
    
    # 加载数据
    print("📖 正在加载数据...")
    train_vis = pd.read_parquet(f'{OUTDIR}/train_vis.parquet')
    label_df = pd.read_parquet(f'{OUTDIR}/label_df.parquet')
    item_attr = pd.read_parquet(f'{OUTDIR}/item_attr.parquet')
    
    print(f"✅ 数据加载完成")
    print(f"📊 train_vis: {train_vis.shape}, 列: {list(train_vis.columns)}")
    print(f"📊 label_df: {label_df.shape}, 列: {list(label_df.columns)}")
    print(f"📊 item_attr: {item_attr.shape}, 列: {list(item_attr.columns)}")
    
    # 数据类型优化前检查
    print("\n🔍 优化前列检查:")
    for col in ['buyer_admin_id', 'item_id', 'irank']:
        if col in train_vis.columns:
            print(f"  ✅ {col}: {train_vis[col].dtype}")
        else:
            print(f"  ❌ {col}: 列不存在")
    
    # 进行数据类型优化
    print("\n🔧 进行数据类型优化...")
    for df_name, df in [('train_vis', train_vis), ('item_attr', item_attr), ('label_df', label_df)]:
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        # 整数类型优化
        int_columns = ['buyer_admin_id', 'item_id', 'cate_id', 'store_id', 'irank', 'label_item']
        for col in int_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], downcast='integer')
        
        # 字符串类型优化
        str_columns = df.select_dtypes(include=['object']).columns
        for col in str_columns:
            if col not in ['create_order_time']:  # 保留时间列
                df[col] = df[col].astype('category')
        
        optimized_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        reduction = (original_memory - optimized_memory) / original_memory * 100
        print(f"  📊 {df_name}: {original_memory:.1f}MB → {optimized_memory:.1f}MB (减少{reduction:.1f}%)")
    
    # 优化后列检查
    print("\n🔍 优化后列检查:")
    for col in ['buyer_admin_id', 'item_id', 'irank']:
        if col in train_vis.columns:
            print(f"  ✅ {col}: {train_vis[col].dtype}")
        else:
            print(f"  ❌ {col}: 列不存在")
    
    return train_vis, label_df, item_attr

def test_covisit_optimized(df, window=3, topk=200):
    """测试优化版共现关系计算"""
    print(f"\n🔄 测试共现关系计算...")
    print(f"  输入数据形状: {df.shape}")
    print(f"  输入数据列: {list(df.columns)}")
    
    start_time = time.time()
    
    if len(df) == 0:
        return pd.DataFrame(columns=['item_a', 'item_b', 'w'])
    
    # 按用户和时间排序，确保时序正确
    print("  🔄 进行排序...")
    if 'irank' in df.columns:
        base = df[['buyer_admin_id', 'item_id', 'irank']].sort_values(['buyer_admin_id', 'irank'])
        print("  ✅ 使用irank排序")
    elif 'create_order_time' in df.columns:
        base = df[['buyer_admin_id', 'item_id', 'create_order_time']].sort_values(['buyer_admin_id', 'create_order_time'])
        print("  ✅ 使用create_order_time排序")
    else:
        base = df[['buyer_admin_id', 'item_id']].sort_values(['buyer_admin_id'])
        print("  ⚠️  没有找到时间排序列，使用用户ID排序")
    
    print(f"  排序后数据形状: {base.shape}")
    
    # 预计算用户分组信息
    print("  🔄 计算用户分组...")
    user_groups = base.groupby('buyer_admin_id')
    print(f"  用户组数: {len(user_groups)}")
    
    # 测试前100个用户
    print("  🔄 测试前100个用户的共现计算...")
    user_ids = list(user_groups.groups.keys())[:100]
    
    covisit_records = []
    
    for user_id in user_ids:
        user_items = user_groups.get_group(user_id)['item_id'].values
        
        if len(user_items) < 2:
            continue
        
        for lag in range(1, min(window + 1, len(user_items))):
            item_a = user_items[:-lag]
            item_b = user_items[lag:]
            
            for a, b in zip(item_a, item_b):
                if a != b:
                    covisit_records.append((int(a), int(b), 1.0 / lag))
    
    print(f"  生成共现记录数: {len(covisit_records)}")
    
    if covisit_records:
        covisit_df = pd.DataFrame(covisit_records, columns=['item_a', 'item_b', 'w'])
        print(f"  共现DataFrame形状: {covisit_df.shape}")
    
    end_time = time.time()
    print(f"  ✅ 测试完成，耗时: {end_time - start_time:.2f}秒")
    
    return len(covisit_records) > 0

if __name__ == "__main__":
    try:
        # 测试数据加载
        train_vis, label_df, item_attr = test_data_loading()
        
        # 测试共现关系计算
        success = test_covisit_optimized(train_vis)
        
        if success:
            print("\n✅ 所有测试通过！")
        else:
            print("\n❌ 测试失败！")
            
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

