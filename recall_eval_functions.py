# 🎯 召回和评估函数 - 真实指标实现
# 从1_recall.ipynb和3_eval.ipynb提取的核心函数

import pandas as pd
import numpy as np
import time
import os
from typing import Dict, Any, Tuple
import gc

def run_recall(params: Dict[str, Any], data_dir: str = 'x', 
               sample_ratio: float = 1.0) -> Dict[str, Any]:
    """
    运行召回算法 - 真实指标版本
    
    Args:
        params: 参数字典
        data_dir: 数据目录
        sample_ratio: 用户采样比例
    
    Returns:
        artifacts: 召回结果
    """
    print(f"🔄 运行召回算法...")
    print(f"📊 参数: {params}")
    
    # 优先使用抽样数据，如果没有则使用全量数据
    train_sampled_path = f"{data_dir}/train_vis_sampled.parquet"
    train_path = f"{data_dir}/train_sorted.parquet"
    item_attr_path = f"{data_dir}/item_attr.parquet"
    
    if os.path.exists(train_sampled_path):
        print(f"📊 使用抽样数据: {train_sampled_path}")
        train = pd.read_parquet(train_sampled_path)
    else:
        print(f"📊 使用全量数据: {train_path}")
        train = pd.read_parquet(train_path)
    
    # 加载商品属性（如果存在）
    if os.path.exists(item_attr_path):
        item_attr = pd.read_parquet(item_attr_path)
        print(f"📊 加载商品属性: {len(item_attr):,} 个商品")
    else:
        # 创建模拟商品属性
        unique_items = train['item_id'].unique()
        item_attr = pd.DataFrame({
            'item_id': unique_items,
            'cate_id': np.random.randint(1, 20, len(unique_items)),
            'store_id': np.random.randint(1, 50, len(unique_items))
        })
        print(f"📊 创建模拟商品属性: {len(item_attr):,} 个商品")
    
    # 数据采样 - 添加随机种子确保可重复性
    if sample_ratio < 1.0:
        unique_users = train['buyer_admin_id'].unique()
        rng = np.random.default_rng(42)  # 固定随机种子
        sample_users = rng.choice(
            unique_users, 
            size=int(len(unique_users) * sample_ratio),
            replace=False
        )
        train = train[train['buyer_admin_id'].isin(sample_users)]
        print(f"📊 采样后数据: {len(train):,} 行, {len(sample_users):,} 用户")
    
    # 优化数据类型
    train = train.astype({
        'buyer_admin_id': 'int32',
        'item_id': 'int32'
    })
    
    # 如果存在cate_id和store_id列，也进行类型转换
    if 'cate_id' in train.columns:
        train['cate_id'] = train['cate_id'].astype('int32')
    if 'store_id' in train.columns:
        train['store_id'] = train['store_id'].astype('int32')
    
    # 构建统计表
    print(f"📊 构建统计表...")
    
    # 1. 复购评分
    rebuy = build_rebuy_scores_optimized(train, params['tau_days'])
    
    # 2. 共现关系
    covisit = build_covisit_optimized(train, params['covisit_window'], 
                                    params['covisit_top_per_a'])
    
    # 3. 热门统计
    cate_pop, store_pop, global_pop = build_popularity_stats_optimized(
        train, item_attr, params['pop_pool'], params['per_cate_pool'], 
        params['per_store_pool']
    )
    
    # 4. 生成候选
    candidates = build_candidates_ultra_fast(
        train, rebuy, covisit, cate_pop, store_pop, global_pop, params
    )
    
    artifacts = {
        'candidates': candidates,
        'rebuy': rebuy,
        'covisit': covisit,
        'cate_pop': cate_pop,
        'store_pop': store_pop,
        'global_pop': global_pop,
        'params': params,
        'train': train
    }
    
    print(f"✅ 召回完成: {len(candidates):,} 个候选")
    return artifacts

