#!/usr/bin/env python3
"""
快速调试修复脚本 - 检查数据列结构
"""

import pandas as pd
import os

def check_data_structure():
    """检查数据结构"""
    print("🔍 检查数据文件结构...")
    
    files_to_check = [
        'x/train_vis.parquet',
        'x/label_df.parquet', 
        'x/item_attr.parquet'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            df = pd.read_parquet(file_path)
            print(f"\n📊 {file_path}:")
            print(f"  形状: {df.shape}")
            print(f"  列名: {list(df.columns)}")
            print(f"  数据类型:")
            for col, dtype in df.dtypes.items():
                print(f"    {col}: {dtype}")
            print(f"  前3行数据:")
            print(df.head(3))
        else:
            print(f"❌ 文件不存在: {file_path}")

def test_covisit_function():
    """测试共现关系函数"""
    print("\n🔄 测试共现关系函数...")
    
    # 加载数据
    train_vis = pd.read_parquet('x/train_vis.parquet')
    
    print(f"训练数据列: {list(train_vis.columns)}")
    
    # 检查关键列
    required_cols = ['buyer_admin_id', 'item_id']
    time_cols = ['irank', 'create_order_time']
    
    missing_required = [col for col in required_cols if col not in train_vis.columns]
    available_time = [col for col in time_cols if col in train_vis.columns]
    
    if missing_required:
        print(f"❌ 缺少必要列: {missing_required}")
        return False
    
    if not available_time:
        print(f"❌ 缺少时间排序列: {time_cols}")
        return False
    
    print(f"✅ 必要列齐全: {required_cols}")
    print(f"✅ 可用时间列: {available_time}")
    
    # 测试排序
    try:
        if 'irank' in train_vis.columns:
            base = train_vis[['buyer_admin_id', 'item_id', 'irank']].sort_values(['buyer_admin_id', 'irank'])
            print("✅ irank排序成功")
        elif 'create_order_time' in train_vis.columns:
            base = train_vis[['buyer_admin_id', 'item_id', 'create_order_time']].sort_values(['buyer_admin_id', 'create_order_time'])
            print("✅ create_order_time排序成功")
        
        print(f"排序后数据形状: {base.shape}")
        return True
        
    except Exception as e:
        print(f"❌ 排序失败: {e}")
        return False

if __name__ == "__main__":
    check_data_structure()
    test_covisit_function()

