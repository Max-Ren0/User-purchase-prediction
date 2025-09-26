#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推荐系统管道工具函数
提供通用的数据处理和评估功能

主要功能：
- 数据加载和预处理
- 性能评估指标
- 结果保存和可视化
"""

import os
import pandas as pd
import numpy as np
import time
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

def load_data(data_dir='data'):
    """加载所有数据文件"""
    print("📖 加载数据文件...")
    
    data = {}
    files = {
        'train_sorted': 'train_sorted.parquet',
        'train_vis': 'train_vis.parquet', 
        'item_attr': 'item_attr.parquet',
        'test_sorted': 'test_sorted.parquet',
        'label_df': 'label_df.parquet'
    }
    
    for key, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            data[key] = pd.read_parquet(filepath)
            print(f"  ✅ {key}: {data[key].shape}")
        else:
            print(f"  ❌ 缺少文件: {filename}")
            return None
    
    return data

def calculate_metrics(candidates_df, label_df, k=50):
    """计算评估指标"""
    if len(candidates_df) == 0 or len(label_df) == 0:
        return {'hr': 0.0, 'mrr': 0.0, 'ndcg': 0.0}
    
    # 预处理标签
    label_map = {}
    for _, row in label_df.iterrows():
        label_map[row['buyer_admin_id']] = row['label_item']
    
    hr_hits = 0
    mrr_sum = 0.0
    ndcg_sum = 0.0
    total_users = len(label_map)
    
    for user_id, group in candidates_df.groupby('buyer_admin_id'):
        if user_id in label_map:
            user_items = group['item_id'].values[:k]  # 取前k个
            target_item = label_map[user_id]
            
            if target_item in user_items:
                hr_hits += 1
                rank = np.where(user_items == target_item)[0][0] + 1
                mrr_sum += 1.0 / rank
                ndcg_sum += 1.0 / np.log2(rank + 1)
    
    hr = hr_hits / total_users if total_users > 0 else 0.0
    mrr = mrr_sum / total_users if total_users > 0 else 0.0
    ndcg = ndcg_sum / total_users if total_users > 0 else 0.0
    
    return {
        'hr': hr,
        'mrr': mrr,
        'ndcg': ndcg,
        'total_users': total_users,
        'hits': hr_hits
    }

def save_results(results, filename, data_dir='results'):
    """保存结果"""
    os.makedirs(data_dir, exist_ok=True)
    
    if isinstance(results, pd.DataFrame):
        filepath = os.path.join(data_dir, filename)
        results.to_parquet(filepath, index=False, compression='snappy')
        print(f"✅ 保存结果: {filepath}")
    else:
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ 保存结果: {filepath}")

def load_config(config_file='competition_config.json'):
    """加载配置文件"""
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"❌ 配置文件不存在: {config_file}")
        return None

def get_optimized_params(config_file='competition_config.json', mode='production'):
    """获取优化后的参数"""
    config = load_config(config_file)
    if config and 'params' in config:
        return config['params'].get(mode, {})
    else:
        print("❌ 无法加载优化参数，使用默认参数")
        return {
            'covisit_window': 4,
            'covisit_top_per_a': 317,
            'recent_k': 4,
            'cand_per_recent': 69,
            'tau_days': 11,
            'per_cate_pool': 38,
            'per_store_pool': 96,
            'pop_pool': 4863,
            'recall_cap': 866,
            'batch_size': 4000
        }

def print_performance_summary(metrics, title="性能评估"):
    """打印性能摘要"""
    print(f"\n📊 {title}")
    print("=" * 40)
    print(f"HR@50:   {metrics.get('hr', 0):.4f}")
    print(f"MRR@50:  {metrics.get('mrr', 0):.4f}")
    print(f"NDCG@50: {metrics.get('ndcg', 0):.4f}")
    
    if 'total_users' in metrics:
        print(f"总用户数: {metrics['total_users']:,}")
    if 'hits' in metrics:
        print(f"命中数: {metrics['hits']:,}")

def check_data_quality(data):
    """检查数据质量"""
    print("\n🔍 数据质量检查")
    print("=" * 30)
    
    for name, df in data.items():
        print(f"\n📊 {name}:")
        print(f"  形状: {df.shape}")
        print(f"  内存: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB")
        print(f"  缺失值: {df.isnull().sum().sum()}")
        
        if 'buyer_admin_id' in df.columns:
            print(f"  用户数: {df['buyer_admin_id'].nunique():,}")
        if 'item_id' in df.columns:
            print(f"  商品数: {df['item_id'].nunique():,}")

def create_submission(candidates_df, output_file='submission.csv'):
    """创建提交文件"""
    if len(candidates_df) == 0:
        print("❌ 候选数据为空，无法创建提交文件")
        return
    
    # 按用户分组，取前50个候选
    submission = []
    for user_id, group in candidates_df.groupby('buyer_admin_id'):
        user_items = group['item_id'].values[:50]  # 取前50个
        submission.append({
            'buyer_admin_id': user_id,
            'item_id': ' '.join(map(str, user_items))
        })
    
    submission_df = pd.DataFrame(submission)
    submission_df.to_csv(output_file, index=False)
    print(f"✅ 提交文件已创建: {output_file}")
    print(f"📊 提交用户数: {len(submission_df):,}")

def benchmark_performance(func, *args, **kwargs):
    """性能基准测试"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    print(f"⏱️  执行时间: {end_time - start_time:.2f}秒")
    return result

def memory_usage():
    """内存使用情况"""
    import psutil
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"💾 内存使用: {memory_info.rss / 1024 / 1024:.1f}MB")

def setup_logging(log_file='pipeline.log'):
    """设置日志"""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def validate_pipeline():
    """验证管道完整性"""
    print("🔍 验证管道完整性...")
    
    # 检查必要文件
    required_files = [
        'data/Antai_hackathon_train.csv',
        'data/Antai_hackathon_attr.csv',
        'data/dianshang_test.csv',
        'competition_config.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    # 检查Python依赖
    required_packages = [
        'pandas', 'numpy', 'sklearn', 'skopt', 'lightgbm'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少Python包:")
        for package in missing_packages:
            print(f"  - {package}")
        return False
    
    print("✅ 管道验证通过")
    return True

if __name__ == "__main__":
    print("🔧 推荐系统管道工具")
    print("=" * 30)
    
    # 验证管道
    if validate_pipeline():
        print("✅ 系统就绪")
    else:
        print("❌ 系统配置不完整")