def eval_offline(artifacts: Dict[str, Any], data_dir: str = 'x') -> Dict[str, float]:
    """
    离线评估 - 真实指标版本
    
    Args:
        artifacts: 召回结果
        data_dir: 数据目录
    
    Returns:
        metrics: 评估指标
    """
    print(f"📊 运行离线评估...")
    
    try:
        # 加载标签数据
        label_path = f"{data_dir}/label_df.parquet"
        if not os.path.exists(label_path):
            print(f"⚠️ 标签文件不存在: {label_path}")
            return {
                'hr50': 0.0,
                'mrr50': 0.0,
                'ndcg50': 0.0
            }
        
        label_df = pd.read_parquet(label_path)
        candidates = artifacts['candidates']
        
        # 优化：预处理标签为dict与set
        label_map = (label_df.groupby('buyer_admin_id')['label_item']
                     .apply(set).to_dict())
        
        # 计算评估指标
        hr50 = calculate_hr50_optimized(candidates, label_map)
        mrr50 = calculate_mrr50_optimized(candidates, label_map)
        ndcg50 = calculate_ndcg50_optimized(candidates, label_map)
        
        metrics = {
            'hr50': hr50,
            'mrr50': mrr50,
            'ndcg50': ndcg50
        }
        
        print(f"✅ 评估完成: HR@50={hr50:.3f}, MRR@50={mrr50:.3f}, NDCG@50={ndcg50:.3f}")
        return metrics
        
    except Exception as e:
        print(f"❌ 评估失败: {e}")
        return {
            'hr50': 0.0,
            'mrr50': 0.0,
            'ndcg50': 0.0
        }

# 从1_recall.ipynb提取的核心函数
def build_rebuy_scores_optimized(df, tau_days=14):
    """构建复购评分 - 优化版"""
    print(f"  🔄 构建复购评分...")
    
    # 修复：对每次购买相对参考时刻（如该用户的最后一次）做指数衰减，再求和
    ref = df.groupby('buyer_admin_id')['create_order_time'].transform('max')
    days = (ref - df['create_order_time']).dt.days.clip(lower=0)
    w = np.exp(-days / float(tau_days))
    
    # 按用户和商品聚合
    rebuy = (df.assign(score_rebuy=w)
              .groupby(['buyer_admin_id', 'item_id'])['score_rebuy']
              .sum().reset_index())
    
    return rebuy

def build_covisit_optimized(df, W=3, topk=200):
    """构建共现关系 - 优化版"""
    print(f"  🔗 构建共现关系...")
    
    # 按用户排序
    df_sorted = df.sort_values(['buyer_admin_id', 'create_order_time'])
    
    pairs = []
    for uid, group in df_sorted.groupby('buyer_admin_id'):
        items = group['item_id'].values
        for i in range(len(items)):
            for j in range(i+1, min(i+W+1, len(items))):
                pairs.append({
                    'item_a': items[i],
                    'item_b': items[j],
                    'w': 1.0 / (j - i)
                })
    
    if not pairs:
        return pd.DataFrame(columns=['item_a', 'item_b', 'w'])
    
    co = pd.DataFrame(pairs)
    co = co.groupby(['item_a', 'item_b'])['w'].sum().reset_index()
    co['rn'] = co.groupby('item_a')['w'].rank(ascending=False, method='first')
    
    return co[co['rn'] <= topk].drop(columns='rn')

def build_popularity_stats_optimized(df, item_attr, pop_pool=2000, 
                                   per_cate_pool=80, per_store_pool=60):
    """构建热门统计 - 优化版"""
    print(f"  🌍 构建热门统计...")
    
    # 全局热门
    global_pop = df.groupby('item_id').size().rename('pop').reset_index()
    global_pop = global_pop.sort_values('pop', ascending=False).head(pop_pool)
    
    # 类目热门（如果item_attr中有cate_id）
    if 'cate_id' in item_attr.columns:
        df_with_cate = df.merge(item_attr[['item_id', 'cate_id']], on='item_id', how='left')
        cate_pop = (df_with_cate.groupby(['cate_id', 'item_id']).size().rename('pop').reset_index())
        cate_pop['rn'] = cate_pop.groupby('cate_id')['pop'].rank(ascending=False, method='first')
        cate_pop = cate_pop[cate_pop['rn'] <= per_cate_pool]
    else:
        # 创建空的类目热门表
        cate_pop = pd.DataFrame(columns=['cate_id', 'item_id', 'rn'])
    
    # 店铺热门（如果item_attr中有store_id）
    if 'store_id' in item_attr.columns:
        df_with_store = df.merge(item_attr[['item_id', 'store_id']], on='item_id', how='left')
        store_pop = (df_with_store.groupby(['store_id', 'item_id']).size().rename('pop').reset_index())
        store_pop['rn'] = store_pop.groupby('store_id')['pop'].rank(ascending=False, method='first')
        store_pop = store_pop[store_pop['rn'] <= per_store_pool]
    else:
        # 创建空的店铺热门表
        store_pop = pd.DataFrame(columns=['store_id', 'item_id', 'rn'])
    
    return cate_pop, store_pop, global_pop

