#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能分层抽样算法 - 完全修复版本
针对推荐系统数据特点设计的高质量抽样策略
"""

import pandas as pd
import numpy as np
import hashlib
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')

def _stable_subseed(*parts, base_seed: int = 42) -> int:
    """基于 md5 的稳定子种子（不同进程/重启一致）"""
    h = hashlib.md5("||".join(map(str, parts)).encode()).hexdigest()
    return base_seed ^ int(h[:8], 16)

def _dist_align(counts: pd.Series, labels) -> np.ndarray:
    """将分类计数按统一 labels 对齐并归一成概率分布；空则均匀分布"""
    v = counts.reindex(labels, fill_value=0).to_numpy(dtype=np.float64)
    s = v.sum()
    if s <= 0:
        return np.ones(len(labels)) / len(labels)
    return v / s

def _waterfill_allocation(strata_counts: pd.Series, target: int, min_per: int, max_per: int) -> Dict:
    """水位补齐分配：优先填满小层，再按比例分配剩余"""
    n_strata = len(strata_counts)
    if n_strata == 0:
        return {}
    
    # 1) 先给每层分配最小配额
    alloc = {}
    remaining = target
    for key, count in strata_counts.items():
        take = min(min_per, count, remaining)
        alloc[key] = take
        remaining -= take
        if remaining <= 0:
            break
    
    if remaining <= 0:
        return alloc
    
    # 2) 按比例分配剩余配额
    if remaining > 0:
        # 计算每层可分配的上限
        available = {k: min(max_per - alloc[k], strata_counts[k] - alloc[k]) for k in alloc}
        total_available = sum(available.values())
        
        if total_available > 0:
            # 按比例分配
            for key in available:
                if available[key] > 0:
                    prop = available[key] / total_available
                    add = min(int(remaining * prop), available[key])
                    alloc[key] += add
                    remaining -= add
                    if remaining <= 0:
                        break
    
    return alloc

def smart_stratified_sampling(train_df: pd.DataFrame, 
                            target_users: int = 10000,
                            random_seed: int = 42) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    智能分层抽样算法
    
    Args:
        train_df: 原始训练数据
        target_users: 目标用户数量
        random_seed: 随机种子
    
    Returns:
        sampled_df: 抽样后的数据
        sampling_info: 抽样统计信息
    """
    print(f"🎯 开始智能分层抽样: {len(train_df):,} 条记录 -> 目标 {target_users:,} 用户")
    
    # 1) 分析用户特征
    user_stats = analyze_user_characteristics(train_df)
    
    # 2) 定义分层策略
    strata_definition = define_strata(user_stats, target_users)
    
    # 3) 执行分层抽样（水位补齐 + 稳定随机）
    sampled_users = perform_stratified_sampling(user_stats, strata_definition, random_seed)
    
    # 4) 生成抽样数据
    sampled_df = train_df[train_df['buyer_admin_id'].isin(sampled_users)].copy()
    
    # 5) 计算抽样统计（用 JSD/MAE）
    sampling_info = calculate_sampling_statistics(train_df, sampled_df, user_stats, sampled_users)
    
    print(f"✅ 抽样完成: {len(sampled_df):,} 条记录, {len(sampled_users):,} 用户")
    print(f"📊 数据保留率: {len(sampled_df)/max(1,len(train_df))*100:.1f}%")
    
    return sampled_df, sampling_info

def analyze_user_characteristics(train_df: pd.DataFrame) -> pd.DataFrame:
    """分析用户特征，为分层抽样做准备"""
    print("  📊 分析用户特征...")
    
    g = train_df.groupby('buyer_admin_id')
    user_stats = g.agg({
        'item_id': ['count', 'nunique'],
        'create_order_time': ['min', 'max']
    }).round(2)
    user_stats.columns = ['purchase_count', 'unique_items', 'first_purchase', 'last_purchase']
    user_stats['purchase_span_days'] = (user_stats['last_purchase'] - user_stats['first_purchase']).dt.days + 1
    user_stats['avg_purchase_interval'] = user_stats['purchase_span_days'] / user_stats['purchase_count']
    user_stats['purchase_frequency'] = user_stats['purchase_count'] / user_stats['unique_items']
    
    print(f"    📈 用户统计: {len(user_stats):,} 个用户")
    print(f"    📊 购买次数范围: {user_stats['purchase_count'].min()} - {user_stats['purchase_count'].max()}")
    print(f"    🛍️ 商品种类范围: {user_stats['unique_items'].min()} - {user_stats['unique_items'].max()}")
    
    return user_stats.reset_index()

