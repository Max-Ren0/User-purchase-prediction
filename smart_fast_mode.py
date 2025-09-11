# 🚀 智能FAST_MODE策略
# 只限制数据量，不限制参数范围，避免排除合适参数

import pandas as pd
import numpy as np
from typing import Dict, Any

class SmartFastMode:
    """智能快速模式管理"""
    
    def __init__(self):
        self.original_params = {
            'covisit_window': 3,
            'covisit_top_per_a': 200,
            'recent_k': 5,
            'cand_per_recent': 40,
            'tau_days': 14,
            'user_top_cates': 3,
            'user_top_stores': 3,
            'per_cate_pool': 80,
            'per_store_pool': 60,
            'pop_pool': 2000,
            'recall_cap': 600,
            'batch_size': 2000,
        }
    
    def get_fast_mode_config(self, fast_mode: bool = True, user_sample_ratio: float = 0.05):
        """
        获取快速模式配置
        
        Args:
            fast_mode: 是否启用快速模式
            user_sample_ratio: 用户采样比例 (0.05 = 5%)
        
        Returns:
            dict: 配置参数
        """
        if not fast_mode:
            return {
                'FAST_MODE': False,
                'N_SMOKE': None,
                'USER_SAMPLE_RATIO': 1.0,
                'PARAMS': self.original_params.copy(),
                'description': '生产模式 - 完整数据运行'
            }
        
        # 快速模式：只限制数据量，保持参数范围
        return {
            'FAST_MODE': True,
            'N_SMOKE': None,  # 不限制固定数量
            'USER_SAMPLE_RATIO': user_sample_ratio,  # 使用比例采样
            'PARAMS': self.original_params.copy(),  # 保持原始参数
            'description': f'快速模式 - 采样{user_sample_ratio*100:.1f}%用户进行调优'
        }
    
    def sample_users(self, user_ids: np.ndarray, sample_ratio: float = 0.05, random_seed: int = 42):
        """
        智能用户采样
        
        Args:
            user_ids: 用户ID数组
            sample_ratio: 采样比例
            random_seed: 随机种子
        
        Returns:
            np.ndarray: 采样后的用户ID
        """
        np.random.seed(random_seed)
        
        # 分层采样：确保不同活跃度的用户都被采样
        user_activity = pd.Series(user_ids).value_counts()
        
        # 按活跃度分层
        high_activity = user_activity[user_activity >= 10].index
        medium_activity = user_activity[(user_activity >= 5) & (user_activity < 10)].index
        low_activity = user_activity[user_activity < 5].index
        
        sampled_users = []
        
        # 每层按比例采样
        for activity_group in [high_activity, medium_activity, low_activity]:
            if len(activity_group) > 0:
                n_sample = max(1, int(len(activity_group) * sample_ratio))
                sampled = np.random.choice(activity_group, size=n_sample, replace=False)
                sampled_users.extend(sampled)
        
        return np.array(sampled_users)
    
    def get_parameter_ranges(self):
        """
        获取贝叶斯优化的参数范围
        基于原始参数设置合理的搜索范围
        """
        return {
            'covisit_window': (2, 8),           # 原始值3，范围2-8
            'covisit_top_per_a': (100, 400),    # 原始值200，范围100-400
            'recent_k': (3, 15),                # 原始值5，范围3-15
            'cand_per_recent': (20, 80),        # 原始值40，范围20-80
            'tau_days': (7, 30),                # 原始值14，范围7-30
            'user_top_cates': (2, 6),           # 原始值3，范围2-6
            'user_top_stores': (2, 6),          # 原始值3，范围2-6
            'per_cate_pool': (40, 150),         # 原始值80，范围40-150
            'per_store_pool': (30, 120),        # 原始值60，范围30-120
            'pop_pool': (1000, 4000),           # 原始值2000，范围1000-4000
            'recall_cap': (300, 1200),          # 原始值600，范围300-1200
            'batch_size': (1000, 4000),         # 原始值2000，范围1000-4000
        }

# 使用示例
if __name__ == "__main__":
    smart_fast = SmartFastMode()
    
    # 快速模式配置
    fast_config = smart_fast.get_fast_mode_config(fast_mode=True, user_sample_ratio=0.05)
    print("🚀 快速模式配置:")
    print(f"  用户采样比例: {fast_config['USER_SAMPLE_RATIO']*100:.1f}%")
    print(f"  参数范围: 保持原始范围")
    print(f"  描述: {fast_config['description']}")
    
    # 生产模式配置
    prod_config = smart_fast.get_fast_mode_config(fast_mode=False)
    print("\n🏭 生产模式配置:")
    print(f"  用户采样比例: {prod_config['USER_SAMPLE_RATIO']*100:.1f}%")
    print(f"  参数范围: 保持原始范围")
    print(f"  描述: {prod_config['description']}")
    
    # 参数搜索范围
    param_ranges = smart_fast.get_parameter_ranges()
    print("\n🎯 贝叶斯优化参数范围:")
    for param, (min_val, max_val) in param_ranges.items():
        print(f"  {param}: {min_val} - {max_val}")