def build_candidates_ultra_fast(df, rebuy, covisit, cate_pop, store_pop, global_pop, params):
    """构建候选 - 超快版"""
    print(f"  🎯 构建候选...")
    
    # 预计算映射
    cov_neighbors = {}
    for a, g in covisit.groupby('item_a'):
        sub = g[['item_b', 'w']].head(params['cand_per_recent']).to_numpy()
        if len(sub):
            cov_neighbors[int(a)] = (sub[:, 0].astype('int64'), sub[:, 1].astype('float32'))
    
    recent_map = (df.sort_values('create_order_time')
                  .groupby('buyer_admin_id')['item_id']
                  .apply(lambda s: s.tail(params['recent_k']).to_numpy('int64'))
                  ).to_dict()
    
    # 用户偏好（如果数据中有cate_id和store_id）
    user_topc = {}
    user_tops = {}
    
    if 'cate_id' in item_attr.columns and 'store_id' in item_attr.columns:
        df_with_attr = df.merge(item_attr[['item_id', 'cate_id', 'store_id']], on='item_id', how='left')
        user_topc = (df_with_attr.groupby('buyer_admin_id')['cate_id']
                     .apply(lambda s: s.value_counts().head(params.get('user_top_cates', 3))
                            .index.to_numpy('int64')).to_dict())
        user_tops = (df_with_attr.groupby('buyer_admin_id')['store_id']
                     .apply(lambda s: s.value_counts().head(params.get('user_top_stores', 3))
                            .index.to_numpy('int64')).to_dict())
    
    # 热门池映射
    cate_top = {}
    if not cate_pop.empty and 'cate_id' in cate_pop.columns:
        cate_top = {int(c): grp.loc[grp['rn'] <= params['per_cate_pool'], 'item_id'].to_numpy('int64')
                    for c, grp in cate_pop.groupby('cate_id')}
    
    store_top = {}
    if not store_pop.empty and 'store_id' in store_pop.columns:
        store_top = {int(s): grp.loc[grp['rn'] <= params['per_store_pool'], 'item_id'].to_numpy('int64')
                     for s, grp in store_pop.groupby('store_id')}
    global_items = global_pop['item_id'].to_numpy('int64')
    
    # 复购映射
    rebuy_map = {}
    for uid, g in rebuy.groupby('buyer_admin_id'):
        rebuy_map[int(uid)] = (g['item_id'].to_numpy('int64'), g['score_rebuy'].to_numpy('float32'))
    
    # 生成候选
    candidates = {}
    unique_users = df['buyer_admin_id'].unique()
    
    for uid in unique_users:
        cand = {}
        
        # 1. 复购召回
        if uid in rebuy_map:
            items, ws = rebuy_map[uid]
            for it, w in zip(items, ws):
                cand.setdefault(int(it), []).append(('rebuy', float(w)))
        
        # 2. 协同过滤召回
        for a in recent_map.get(uid, []):
            pair = cov_neighbors.get(int(a))
            if pair is not None:
                bs, ws = pair
                for b, w in zip(bs, ws):
                    cand.setdefault(int(b), []).append(('covisit', float(w)))
        
        # 3. 个性化热门召回
        for c in user_topc.get(uid, []):
            for it in cate_top.get(int(c), ()):
                cand.setdefault(int(it), []).append(('cate_hot', 1.0))
        
        for s in user_tops.get(uid, []):
            for it in store_top.get(int(s), ()):
                cand.setdefault(int(it), []).append(('store_hot', 1.0))
        
        # 4. 全局热门召回 - 优化：仅当候选不足时补全局热门的前M个
        if len(cand) < params['recall_cap'] * 0.6:
            for it in global_items[:min(100, len(global_items))]:
                cand.setdefault(int(it), []).append(('global_pop', 1.0))
        
        # 计算最终评分
        user_items = []
        for item_id, sources in cand.items():
            pre_score = sum(score for _, score in sources)
            user_items.append((item_id, pre_score, sources, len(sources)))
        
        # 排序并截断
        user_items.sort(key=lambda x: x[1], reverse=True)
        top_items = user_items[:params['recall_cap']]
        
        candidates[uid] = top_items
    
    return candidates

