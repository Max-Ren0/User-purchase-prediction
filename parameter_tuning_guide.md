# 🎯 推荐系统参数调优完全指南

## 📋 参数总览

基于您的推荐系统，以下是所有关键参数及其调优策略：

```python
PARAMS = {
    'covisit_window': 3,           # 共现滑窗大小
    'covisit_top_per_a': 200,      # 每个商品保留TopK共现关系
    'recent_k': 5,                 # 用户最近K个商品作为种子
    'cand_per_recent': 40,         # 每个种子商品扩展N个候选
    'tau_days': 14,                # 复购时间衰减参数(天)
    'user_top_cates': 3,           # 用户偏好类目数
    'user_top_stores': 3,          # 用户偏好店铺数
    'per_cate_pool': 80,           # 每个类目热门池大小
    'per_store_pool': 60,          # 每个店铺热门池大小
    'pop_pool': 2000,              # 全局热门池大小
    'recall_cap': 600,             # 单用户候选上限
    'batch_size': 2000,            # 批处理大小
}
```

---

## 🔬 参数详细分析与调优策略

### 1️⃣ **共现相关参数**

#### **covisit_window** (共现滑窗)
- **作用**: 定义商品共现的时间窗口大小
- **当前值**: 3
- **调优范围**: 2-8
- **选择策略**:
  ```python
  # 基于用户行为模式选择
  avg_session_length = train_vis.groupby('buyer_admin_id').size().mean()
  
  if avg_session_length < 5:
      covisit_window = 2-3      # 短会话用户
  elif avg_session_length < 10:
      covisit_window = 3-5      # 中等会话用户  
  else:
      covisit_window = 5-8      # 长会话用户
  ```

#### **covisit_top_per_a** (共现关系数量)
- **作用**: 每个商品保留的最大共现关系数
- **当前值**: 200
- **调优范围**: 50-500
- **选择策略**:
  ```python
  # 基于商品流行度分布
  item_popularity = train_vis['item_id'].value_counts()
  median_pop = item_popularity.median()
  
  if median_pop < 10:
      covisit_top_per_a = 50-100    # 长尾商品多
  elif median_pop < 50:
      covisit_top_per_a = 100-200   # 中等分布
  else:
      covisit_top_per_a = 200-500   # 热门商品集中
  ```

### 2️⃣ **用户行为相关参数**

#### **recent_k** (最近商品数)
- **作用**: 用户最近K个商品作为协同过滤种子
- **当前值**: 5
- **调优范围**: 3-10
- **选择策略**:
  ```python
  # 基于用户活跃度
  user_activity = train_vis.groupby('buyer_admin_id').size()
  q75_activity = user_activity.quantile(0.75)
  
  if q75_activity < 10:
      recent_k = 3-5        # 低活跃用户
  elif q75_activity < 30:
      recent_k = 5-7        # 中等活跃用户
  else:
      recent_k = 7-10       # 高活跃用户
  ```

#### **cand_per_recent** (种子扩展数)
- **作用**: 每个种子商品扩展的候选数量
- **当前值**: 40
- **调优范围**: 20-100
- **选择策略**:
  ```python
  # 基于召回预算和精度要求
  total_users = train_vis['buyer_admin_id'].nunique()
  
  if total_users < 100000:
      cand_per_recent = 50-100      # 小规模，可以多召回
  elif total_users < 500000:
      cand_per_recent = 30-60       # 中规模，平衡召回
  else:
      cand_per_recent = 20-40       # 大规模，控制召回
  ```

### 3️⃣ **时间衰减参数**

#### **tau_days** (复购时间衰减)
- **作用**: 控制历史行为的时间衰减速度
- **当前值**: 14天
- **调优范围**: 7-30天
- **选择策略**:
  ```python
  # 基于商品复购周期分析
  def analyze_repurchase_cycle():
      user_item_times = train_vis.groupby(['buyer_admin_id', 'item_id'])['create_order_time'].apply(list)
      
      cycles = []
      for times in user_item_times:
          if len(times) > 1:
              times_sorted = sorted(times)
              for i in range(1, len(times_sorted)):
                  cycle = (times_sorted[i] - times_sorted[i-1]).days
                  cycles.append(cycle)
      
      if cycles:
          median_cycle = np.median(cycles)
          return median_cycle / 2  # 设为中位数的一半
      else:
          return 14  # 默认值
  
  tau_days = analyze_repurchase_cycle()
  ```

### 4️⃣ **个性化热门参数**

#### **user_top_cates/user_top_stores** (用户偏好数量)
- **作用**: 用户偏好的类目/店铺数量
- **当前值**: 3
- **调优范围**: 2-5
- **选择策略**:
  ```python
  # 基于用户偏好集中度
  user_cate_diversity = train_vis.groupby('buyer_admin_id')['item_id'].apply(
      lambda x: x.merge(item_attr, on='item_id')['cate_id'].nunique()
  ).mean()
  
  if user_cate_diversity < 3:
      user_top_cates = 2        # 偏好集中
  elif user_cate_diversity < 6:
      user_top_cates = 3        # 偏好中等
  else:
      user_top_cates = 4-5      # 偏好分散
  ```