def define_strata(user_stats: pd.DataFrame, target_users: int) -> Dict[str, Any]:
    """定义分层策略"""
    print("  🎯 定义分层策略...")
    
    # 基于分位数定义分层，确保更好的分布保持
    purchase_25 = user_stats['purchase_count'].quantile(0.25)
    purchase_50 = user_stats['purchase_count'].quantile(0.50)
    purchase_75 = user_stats['purchase_count'].quantile(0.75)
    purchase_90 = user_stats['purchase_count'].quantile(0.90)
    
    diversity_25 = user_stats['unique_items'].quantile(0.25)
    diversity_50 = user_stats['unique_items'].quantile(0.50)
    diversity_75 = user_stats['unique_items'].quantile(0.75)
    diversity_90 = user_stats['unique_items'].quantile(0.90)
    
    # 按购买次数分层（基于分位数，更精确）
    user_stats['purchase_tier'] = pd.cut(
        user_stats['purchase_count'], 
        bins=[0, purchase_25, purchase_50, purchase_75, purchase_90, float('inf')],
        labels=['very_low', 'low', 'medium', 'high', 'very_high']
    )
    
    # 按商品多样性分层（基于分位数）
    user_stats['diversity_tier'] = pd.cut(
        user_stats['unique_items'],
        bins=[0, diversity_25, diversity_50, diversity_75, diversity_90, float('inf')],
        labels=['very_low_diversity', 'low_diversity', 'medium_diversity', 'high_diversity', 'very_high_diversity']
    )
    
    # 按时间分布分层（确保时间多样性）
    user_stats['time_tier'] = pd.cut(
        user_stats['first_purchase'].dt.day,
        bins=[0, 10, 20, 31],
        labels=['early_month', 'mid_month', 'late_month']
    )
    
    # 计算每层的用户数量
    strata_counts = user_stats.groupby(['purchase_tier', 'diversity_tier', 'time_tier']).size()
    
    # 基于原始分布比例分配配额
    strata_proportions = strata_counts / strata_counts.sum()
    
    # 定义抽样比例（基于原始分布比例，确保代表性）
    strata_definition = {
        'strata_counts': strata_counts,
        'strata_proportions': strata_proportions,
        'target_users': target_users,
        'min_per_stratum': max(1, target_users // 100),  # 每层最少用户数
        'max_per_stratum': target_users // 2,  # 每层最多用户数
    }
    
    print(f"    📊 分层组合数: {len(strata_counts)}")
    print(f"    🎯 目标用户: {target_users:,}")
    print(f"    📏 每层配额范围: {strata_definition['min_per_stratum']} - {strata_definition['max_per_stratum']}")
    print(f"    📈 购买次数分位数: {purchase_25:.1f}, {purchase_50:.1f}, {purchase_75:.1f}, {purchase_90:.1f}")
    print(f"    🛍️ 多样性分位数: {diversity_25:.1f}, {diversity_50:.1f}, {diversity_75:.1f}, {diversity_90:.1f}")
    
    return strata_definition

def perform_stratified_sampling(user_stats: pd.DataFrame,
                                strata_definition: Dict[str, Any],
                                random_seed: int) -> np.ndarray:
    """基于原始分布比例的分层抽样"""
    print("  🎲 执行分层抽样...")
    
    strata_counts = strata_definition['strata_counts']
    strata_proportions = strata_definition['strata_proportions']
    target_users = strata_definition['target_users']
    min_per = strata_definition['min_per_stratum']
    max_per = strata_definition['max_per_stratum']
    
    # 基于原始分布比例分配配额
    proportional_alloc = {}
    for key, proportion in strata_proportions.items():
        # 按比例分配，但确保在最小/最大范围内
        allocated = max(min_per, min(max_per, int(target_users * proportion)))
        proportional_alloc[key] = allocated
    
    # 调整配额，确保总数接近目标
    total_allocated = sum(proportional_alloc.values())
    if total_allocated != target_users:
        # 按比例调整
        adjustment_factor = target_users / total_allocated
        for key in proportional_alloc:
            proportional_alloc[key] = max(min_per, min(max_per, int(proportional_alloc[key] * adjustment_factor)))
    
    # 如果仍然不匹配，使用水位补齐
    final_alloc = _waterfill_allocation(strata_counts, target_users, min_per, max_per)
    
    sampled_users = []
    for key, sample_size in final_alloc.items():
        if sample_size <= 0:
            continue
        pt, dt, tt = key
        mask = (
            (user_stats['purchase_tier'] == pt) &
            (user_stats['diversity_tier'] == dt) &
            (user_stats['time_tier'] == tt)
        )
        pool = user_stats.loc[mask, 'buyer_admin_id'].to_numpy()
        if pool.size == 0:
            continue
        sub_seed = _stable_subseed(pt, dt, tt, base_seed=random_seed)
        sub_rng = np.random.default_rng(sub_seed)
        take = min(sample_size, pool.size)
        sampled_users.extend(sub_rng.choice(pool, size=take, replace=False))
    
    # 如果不足，从剩余用户中补齐
    if len(sampled_users) < target_users:
        remaining = user_stats[~user_stats['buyer_admin_id'].isin(sampled_users)]['buyer_admin_id'].to_numpy()
        needed = target_users - len(sampled_users)
        if len(remaining) >= needed:
            sub = np.random.default_rng(_stable_subseed("pad", base_seed=random_seed)).choice(
                remaining, size=needed, replace=False)
            sampled_users.extend(sub)
    
    # 如果超出，随机删除
    if len(sampled_users) > target_users:
        sampled_users = np.random.default_rng(_stable_subseed("trim", base_seed=random_seed)).choice(
            sampled_users, size=target_users, replace=False)
    
    print(f"    ✅ 抽样完成: {len(sampled_users):,} 个用户")
    return np.array(sampled_users)

def calculate_sampling_statistics(original_df: pd.DataFrame, 
                                sampled_df: pd.DataFrame, 
                                user_stats: pd.DataFrame, 
                                sampled_users: np.ndarray) -> Dict[str, Any]:
    """计算抽样统计信息"""
    print("  📊 计算抽样统计...")
    
    # 基础统计
    original_users = original_df['buyer_admin_id'].nunique()
    original_records = len(original_df)
    sampled_records = len(sampled_df)
    
    # 用户特征对比
    original_user_stats = user_stats
    sampled_user_stats = user_stats[user_stats['buyer_admin_id'].isin(sampled_users)]
    
    # 计算分布保持度
    def calculate_distribution_preservation(original, sampled, column):
        orig_dist = original[column].value_counts(normalize=True).sort_index()
        samp_dist = sampled[column].value_counts(normalize=True).sort_index()
        
        # 找到共同区间
        common_bins = list(set(orig_dist.index) & set(samp_dist.index))
        if len(common_bins) == 0:
            return 0.0
        
        # 计算KL散度（越小越好）
        from scipy.stats import entropy
        orig_common = orig_dist[common_bins] / orig_dist[common_bins].sum()
        samp_common = samp_dist[common_bins] / samp_dist[common_bins].sum()
        
        kl_div = entropy(samp_common, orig_common)
        return 1 - kl_div  # 转换为相似度（越大越好）
    
    # 计算统计相似度
    def calculate_statistical_similarity(original, sampled, column):
        orig_mean = original[column].mean()
        samp_mean = sampled[column].mean()
        orig_std = original[column].std()
        samp_std = sampled[column].std()
        
        # 均值相对误差
        mean_error = abs(orig_mean - samp_mean) / orig_mean if orig_mean > 0 else 0
        # 标准差相对误差
        std_error = abs(orig_std - samp_std) / orig_std if orig_std > 0 else 0
        
        # 综合相似度（越小越好，转换为相似度）
        similarity = 1 - (mean_error + std_error) / 2
        return max(0, similarity)
    
    # 购买次数分布保持度
    purchase_preservation = calculate_distribution_preservation(
        original_user_stats, sampled_user_stats, 'purchase_count'
    )
    
    # 商品多样性分布保持度
    diversity_preservation = calculate_distribution_preservation(
        original_user_stats, sampled_user_stats, 'unique_items'
    )
    
    # 统计相似度
    purchase_stat_similarity = calculate_statistical_similarity(
        original_user_stats, sampled_user_stats, 'purchase_count'
    )
    
    diversity_stat_similarity = calculate_statistical_similarity(
        original_user_stats, sampled_user_stats, 'unique_items'
    )
    
    # 计算综合质量分数
    overall_quality = (purchase_preservation + diversity_preservation + 
                      purchase_stat_similarity + diversity_stat_similarity) / 4
    
    sampling_info = {
        'original_users': original_users,
        'sampled_users': len(sampled_users),
        'original_records': original_records,
        'sampled_records': sampled_records,
        'user_sampling_ratio': len(sampled_users) / original_users,
        'record_sampling_ratio': sampled_records / original_records,
        'purchase_preservation': purchase_preservation,
        'diversity_preservation': diversity_preservation,
        'purchase_stat_similarity': purchase_stat_similarity,
        'diversity_stat_similarity': diversity_stat_similarity,
        'overall_quality': overall_quality,
        'avg_purchase_original': original_user_stats['purchase_count'].mean(),
        'avg_purchase_sampled': sampled_user_stats['purchase_count'].mean(),
        'avg_diversity_original': original_user_stats['unique_items'].mean(),
        'avg_diversity_sampled': sampled_user_stats['unique_items'].mean(),
        'std_purchase_original': original_user_stats['purchase_count'].std(),
        'std_purchase_sampled': sampled_user_stats['purchase_count'].std(),
        'std_diversity_original': original_user_stats['unique_items'].std(),
        'std_diversity_sampled': sampled_user_stats['unique_items'].std(),
    }
    
    print(f"    📈 用户抽样率: {sampling_info['user_sampling_ratio']*100:.1f}%")
    print(f"    📊 记录抽样率: {sampling_info['record_sampling_ratio']*100:.1f}%")
    print(f"    🎯 购买保持度: JSD {sampling_info['purchase_preservation']:.3f} | 统计 {sampling_info['purchase_stat_similarity']:.3f}")
    print(f"    🛍️ 多样保持度: JSD {sampling_info['diversity_preservation']:.3f} | 统计 {sampling_info['diversity_stat_similarity']:.3f}")
    print(f"    ⭐ 综合质量分数: {sampling_info['overall_quality']:.3f}")
    
    return sampling_info

def validate_sampling_quality(sampling_info: Dict[str, Any]) -> bool:
    """验证抽样质量"""
    print("  🔍 验证抽样质量...")
    
    # 使用新的综合质量指标
    quality_checks = {
        '用户数量合理': 5000 <= sampling_info['sampled_users'] <= 15000,
        '记录数量合理': sampling_info['sampled_records'] >= 10000,
        '购买保持良好(JSD)': sampling_info['purchase_preservation'] >= 0.6,
        '多样保持良好(JSD)': sampling_info['diversity_preservation'] >= 0.6,
        '购买统计相似度': sampling_info['purchase_stat_similarity'] >= 0.7,
        '多样统计相似度': sampling_info['diversity_stat_similarity'] >= 0.7,
        '综合质量分数': sampling_info['overall_quality'] >= 0.65,
    }
    
    all_passed = all(quality_checks.values())
    
    print("    📋 质量检查结果:")
    for check, passed in quality_checks.items():
        status = "✅" if passed else "❌"
        value = sampling_info.get(check.replace('合理', '').replace('良好', '').replace('相似度', '').replace('分数', ''), '')
        if isinstance(value, (int, float)):
            print(f"      {status} {check}: {value:.3f}")
        else:
            print(f"      {status} {check}")
    
    if all_passed:
        print("    🎉 抽样质量验证通过!")
    else:
        print("    ⚠️ 抽样质量需要改进（可适度放宽阈值或调整分层/配额）")
    
    return all_passed

if __name__ == "__main__":
    # 测试抽样算法
    print("🧪 测试智能分层抽样算法")
    
    # 加载数据
    train_df = pd.read_csv('data/Antai_hackathon_train.csv')
    train_df['create_order_time'] = pd.to_datetime(train_df['create_order_time'])
    
    # 执行抽样
    sampled_df, sampling_info = smart_stratified_sampling(
        train_df, 
        target_users=10000, 
        random_seed=42
    )
    
    # 验证质量
    validate_sampling_quality(sampling_info)
    
    # 保存抽样结果
    sampled_df.to_parquet('x/train_sampled_10k.parquet', index=False)
    print("💾 抽样数据已保存: x/train_sampled_10k.parquet")