# 从3_eval.ipynb提取的评估函数
def calculate_hr50_optimized(candidates, label_map):
    """计算Hit Rate@50 - 优化版"""
    hits = 0
    total = 0
    
    for uid, items in candidates.items():
        if uid in label_map:
            total += 1
            user_labels = label_map[uid]
            top_items = set(item[0] for item in items[:50])  # Top-50
            if user_labels & top_items:  # 集合交集
                hits += 1
    
    return hits / total if total > 0 else 0.0

def calculate_hr50(candidates, label_df):
    """计算Hit Rate@50 - 原版（保留兼容性）"""
    hits = 0
    total = 0
    
    for uid, items in candidates.items():
        if uid in label_df['buyer_admin_id'].values:
            total += 1
            user_labels = label_df[label_df['buyer_admin_id'] == uid]['label_item'].values
            top_items = [item[0] for item in items[:50]]  # Top-50
            if any(label in top_items for label in user_labels):
                hits += 1
    
    return hits / total if total > 0 else 0.0

def calculate_mrr50_optimized(candidates, label_map):
    """计算MRR@50 - 优化版"""
    mrr_sum = 0
    total = 0
    
    for uid, items in candidates.items():
        if uid in label_map:
            total += 1
            user_labels = label_map[uid]
            top_items = [item[0] for item in items[:50]]  # Top-50
            for i, item in enumerate(top_items):
                if item in user_labels:
                    mrr_sum += 1.0 / (i + 1)
                    break
    
    return mrr_sum / total if total > 0 else 0.0

def calculate_mrr50(candidates, label_df):
    """计算MRR@50 - 原版（保留兼容性）"""
    mrr_sum = 0
    total = 0
    
    for uid, items in candidates.items():
        if uid in label_df['buyer_admin_id'].values:
            total += 1
            user_labels = label_df[label_df['buyer_admin_id'] == uid]['label_item'].values
            top_items = [item[0] for item in items[:50]]  # Top-50
            
            for rank, item in enumerate(top_items, 1):
                if item in user_labels:
                    mrr_sum += 1.0 / rank
                    break
    
    return mrr_sum / total if total > 0 else 0.0

def calculate_ndcg50_optimized(candidates, label_map):
    """计算NDCG@50 - 优化版"""
    ndcg_sum = 0
    total = 0
    
    for uid, items in candidates.items():
        if uid in label_map:
            total += 1
            user_labels = label_map[uid]
            top_items = [item[0] for item in items[:50]]  # Top-50
            
            # 计算DCG
            dcg = 0
            for rank, item in enumerate(top_items, 1):
                if item in user_labels:
                    dcg += 1.0 / np.log2(rank + 1)
            
            # 计算IDCG (理想情况)
            idcg = sum(1.0 / np.log2(i + 1) for i in range(1, min(len(user_labels), 50) + 1))
            
            ndcg_sum += dcg / idcg if idcg > 0 else 0
    
    return ndcg_sum / total if total > 0 else 0.0

def calculate_ndcg50(candidates, label_df):
    """计算NDCG@50 - 原版（保留兼容性）"""
    ndcg_sum = 0
    total = 0
    
    for uid, items in candidates.items():
        if uid in label_df['buyer_admin_id'].values:
            total += 1
            user_labels = label_df[label_df['buyer_admin_id'] == uid]['label_item'].values
            top_items = [item[0] for item in items[:50]]  # Top-50
            
            # 计算DCG
            dcg = 0
            for rank, item in enumerate(top_items, 1):
                if item in user_labels:
                    dcg += 1.0 / np.log2(rank + 1)
            
            # 计算IDCG (理想情况)
            idcg = sum(1.0 / np.log2(i + 1) for i in range(1, min(len(user_labels), 50) + 1))
            
            ndcg_sum += dcg / idcg if idcg > 0 else 0
    
    return ndcg_sum / total if total > 0 else 0.0