#### **per_cate_pool/per_store_pool** (热门池大小)
- **作用**: 每个类目/店铺的热门商品池大小
- **当前值**: 80/60
- **调优范围**: 30-200
- **选择策略**:
  ```python
  # 基于类目/店铺内商品数量分布
  cate_item_count = item_attr.groupby('cate_id').size()
  median_cate_size = cate_item_count.median()
  
  per_cate_pool = min(200, max(30, int(median_cate_size * 0.1)))
  per_store_pool = min(150, max(20, int(median_cate_size * 0.08)))
  ```

### 5️⃣ **系统性能参数**

#### **recall_cap** (单用户候选上限)
- **作用**: 控制每个用户的最大候选数量
- **当前值**: 600
- **调优范围**: 200-1000
- **选择策略**:
  ```python
  # 基于下游排序模型容量和计算资源
  
  # 方法1: 基于排序模型容量
  if ranking_model_capacity < 1000:
      recall_cap = 200-400
  elif ranking_model_capacity < 5000:
      recall_cap = 400-600
  else:
      recall_cap = 600-1000
  
  # 方法2: 基于精度-效率平衡
  # 通过离线实验确定最优值
  ```

---

## 📊 参数调优实战方法

### **方法1: 网格搜索**

```python
def grid_search_params():
    """网格搜索最优参数组合"""
    
    # 定义搜索空间
    param_grid = {
        'covisit_window': [2, 3, 5],
        'recent_k': [3, 5, 7],
        'tau_days': [7, 14, 21],
        'recall_cap': [400, 600, 800]
    }
    
    best_score = 0
    best_params = None
    
    # 网格搜索
    for covisit_window in param_grid['covisit_window']:
        for recent_k in param_grid['recent_k']:
            for tau_days in param_grid['tau_days']:
                for recall_cap in param_grid['recall_cap']:
                    
                    params = {
                        'covisit_window': covisit_window,
                        'recent_k': recent_k,
                        'tau_days': tau_days,
                        'recall_cap': recall_cap,
                        # 其他参数使用默认值
                    }
                    
                    # 运行召回算法
                    score = evaluate_recall_performance(params)
                    
                    if score > best_score:
                        best_score = score
                        best_params = params
    
    return best_params, best_score
```

### **方法2: 贝叶斯优化**

```python
from skopt import gp_minimize
from skopt.space import Integer, Real

def bayesian_optimization():
    """使用贝叶斯优化调参"""
    
    # 定义搜索空间
    space = [
        Integer(2, 8, name='covisit_window'),
        Integer(3, 10, name='recent_k'),
        Integer(20, 100, name='cand_per_recent'),
        Real(7, 30, name='tau_days'),
        Integer(200, 1000, name='recall_cap')
    ]
    
    def objective(params):
        """目标函数"""
        param_dict = {
            'covisit_window': params[0],
            'recent_k': params[1], 
            'cand_per_recent': params[2],
            'tau_days': params[3],
            'recall_cap': params[4]
        }
        
        # 运行召回算法并评估
        score = evaluate_recall_performance(param_dict)
        return -score  # 最小化负分数 = 最大化分数
    
    # 执行优化
    result = gp_minimize(objective, space, n_calls=50, random_state=42)
    
    return result.x, -result.fun
```

### **方法3: 逐步调优**

```python
def step_by_step_tuning():
    """逐步调优策略"""
    
    # 1. 先调核心参数
    print("🔄 第一轮：调优核心召回参数")
    core_params = ['covisit_window', 'recent_k', 'tau_days']
    best_core = tune_params_subset(core_params)
    
    # 2. 再调扩展参数  
    print("🔄 第二轮：调优扩展参数")
    extend_params = ['cand_per_recent', 'covisit_top_per_a']
    best_extend = tune_params_subset(extend_params, base_params=best_core)
    
    # 3. 最后调性能参数
    print("🔄 第三轮：调优性能参数")
    perf_params = ['recall_cap', 'batch_size']
    best_perf = tune_params_subset(perf_params, base_params={**best_core, **best_extend})
    
    return {**best_core, **best_extend, **best_perf}
```

---

## 🎯 不同场景的推荐参数配置

### **场景1: 电商快消品**
```python
FAST_CONSUMER_PARAMS = {
    'covisit_window': 3,           # 购买决策快
    'recent_k': 3,                 # 关注最近偏好
    'tau_days': 7,                 # 快速衰减
    'user_top_cates': 2,           # 偏好相对固定
    'recall_cap': 400,             # 中等召回量
}
```

### **场景2: 3C数码产品**
```python
ELECTRONICS_PARAMS = {
    'covisit_window': 5,           # 研究周期长
    'recent_k': 7,                 # 考虑更多历史
    'tau_days': 30,                # 慢速衰减
    'user_top_cates': 4,           # 多品类需求
    'recall_cap': 800,             # 高召回量
}
```

