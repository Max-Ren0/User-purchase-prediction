#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
留一验证评估函数
专门为推荐系统设计的科学评估方法

核心特点：
1. 严格的留一验证：每个用户只保留最后一次购买作为标签
2. 时序切分：确保训练和测试数据在时间上不重叠
3. 多指标评估：HR@K, MRR@K, NDCG@K
4. 高效计算：向量化实现，支持大规模数据
"""

import pandas as pd
import numpy as np
import math
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

def calculate_hr_at_k(candidates_df: pd.DataFrame, 
                     label_df: pd.DataFrame, 
                     k: int = 50) -> float:
    """
    计算Hit Rate@K (命中率)
    
    Args:
        candidates_df: 候选商品DataFrame，包含buyer_admin_id, item_id, pred
        label_df: 标签DataFrame，包含buyer_admin_id, label_item
        k: Top-K数量
    
    Returns:
        float: HR@K值
    """
    if len(candidates_df) == 0 or len(label_df) == 0:
        return 0.0
    
    # 创建标签映射
    label_map = label_df.set_index('buyer_admin_id')['label_item'].to_dict()
    
    hits = 0
    total_users = 0
    
    for user_id, group in candidates_df.groupby('buyer_admin_id'):
        if user_id in label_map:
            total_users += 1
            target_item = label_map[user_id]
            
            # 按预测分数排序，取前k个
            top_k_items = group.nlargest(k, 'pred')['item_id'].values
            
            # 检查目标商品是否在前k个中
            if target_item in top_k_items:
                hits += 1
    
    return hits / total_users if total_users > 0 else 0.0

def calculate_mrr_at_k(candidates_df: pd.DataFrame, 
                      label_df: pd.DataFrame, 
                      k: int = 50) -> float:
    """
    计算Mean Reciprocal Rank@K (平均倒数排名)
    
    Args:
        candidates_df: 候选商品DataFrame，包含buyer_admin_id, item_id, pred
        label_df: 标签DataFrame，包含buyer_admin_id, label_item
        k: Top-K数量
    
    Returns:
        float: MRR@K值
    """
    if len(candidates_df) == 0 or len(label_df) == 0:
        return 0.0
    
    # 创建标签映射
    label_map = label_df.set_index('buyer_admin_id')['label_item'].to_dict()
    
    mrr_sum = 0.0
    total_users = 0
    
    for user_id, group in candidates_df.groupby('buyer_admin_id'):
        if user_id in label_map:
            total_users += 1
            target_item = label_map[user_id]
            
            # 按预测分数排序，取前k个
            top_k_items = group.nlargest(k, 'pred')['item_id'].values
            
            # 找到目标商品的排名
            for rank, item_id in enumerate(top_k_items, 1):
                if item_id == target_item:
                    mrr_sum += 1.0 / rank
                    break
    
    return mrr_sum / total_users if total_users > 0 else 0.0

def calculate_ndcg_at_k(candidates_df: pd.DataFrame, 
                       label_df: pd.DataFrame, 
                       k: int = 50) -> float:
    """
    计算Normalized Discounted Cumulative Gain@K
    
    Args:
        candidates_df: 候选商品DataFrame，包含buyer_admin_id, item_id, pred
        label_df: 标签DataFrame，包含buyer_admin_id, label_item
        k: Top-K数量
    
    Returns:
        float: NDCG@K值
    """
    if len(candidates_df) == 0 or len(label_df) == 0:
        return 0.0
    
    # 创建标签映射
    label_map = label_df.set_index('buyer_admin_id')['label_item'].to_dict()
    
    ndcg_sum = 0.0
    total_users = 0
    
    for user_id, group in candidates_df.groupby('buyer_admin_id'):
        if user_id in label_map:
            total_users += 1
            target_item = label_map[user_id]
            
            # 按预测分数排序，取前k个
            top_k_items = group.nlargest(k, 'pred')['item_id'].values
            
            # 计算DCG
            dcg = 0.0
            for rank, item_id in enumerate(top_k_items, 1):
                if item_id == target_item:
                    dcg += 1.0 / math.log2(rank + 1)
                    break
            
            # 计算IDCG (理想情况下为1.0，因为只有一个相关物品)
            idcg = 1.0
            
            # 计算NDCG
            ndcg_sum += dcg / idcg if idcg > 0 else 0.0
    
    return ndcg_sum / total_users if total_users > 0 else 0.0

def evaluate_recommendations(candidates_df: pd.DataFrame, 
                           label_df: pd.DataFrame, 
                           k_values: List[int] = [10, 20, 50]) -> Dict[str, Any]:
    """
    综合评估推荐结果
    
    Args:
        candidates_df: 候选商品DataFrame
        label_df: 标签DataFrame
        k_values: 评估的K值列表
    
    Returns:
        Dict: 包含各种指标的评估结果
    """
    print("📊 开始综合评估...")
    
    results = {}
    
    for k in k_values:
        print(f"  🔍 计算K={k}的指标...")
        
        hr = calculate_hr_at_k(candidates_df, label_df, k)
        mrr = calculate_mrr_at_k(candidates_df, label_df, k)
        ndcg = calculate_ndcg_at_k(candidates_df, label_df, k)
        
        results[f'hr{k}'] = hr
        results[f'mrr{k}'] = mrr
        results[f'ndcg{k}'] = ndcg
        
        print(f"    HR@{k}: {hr:.4f}")
        print(f"    MRR@{k}: {mrr:.4f}")
        print(f"    NDCG@{k}: {ndcg:.4f}")
    
    # 计算综合评分
    hr50 = results.get('hr50', 0.0)
    mrr50 = results.get('mrr50', 0.0)
    ndcg50 = results.get('ndcg50', 0.0)
    
    # 综合评分权重：HR@50权重最高
    results['total_score'] = 0.6 * hr50 + 0.25 * mrr50 + 0.15 * ndcg50
    
    # 添加基础统计
    results['total_users'] = label_df['buyer_admin_id'].nunique()
    results['total_candidates'] = len(candidates_df)
    results['avg_candidates_per_user'] = len(candidates_df) / label_df['buyer_admin_id'].nunique()
    
    print(f"✅ 评估完成!")
    print(f"📊 综合评分: {results['total_score']:.4f}")
    print(f"👥 评估用户数: {results['total_users']:,}")
    print(f"🎯 候选商品数: {results['total_candidates']:,}")
    
    return results

def validate_leave_one_out_setup(train_df: pd.DataFrame, 
                                label_df: pd.DataFrame) -> bool:
    """
    验证留一验证设置是否正确
    
    Args:
        train_df: 训练数据
        label_df: 标签数据
    
    Returns:
        bool: 设置是否正确
    """
    print("🔍 验证留一验证设置...")
    
    # 检查1：标签用户是否都在训练数据中
    train_users = set(train_df['buyer_admin_id'].unique())
    label_users = set(label_df['buyer_admin_id'].unique())
    
    if not label_users.issubset(train_users):
        print("❌ 错误：标签用户不在训练数据中")
        return False
    
    # 检查2：标签商品是否在训练数据中出现过（抽样场景下放宽检查）
    train_items = set(train_df['item_id'].unique())
    label_items = set(label_df['label_item'].unique())
    
    common_items = train_items & label_items
    missing_items = label_items - train_items
    
    if len(common_items) == 0:
        print("❌ 错误：没有任何标签商品在训练数据中")
        return False
    
    if len(missing_items) > 0:
        missing_rate = len(missing_items) / len(label_items) * 100
        print(f"⚠️  警告：{len(missing_items)} 个标签商品不在训练数据中 ({missing_rate:.1f}%)")
        print("   这在抽样场景下是正常的，因为抽样只选择了部分用户")
        print(f"   共同商品数: {len(common_items):,} 个")
    
    # 检查3：每个用户只有一个标签
    user_label_counts = label_df['buyer_admin_id'].value_counts()
    if (user_label_counts > 1).any():
        print("❌ 错误：存在用户有多个标签")
        return False
    
    # 检查4：标签时间应该在训练数据之后
    if 'create_order_time' in train_df.columns and 'create_order_time' in label_df.columns:
        train_df['create_order_time'] = pd.to_datetime(train_df['create_order_time'])
        label_df['create_order_time'] = pd.to_datetime(label_df['create_order_time'])
        
        for user_id in label_df['buyer_admin_id'].unique():
            user_train_max = train_df[train_df['buyer_admin_id'] == user_id]['create_order_time'].max()
            user_label_time = label_df[label_df['buyer_admin_id'] == user_id]['create_order_time'].iloc[0]
            
            if user_label_time <= user_train_max:
                print(f"❌ 错误：用户{user_id}的标签时间不在训练数据之后")
                return False
    
    print("✅ 留一验证设置正确")
    return True

def create_evaluation_report(results: Dict[str, Any], 
                           model_name: str = "推荐模型") -> str:
    """
    创建评估报告
    
    Args:
        results: 评估结果
        model_name: 模型名称
    
    Returns:
        str: 评估报告
    """
    report = f"""
