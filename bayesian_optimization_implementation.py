# 🎯 贝叶斯优化实现 - 智能FAST_MODE版本
# 只限制数据量，不限制参数范围，避免排除合适参数

import pandas as pd
import numpy as np
import time
from datetime import datetime
import json
from typing import Dict, Any, Tuple
from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args
from skopt.acquisition import gaussian_ei

class BayesianOptimizer:
    """贝叶斯优化器 - 智能FAST_MODE版本"""
    
    def __init__(self, fast_mode: bool = True, user_sample_ratio: float = 0.05):
        self.fast_mode = fast_mode
        self.user_sample_ratio = user_sample_ratio
        self.results = []
        self.best_params = None
        self.best_score = 0
        
        # 参数搜索范围（基于原始参数设置合理范围）
        self.param_ranges = {
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
        
        # 定义搜索空间
        self.dimensions = [
            Integer(self.param_ranges['covisit_window'][0], 
                   self.param_ranges['covisit_window'][1], name='covisit_window'),
            Integer(self.param_ranges['covisit_top_per_a'][0], 
                   self.param_ranges['covisit_top_per_a'][1], name='covisit_top_per_a'),
            Integer(self.param_ranges['recent_k'][0], 
                   self.param_ranges['recent_k'][1], name='recent_k'),
            Integer(self.param_ranges['cand_per_recent'][0], 
                   self.param_ranges['cand_per_recent'][1], name='cand_per_recent'),
            Integer(self.param_ranges['tau_days'][0], 
                   self.param_ranges['tau_days'][1], name='tau_days'),
            Integer(self.param_ranges['user_top_cates'][0], 
                   self.param_ranges['user_top_cates'][1], name='user_top_cates'),
            Integer(self.param_ranges['user_top_stores'][0], 
                   self.param_ranges['user_top_stores'][1], name='user_top_stores'),
            Integer(self.param_ranges['per_cate_pool'][0], 
                   self.param_ranges['per_cate_pool'][1], name='per_cate_pool'),
            Integer(self.param_ranges['per_store_pool'][0], 
                   self.param_ranges['per_store_pool'][1], name='per_store_pool'),
            Integer(self.param_ranges['pop_pool'][0], 
                   self.param_ranges['pop_pool'][1], name='pop_pool'),
            Integer(self.param_ranges['recall_cap'][0], 
                   self.param_ranges['recall_cap'][1], name='recall_cap'),
            Integer(self.param_ranges['batch_size'][0], 
                   self.param_ranges['batch_size'][1], name='batch_size'),
        ]
    
    def evaluate_params(self, params: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        评估参数组合的效果
        
        Args:
            params: 参数字典
        
        Returns:
            score: 综合评分
            metrics: 详细指标
        """
        print(f"🔍 测试参数: {params}")
        
        # 模拟参数效果评估（您需要根据实际业务指标来定义）
        # 这里提供一个示例实现
        
        # 1. 召回率评分 (40%)
        recall_score = self._estimate_recall_score(params)
        
        # 2. 多样性评分 (20%)
        diversity_score = self._estimate_diversity_score(params)
        
        # 3. 计算效率评分 (20%)
        efficiency_score = self._estimate_efficiency_score(params)
        
        # 4. 覆盖率评分 (20%)
        coverage_score = self._estimate_coverage_score(params)
        
        # 综合评分
        total_score = (0.4 * recall_score + 
                      0.2 * diversity_score + 
                      0.2 * efficiency_score + 
                      0.2 * coverage_score)
        
        metrics = {
            'recall_score': recall_score,
            'diversity_score': diversity_score,
            'efficiency_score': efficiency_score,
            'coverage_score': coverage_score,
            'total_score': total_score,
            'fast_mode': self.fast_mode,
            'user_sample_ratio': self.user_sample_ratio
        }
        
        print(f"  📊 评分: {total_score:.3f} (召回:{recall_score:.3f}, 多样性:{diversity_score:.3f}, 效率:{efficiency_score:.3f}, 覆盖率:{coverage_score:.3f})")
        
        return total_score, metrics
    
    def _estimate_recall_score(self, params: Dict[str, Any]) -> float:
        """估算召回率评分"""
        score = 0
        
        # covisit_window: 窗口越大，召回越多
        window_score = min(1.0, params['covisit_window'] / 8.0)
        score += 0.3 * window_score
        
        # recent_k: 最近商品数越多，召回越多
        recent_score = min(1.0, params['recent_k'] / 15.0)
        score += 0.3 * recent_score
        
        # recall_cap: 候选数越多，召回越多
        cap_score = min(1.0, params['recall_cap'] / 1200.0)
        score += 0.4 * cap_score
        
        return score
    
    def _estimate_diversity_score(self, params: Dict[str, Any]) -> float:
        """估算多样性评分"""
        diversity = 0
        
        # 全局热门池大小影响多样性
        if params['pop_pool'] > 2000:
            diversity += 0.3
        
        # 类目和店铺池大小影响个性化多样性
        if params['per_cate_pool'] > 80:
            diversity += 0.3
        if params['per_store_pool'] > 60:
            diversity += 0.2
        
        # 共现关系数量影响协同过滤多样性
        if params['covisit_top_per_a'] > 200:
            diversity += 0.2
        
        return min(1.0, diversity)
    
    def _estimate_efficiency_score(self, params: Dict[str, Any]) -> float:
        """估算计算效率评分"""
        # 基于参数值估算计算复杂度
        complexity = 0
        
        # 共现计算复杂度
        covisit_factor = params['covisit_window'] * params['covisit_top_per_a'] / 1000.0
        
        # 候选生成复杂度
        candidate_factor = params['recent_k'] * params['cand_per_recent'] * params['recall_cap'] / 100000.0
        
        # 热门池计算复杂度
        pool_factor = (params['per_cate_pool'] + params['per_store_pool'] + params['pop_pool']) / 5000.0
        
        total_complexity = covisit_factor + candidate_factor + pool_factor
        
        # 效率评分：复杂度越低，效率越高
        efficiency = max(0, 1.0 - total_complexity / 10.0)
        
        return efficiency
    
    def _estimate_coverage_score(self, params: Dict[str, Any]) -> float:
        """估算覆盖率评分"""
        coverage = 0
        
        # 全局热门池影响覆盖率
        if params['pop_pool'] > 2000:
            coverage += 0.4
        
        # 类目池影响覆盖率
        if params['per_cate_pool'] > 80:
            coverage += 0.3
        
        # 店铺池影响覆盖率
        if params['per_store_pool'] > 60:
            coverage += 0.3
        
        return min(1.0, coverage)
    
    def run_optimization(self, n_calls: int = 50, random_state: int = 42):
        """
        运行贝叶斯优化
        
        Args:
            n_calls: 评估次数
            random_state: 随机种子
        
        Returns:
            best_params: 最佳参数
            best_score: 最佳评分
        """
        print(f"🎯 开始贝叶斯优化")
        print(f"📊 模式: {'快速模式' if self.fast_mode else '生产模式'}")
        print(f"👥 用户采样比例: {self.user_sample_ratio*100:.1f}%")
        print(f"🔄 评估次数: {n_calls}")
        print(f"📏 参数范围: {len(self.param_ranges)} 个参数")
        
        # 目标函数
        @use_named_args(dimensions=self.dimensions)
        def objective(**params):
            score, metrics = self.evaluate_params(params)
            
            # 记录结果
            result = {
                'params': params.copy(),
                'score': score,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(result)
            
            # 更新最佳参数
            if score > self.best_score:
                self.best_score = score
                self.best_params = params.copy()
                print(f"  🎉 新的最佳参数! 评分: {score:.3f}")
            
            return -score  # 最小化负分数
        
        # 运行贝叶斯优化
        start_time = time.time()
        
        try:
            result = gp_minimize(
                func=objective,
                dimensions=self.dimensions,
                n_calls=n_calls,
                random_state=random_state,
                acq_func='EI'  # 使用期望改进采集函数
            )
            
            end_time = time.time()
            
            print(f"\n✅ 贝叶斯优化完成!")
            print(f"⏰ 总耗时: {end_time - start_time:.2f}秒")
            print(f"🏆 最佳评分: {self.best_score:.3f}")
            print(f"🎯 最佳参数: {self.best_params}")
            
            return self.best_params, self.best_score
            
        except Exception as e:
            print(f"❌ 贝叶斯优化失败: {e}")
            return None, 0
    
    def save_results(self, filename: str = 'bayesian_optimization_results.json'):
        """保存优化结果"""
        results_data = {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'all_results': self.results,
            'param_ranges': self.param_ranges,
            'fast_mode': self.fast_mode,
            'user_sample_ratio': self.user_sample_ratio,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 优化结果已保存到: {filename}")
    
    def print_summary(self):
        """打印优化摘要"""
        print(f"\n📊 贝叶斯优化摘要")
        print(f"=" * 50)
        print(f"🎯 模式: {'快速模式' if self.fast_mode else '生产模式'}")
        print(f"👥 用户采样比例: {self.user_sample_ratio*100:.1f}%")
        print(f"🔄 总评估次数: {len(self.results)}")
        print(f"🏆 最佳评分: {self.best_score:.3f}")
        print(f"🎯 最佳参数:")
        for param, value in self.best_params.items():
            print(f"  {param}: {value}")
        
        # 显示评分分布
        if self.results:
            scores = [r['score'] for r in self.results]
            print(f"\n📈 评分统计:")
            print(f"  最高分: {max(scores):.3f}")
            print(f"  最低分: {min(scores):.3f}")
            print(f"  平均分: {np.mean(scores):.3f}")
            print(f"  标准差: {np.std(scores):.3f}")

# 使用示例
if __name__ == "__main__":
    # 快速模式优化
    print("🚀 快速模式贝叶斯优化")
    fast_optimizer = BayesianOptimizer(fast_mode=True, user_sample_ratio=0.05)
    fast_params, fast_score = fast_optimizer.run_optimization(n_calls=30)
    fast_optimizer.save_results('fast_mode_results.json')
    fast_optimizer.print_summary()
    
    print("\n" + "="*60)
    
    # 生产模式优化
    print("🏭 生产模式贝叶斯优化")
    prod_optimizer = BayesianOptimizer(fast_mode=False, user_sample_ratio=1.0)
    prod_params, prod_score = prod_optimizer.run_optimization(n_calls=50)
    prod_optimizer.save_results('prod_mode_results.json')
    prod_optimizer.print_summary()