### **场景3: 服装时尚**
```python
FASHION_PARAMS = {
    'covisit_window': 4,           # 季节性影响
    'recent_k': 5,                 # 平衡历史和趋势
    'tau_days': 14,                # 中等衰减
    'user_top_cates': 3,           # 风格相对稳定
    'recall_cap': 600,             # 标准召回量
}
```

---

## 📈 参数效果评估指标

### **召回效果指标**
```python
def evaluate_recall_performance(params):
    """评估召回效果"""
    
    # 运行召回算法
    candidates = run_recall_with_params(params)
    
    # 计算指标
    metrics = {
        'recall@50': calculate_recall_at_k(candidates, 50),
        'recall@100': calculate_recall_at_k(candidates, 100),
        'coverage': calculate_item_coverage(candidates),
        'diversity': calculate_diversity(candidates),
        'novelty': calculate_novelty(candidates),
    }
    
    # 综合评分
    score = (
        0.4 * metrics['recall@50'] +
        0.3 * metrics['recall@100'] + 
        0.1 * metrics['coverage'] +
        0.1 * metrics['diversity'] +
        0.1 * metrics['novelty']
    )
    
    return score, metrics
```

### **系统性能指标**
```python
def evaluate_system_performance(params):
    """评估系统性能"""
    
    start_time = time.time()
    memory_start = get_memory_usage()
    
    # 运行算法
    candidates = run_recall_with_params(params)
    
    end_time = time.time()
    memory_end = get_memory_usage()
    
    perf_metrics = {
        'execution_time': end_time - start_time,
        'memory_usage': memory_end - memory_start,
        'throughput': len(candidates) / (end_time - start_time),
        'candidates_per_user': len(candidates) / num_users
    }
    
    return perf_metrics
```

---

## 🔧 实用调参工具

### **参数敏感性分析**
```python
def parameter_sensitivity_analysis():
    """参数敏感性分析"""
    
    base_params = PARAMS.copy()
    sensitivity_results = {}
    
    for param_name in ['covisit_window', 'recent_k', 'tau_days', 'recall_cap']:
        param_scores = []
        
        # 获取参数范围
        if param_name == 'covisit_window':
            param_range = range(2, 9)
        elif param_name == 'recent_k':
            param_range = range(3, 11)
        elif param_name == 'tau_days':
            param_range = range(7, 31, 3)
        elif param_name == 'recall_cap':
            param_range = range(200, 1001, 100)
        
        # 测试每个值
        for param_value in param_range:
            test_params = base_params.copy()
            test_params[param_name] = param_value
            
            score, _ = evaluate_recall_performance(test_params)
            param_scores.append((param_value, score))
        
        sensitivity_results[param_name] = param_scores
    
    return sensitivity_results
```

### **参数推荐器**
```python
def recommend_parameters(dataset_stats):
    """基于数据集特征推荐参数"""
    
    recommendations = {}
    
    # 基于用户活跃度
    avg_user_items = dataset_stats['avg_items_per_user']
    if avg_user_items < 10:
        recommendations['recent_k'] = 3
        recommendations['recall_cap'] = 300
    elif avg_user_items < 30:
        recommendations['recent_k'] = 5
        recommendations['recall_cap'] = 600
    else:
        recommendations['recent_k'] = 7
        recommendations['recall_cap'] = 800
    
    # 基于商品流行度分布
    item_gini = dataset_stats['item_popularity_gini']
    if item_gini > 0.8:  # 高集中度
        recommendations['covisit_top_per_a'] = 100
        recommendations['per_cate_pool'] = 50
    else:  # 低集中度
        recommendations['covisit_top_per_a'] = 200
        recommendations['per_cate_pool'] = 80
    
    # 基于时间跨度
    time_span_days = dataset_stats['time_span_days']
    recommendations['tau_days'] = min(30, max(7, time_span_days // 10))
    
    return recommendations
```

---

## 💡 调参最佳实践

### **1. 调参顺序**
1. **数据分析** → 了解数据特征
2. **核心参数** → covisit_window, recent_k, tau_days
3. **扩展参数** → cand_per_recent, top_per_a
4. **性能参数** → recall_cap, batch_size
5. **细节参数** → user_top_cates, pool sizes

### **2. 验证策略**
- **时间切分**: 用历史数据预测未来
- **用户切分**: 训练集/验证集用户分离
- **交叉验证**: 多次随机切分验证稳定性

### **3. 调参技巧**
- **先粗调后细调**: 大范围搜索 → 小范围精调
- **单变量调优**: 一次只调一个参数
- **记录实验**: 详细记录每次实验结果
- **业务约束**: 考虑计算资源和响应时间限制

---

## 📋 总结

参数调优是一个**迭代过程**，需要结合：
1. **数据特征分析** - 了解用户行为和商品分布
2. **业务需求** - 平衡召回率、多样性和计算成本
3. **系统约束** - 考虑内存、计算时间等限制
4. **实验验证** - 通过A/B测试验证线上效果

建议您从**当前参数**开始，使用**逐步调优**的方法，重点关注**核心参数**（covisit_window, recent_k, tau_days），然后根据实际效果调整其他参数。