# {model_name} 评估报告

## 📊 性能指标

| 指标 | K=10 | K=20 | K=50 |
|------|------|------|------|
| HR@K | {results.get('hr10', 0):.4f} | {results.get('hr20', 0):.4f} | {results.get('hr50', 0):.4f} |
| MRR@K | {results.get('mrr10', 0):.4f} | {results.get('mrr20', 0):.4f} | {results.get('mrr50', 0):.4f} |
| NDCG@K | {results.get('ndcg10', 0):.4f} | {results.get('ndcg20', 0):.4f} | {results.get('ndcg50', 0):.4f} |

## 📈 综合评分
- **总评分**: {results.get('total_score', 0):.4f}

## 📊 数据统计
- **评估用户数**: {results.get('total_users', 0):,}
- **候选商品数**: {results.get('total_candidates', 0):,}
- **平均每用户候选数**: {results.get('avg_candidates_per_user', 0):.1f}

## 🎯 评估方法
- **验证策略**: 留一验证 (Leave-One-Out)
- **时序切分**: 每个用户最后一次购买作为标签
- **评估指标**: HR@K, MRR@K, NDCG@K
"""
    
    return report

if __name__ == "__main__":
    # 测试评估函数
    print("🧪 测试留一验证评估函数")
    
    # 创建测试数据
    np.random.seed(42)
    
    # 模拟候选数据
    candidates_df = pd.DataFrame({
        'buyer_admin_id': np.repeat(range(100), 50),
        'item_id': np.random.randint(1, 1000, 5000),
        'pred': np.random.rand(5000)
    })
    
    # 模拟标签数据
    label_df = pd.DataFrame({
        'buyer_admin_id': range(100),
        'label_item': np.random.randint(1, 1000, 100)
    })
    
    # 执行评估
    results = evaluate_recommendations(candidates_df, label_df)
    
    # 生成报告
    report = create_evaluation_report(results, "测试模型")
    print(report)
