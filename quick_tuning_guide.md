# 🎯 快速参数调优实战指南

## 🚀 **问题1: 快速模式快在哪里？**

### **📊 数据量对比**
| 模式 | 用户数量 | 计算量 | 运行时间 | 内存使用 |
|------|----------|--------|----------|----------|
| **FAST_MODE=True** | 5,000用户 | 1/20 | 2-3分钟 | 1/5 |
| **FAST_MODE=False** | 全部用户 | 100% | 20-30分钟 | 100% |

### **🔍 具体加速机制**

#### **1. 用户数量限制 (95%加速)**
```python
if FAST_MODE:
    N_SMOKE = 5000
    val_users = val_users[:N_SMOKE]  # 只处理前5000个用户
```
**效果**: 如果总共有10万用户，只处理5,000个，**减少95%的计算量**

#### **2. 参数值减小 (60-70%加速)**
```python
# 开发模式参数（较小值）
PARAMS = {
    'covisit_top_per_a': 120,    # 从200减少到120 (-40%)
    'recent_k': 3,               # 从5减少到3 (-40%) 
    'cand_per_recent': 24,       # 从40减少到24 (-40%)
    'per_cate_pool': 40,         # 从80减少到40 (-50%)
    'per_store_pool': 40,        # 从60减少到40 (-33%)
    'pop_pool': 1000,            # 从2000减少到1000 (-50%)
    'recall_cap': 400,           # 从600减少到400 (-33%)
    'batch_size': 1000,          # 从2000减少到1000 (-50%)
}
```

#### **3. 总体加速效果**
```
总加速比 = 用户数减少 × 参数减少
        = 20倍 × 0.6倍 = 12倍加速
```

---

## 🎯 **问题2: 参数调优怎么调？**

### **📋 调优策略总览**

| 方法 | 适用场景 | 时间成本 | 效果 | 难度 |
|------|----------|----------|------|------|
| **手动调优** | 快速验证 | 低 | 中等 | 简单 |
| **逐步调优** | 系统调优 | 中 | 高 | 中等 |
| **网格搜索** | 全面优化 | 高 | 最高 | 复杂 |

---

## 🚀 **方法1: 手动快速调优**

### **核心参数优先级**
```python
# 第1优先级：影响最大的参数
PRIORITY_1 = ['covisit_window', 'recent_k', 'recall_cap']

# 第2优先级：影响中等的参数  
PRIORITY_2 = ['covisit_top_per_a', 'cand_per_recent', 'tau_days']

# 第3优先级：影响较小的参数
PRIORITY_3 = ['per_cate_pool', 'per_store_pool', 'pop_pool']
```

### **快速调优步骤**
```python
# 步骤1: 调整核心参数
PARAMS = {
    'covisit_window': 3,      # 测试: 2, 3, 4, 5
    'recent_k': 5,            # 测试: 3, 5, 7, 10
    'recall_cap': 600,        # 测试: 400, 600, 800
}

# 步骤2: 运行FAST_MODE验证效果
FAST_MODE = True
# 运行notebook，观察结果

# 步骤3: 记录最佳组合
BEST_PARAMS = {
    'covisit_window': 3,      # 最佳值
    'recent_k': 5,            # 最佳值
    'recall_cap': 600,        # 最佳值
}
```

---

## 🔄 **方法2: 逐步调优**

### **调优顺序**
```python
# 第1轮: 共现参数
for covisit_window in [2, 3, 4, 5]:
    # 测试效果，记录最佳值

# 第2轮: 用户行为参数  
for recent_k in [3, 5, 7, 10]:
    # 基于第1轮最佳值，测试recent_k

# 第3轮: 召回容量参数
for recall_cap in [400, 600, 800, 1000]:
    # 基于前两轮最佳值，测试recall_cap
```

### **具体实施**
```python
# 使用我提供的调优脚本
from parameter_tuning_practical import ParameterTuner

tuner = ParameterTuner()

# 逐步调优
best_params, best_score = tuner.step_by_step_tuning()
```

---

## 🔍 **方法3: 网格搜索**

### **搜索空间定义**
```python
param_ranges = {
    'covisit_window': [2, 3, 4, 5],
    'recent_k': [3, 5, 7, 10], 
    'recall_cap': [400, 600, 800],
    'covisit_top_per_a': [100, 150, 200, 300]
}

# 总组合数: 4 × 4 × 3 × 4 = 192种
# 建议限制在50种以内进行测试
```

### **自动搜索**
```python
tuner = ParameterTuner()
best_params, best_score = tuner.grid_search(param_ranges, max_combinations=50)
```

---

## 📊 **调优效果评估**

### **评估指标**
```python
def evaluate_performance(params):
    """评估参数效果"""
    
    # 1. 召回率 (40%权重)
    recall_score = calculate_recall_at_k(candidates, k=50)
    
    # 2. 多样性 (20%权重)  
    diversity_score = calculate_diversity(candidates)
    
    # 3. 计算效率 (20%权重)
    efficiency_score = 1.0 / execution_time
    
    # 4. 覆盖率 (20%权重)
    coverage_score = calculate_item_coverage(candidates)
    
    # 综合评分
    total_score = (0.4 * recall_score + 
                   0.2 * diversity_score + 
                   0.2 * efficiency_score + 
                   0.2 * coverage_score)
    
    return total_score
```

### **快速验证方法**
```python
# 使用FAST_MODE快速验证参数效果
def quick_validate_params(params):
    """快速验证参数"""
    
    # 1. 设置参数
    PARAMS.update(params)
    
    # 2. 运行FAST_MODE
    FAST_MODE = True
    # 运行1_recall.ipynb
    
    # 3. 检查结果
    if len(candidates) > 0:
        avg_cands = len(candidates) / len(val_users)
        print(f"平均每用户候选数: {avg_cands:.1f}")
        
        # 检查召回策略覆盖率
        print(f"复购召回覆盖率: {(candidates['score_rebuy'] > 0).mean():.1%}")
        print(f"协同过滤覆盖率: {(candidates['score_covisit'] > 0).mean():.1%}")
        
        return True
    else:
        print("❌ 未生成候选，参数可能有问题")
        return False
```

---

## ⚡ **实用调优建议**

### **第1步: 快速验证**
```python
# 1. 保持FAST_MODE = True
# 2. 调整1-2个核心参数
# 3. 运行验证效果
# 4. 记录最佳组合
```

### **第2步: 系统调优**
```python
# 1. 使用逐步调优方法
# 2. 按优先级顺序调优参数
# 3. 每次只调一个参数
# 4. 记录每次调优结果
```

### **第3步: 最终验证**
```python
# 1. 使用最佳参数组合
# 2. 关闭FAST_MODE进行完整测试
# 3. 验证最终效果
# 4. 保存最佳配置
```

---

## 🎯 **立即行动建议**

### **现在就开始调优：**

1. **保持 `FAST_MODE = True`**
2. **调整核心参数**：
   ```python
   # 测试这些参数组合
   PARAMS = {
       'covisit_window': 3,      # 测试: 2, 3, 4
       'recent_k': 5,            # 测试: 3, 5, 7  
       'recall_cap': 600,        # 测试: 400, 600, 800
   }
   ```
3. **运行notebook观察效果**
4. **记录最佳参数组合**
5. **最终生产时使用最佳参数**

### **调优时间规划：**
- **第1天**: 快速验证核心参数
- **第2天**: 系统调优其他参数  
- **第3天**: 最终验证和保存配置

**这样既保证了调优效果，又控制了时间成本！**
