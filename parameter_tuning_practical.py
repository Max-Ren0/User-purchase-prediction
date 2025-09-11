# 🎯 实用参数调优脚本
# 基于您的推荐系统，提供具体的调优方法

import pandas as pd
import numpy as np
import time
from itertools import product
import json
from datetime import datetime

class ParameterTuner:
    """参数调优器"""
    
    def __init__(self):
        self.results = []
        self.best_params = None
        self.best_score = 0
    
    def evaluate_params(self, params, data_sample=None):
        """
        评估参数组合的效果
        
        Args:
            params: 参数字典
            data_sample: 数据样本（用于快速测试）
        
        Returns:
            score: 综合评分
            metrics: 详细指标
        """
        print(f"🔍 测试参数: {params}")
        
        # 模拟参数效果评估
        # 这里您需要根据实际业务指标来定义评分函数
        
        # 示例评分逻辑（您需要根据实际情况调整）
        score = 0
        
        # 1. 召回率评分 (40%)
        recall_score = self._estimate_recall_score(params)
        score += 0.4 * recall_score
        
        # 2. 多样性评分 (20%)
        diversity_score = self._estimate_diversity_score(params)
        score += 0.2 * diversity_score
        
        # 3. 计算效率评分 (20%)
        efficiency_score = self._estimate_efficiency_score(params)
        score += 0.2 * efficiency_score
        
        # 4. 覆盖率评分 (20%)
        coverage_score = self._estimate_coverage_score(params)
        score += 0.2 * coverage_score
        
        metrics = {
            'recall_score': recall_score,
            'diversity_score': diversity_score,
            'efficiency_score': efficiency_score,
            'coverage_score': coverage_score,
            'total_score': score
        }
        
        print(f"  📊 评分: {score:.3f} (召回:{recall_score:.3f}, 多样性:{diversity_score:.3f}, 效率:{efficiency_score:.3f}, 覆盖率:{coverage_score:.3f})")
        
        return score, metrics
    
    def _estimate_recall_score(self, params):
        """估算召回率评分"""
        # 基于参数值估算召回效果
        score = 0
        
        # covisit_window: 窗口越大，召回越多，但计算越慢
        window_score = min(1.0, params['covisit_window'] / 5.0)
        score += 0.3 * window_score
        
        # recent_k: 最近商品数越多，召回越多
        recent_score = min(1.0, params['recent_k'] / 8.0)
        score += 0.3 * recent_score
        
        # recall_cap: 候选数越多，召回越多
        cap_score = min(1.0, params['recall_cap'] / 800.0)
        score += 0.4 * cap_score
        
        return score
    
    def _estimate_diversity_score(self, params):
        """估算多样性评分"""
        # 多样性主要看是否使用了多种召回策略
        diversity = 0
        
        # 全局热门池大小影响多样性
        if params['pop_pool'] > 1000:
            diversity += 0.3
        
        # 类目和店铺池大小影响个性化多样性
        if params['per_cate_pool'] > 50:
            diversity += 0.3
        if params['per_store_pool'] > 40:
            diversity += 0.2
        
        # 共现关系数量影响协同过滤多样性
        if params['covisit_top_per_a'] > 150:
            diversity += 0.2
        
        return min(1.0, diversity)
    
    def _estimate_efficiency_score(self, params):
        """估算计算效率评分"""
        # 基于参数值估算计算复杂度
        complexity = 0
        
        # 用户数（固定）
        user_factor = 1.0
        
        # 共现计算复杂度
        covisit_factor = params['covisit_window'] * params['covisit_top_per_a'] / 1000.0
        
        # 候选生成复杂度
        candidate_factor = params['recent_k'] * params['cand_per_recent'] * params['recall_cap'] / 100000.0
        
        # 热门池计算复杂度
        pool_factor = (params['per_cate_pool'] + params['per_store_pool'] + params['pop_pool']) / 5000.0
        
        total_complexity = user_factor * (covisit_factor + candidate_factor + pool_factor)
        
        # 效率评分：复杂度越低，效率越高
        efficiency = max(0, 1.0 - total_complexity / 10.0)
        
        return efficiency
    
    def _estimate_coverage_score(self, params):
        """估算覆盖率评分"""
        # 覆盖率主要看是否能覆盖到更多商品
        coverage = 0
        
        # 全局热门池影响覆盖率
        if params['pop_pool'] > 1500:
            coverage += 0.4
        
        # 类目池影响覆盖率
        if params['per_cate_pool'] > 60:
            coverage += 0.3
        
        # 店铺池影响覆盖率
        if params['per_store_pool'] > 50:
            coverage += 0.3
        
        return min(1.0, coverage)
    
    def grid_search(self, param_ranges, max_combinations=50):
        """
        网格搜索最优参数
        
        Args:
            param_ranges: 参数范围字典
            max_combinations: 最大搜索组合数
        """
        print(f"🔍 开始网格搜索，最大组合数: {max_combinations}")
        
        # 生成参数组合
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        combinations = list(product(*param_values))
        
        # 限制搜索数量
        if len(combinations) > max_combinations:
            # 随机采样
            import random
            combinations = random.sample(combinations, max_combinations)
            print(f"📊 随机采样 {max_combinations} 个组合进行搜索")
        
        print(f"📊 总共测试 {len(combinations)} 个参数组合")
        
        # 测试每个组合
        for i, combination in enumerate(combinations):
            params = dict(zip(param_names, combination))
            
            print(f"\n🔄 测试组合 {i+1}/{len(combinations)}")
            
            try:
                score, metrics = self.evaluate_params(params)
                
                result = {
                    'params': params,
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
                
            except Exception as e:
                print(f"  ❌ 参数组合测试失败: {e}")
                continue
        
        print(f"\n✅ 网格搜索完成!")
        print(f"🏆 最佳评分: {self.best_score:.3f}")
        print(f"🎯 最佳参数: {self.best_params}")
        
        return self.best_params, self.best_score
    
    def step_by_step_tuning(self):
        """
        逐步调优策略
        一次只调一个参数，其他参数保持默认值
        """
        print("🔄 开始逐步调优...")
        
        # 默认参数
        default_params = {
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
            'batch_size': 2000
        }
        
        # 参数调优顺序（按重要性排序）
        tuning_order = [
            ('covisit_window', [2, 3, 4, 5]),
            ('recent_k', [3, 5, 7, 10]),
            ('recall_cap', [400, 600, 800, 1000]),
            ('covisit_top_per_a', [100, 150, 200, 300]),
            ('cand_per_recent', [20, 30, 40, 50]),
            ('tau_days', [7, 14, 21, 30])
        ]
        
        current_params = default_params.copy()
        best_score = 0
        
        for param_name, param_values in tuning_order:
            print(f"\n🎯 调优参数: {param_name}")
            print(f"📊 测试值: {param_values}")
            
            param_best_score = 0
            param_best_value = current_params[param_name]
            
            for value in param_values:
                test_params = current_params.copy()
                test_params[param_name] = value
                
                score, metrics = self.evaluate_params(test_params)
                
                if score > param_best_score:
                    param_best_score = score
                    param_best_value = value
                    print(f"  ✅ {param_name}={value}: 评分 {score:.3f} (新最佳)")
                else:
                    print(f"  📊 {param_name}={value}: 评分 {score:.3f}")
            
            # 更新当前参数
            current_params[param_name] = param_best_value
            best_score = param_best_score
            
            print(f"🎯 {param_name} 最佳值: {param_best_value}, 评分: {param_best_score:.3f}")
        
        print(f"\n✅ 逐步调优完成!")
        print(f"🏆 最终评分: {best_score:.3f}")
        print(f"🎯 最终参数: {current_params}")
        
        return current_params, best_score
    
    def save_results(self, filename='tuning_results.json'):
        """保存调优结果"""
        results_data = {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'all_results': self.results,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 调优结果已保存到: {filename}")

# 使用示例
if __name__ == "__main__":
    tuner = ParameterTuner()
    
    print("🎯 推荐系统参数调优工具")
    print("=" * 50)
    
    # 方法1: 网格搜索
    print("\n🔍 方法1: 网格搜索")
    param_ranges = {
        'covisit_window': [2, 3, 4],
        'recent_k': [3, 5, 7],
        'recall_cap': [400, 600, 800],
        'covisit_top_per_a': [100, 150, 200]
    }
    
    best_params, best_score = tuner.grid_search(param_ranges, max_combinations=20)
    
    # 方法2: 逐步调优
    print("\n🔄 方法2: 逐步调优")
    tuner2 = ParameterTuner()
    best_params2, best_score2 = tuner2.step_by_step_tuning()
    
    # 保存结果
    tuner.save_results('grid_search_results.json')
    tuner2.save_results('step_by_step_results.json')
