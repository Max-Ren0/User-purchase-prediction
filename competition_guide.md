# 🏆 算法比赛完整指南

## 🎯 比赛策略总览

### **开发阶段 vs 生产阶段**

| 阶段 | FAST_MODE | 用户数量 | 运行时间 | 用途 |
|------|-----------|----------|----------|------|
| **开发阶段** | `True` | 5,000 | 2-3分钟 | 参数调优、流程验证 |
| **生产阶段** | `False` | 全部 | 20-30分钟 | 最终提交 |

---

## 📋 完整比赛流程

### **第1步: 开发调试 (当前)**
```python
# 在 1_recall.ipynb 中设置
FAST_MODE = True  # 快速验证

# 运行所有notebooks进行快速测试
# 时间: 5-10分钟
# 目的: 验证流程、调优参数
```

### **第2步: 参数调优**
```python
# 基于FAST_MODE结果，找到最佳参数组合
# 记录最优参数到 competition_config.py

OPTIMAL_PARAMS = {
    'covisit_window': 3,      # 调优后的最佳值
    'recent_k': 5,
    'recall_cap': 600,
    # ... 其他参数
}
```

### **第3步: 生产运行 (最终提交)**
```python
# 在 1_recall.ipynb 中设置
FAST_MODE = False  # 关闭快速模式

# 使用调优后的参数
PARAMS = OPTIMAL_PARAMS

# 运行完整流程
# 时间: 20-30分钟
# 目的: 生成最终提交文件
```

---

## 🚀 自动化脚本使用

### **方法1: 使用配置管理脚本**
```python
from competition_config import CompetitionConfig

config = CompetitionConfig()

# 切换到开发模式
config.set_mode('development')
# 运行notebooks...

# 切换到生产模式  
config.set_mode('production')
# 运行notebooks...
```

### **方法2: 使用工作流程脚本**
```python
from competition_workflow import CompetitionWorkflow

workflow = CompetitionWorkflow()

# 完整流水线
workflow.full_pipeline()

# 或者分阶段执行
workflow.development_phase()  # 开发阶段
workflow.production_phase()   # 生产阶段
```

---

## ⚙️ 关键配置修改

### **开发模式配置**
```python
# 在 1_recall.ipynb 第一个cell
FAST_MODE = True
N_SMOKE = 5000  # 只处理5000个用户

# 参数设置（较小值，快速运行）
PARAMS = {
    'covisit_window': 2,
    'recent_k': 3,
    'recall_cap': 300,
    # ... 其他参数
}
```

### **生产模式配置**
```python
# 在 1_recall.ipynb 第一个cell
FAST_MODE = False  # 关闭快速模式

# 参数设置（调优后的最佳值）
PARAMS = {
    'covisit_window': 3,      # 调优后的值
    'recent_k': 5,
    'recall_cap': 600,
    # ... 其他参数
}
```

---

## 📊 时间规划建议

### **开发阶段 (1-2天)**
- **第1天**: 快速验证流程，确保代码无错误
- **第2天**: 参数调优，找到最佳配置

### **生产阶段 (比赛前1天)**
- **最终运行**: 使用完整数据和最优参数
- **结果验证**: 检查提交文件格式和内容
- **备份保存**: 保存所有中间结果

---

## 🔧 具体操作步骤

### **步骤1: 当前开发阶段**
```bash
# 1. 确保FAST_MODE = True
# 2. 运行所有notebooks验证流程
# 3. 记录运行时间和效果

python competition_workflow.py
# 选择: workflow.development_phase()
```

### **步骤2: 参数调优**
```python
# 基于开发阶段结果，调整参数
# 在 competition_config.py 中更新参数

# 测试不同参数组合
# 记录最佳配置
```

### **步骤3: 最终生产运行**
```bash
# 1. 设置 FAST_MODE = False
# 2. 使用最优参数
# 3. 运行完整流程

python competition_workflow.py
# 选择: workflow.production_phase()
```

---

## 📄 提交文件检查

### **最终输出文件**
- `submit_long.csv`: 长格式提交文件
- `submit_wide.csv`: 宽格式提交文件

### **文件格式验证**
```python
# 检查提交文件
submit_df = pd.read_csv('submit_wide.csv')
print(f"用户数量: {len(submit_df)}")
print(f"每用户推荐数: {submit_df.shape[1] - 1}")  # 减去用户ID列
print(f"推荐商品范围: {submit_df.iloc[:, 1:].values.min()} - {submit_df.iloc[:, 1:].values.max()}")
```

---

## ⚠️ 注意事项

### **开发阶段**
- ✅ 使用 `FAST_MODE = True` 快速验证
- ✅ 参数可以设置较小值
- ✅ 重点关注流程正确性

### **生产阶段**
- ❌ 必须设置 `FAST_MODE = False`
- ❌ 必须使用完整数据
- ❌ 必须使用调优后的参数
- ✅ 预计运行时间 20-30分钟

### **备份策略**
- 保存开发阶段的中间结果
- 记录最优参数配置
- 备份最终提交文件

---

## 🎯 总结

**您的比赛策略应该是：**

1. **现在**: 继续使用 `FAST_MODE = True` 进行开发和调优
2. **调优完成**: 记录最佳参数配置
3. **比赛前**: 设置 `FAST_MODE = False`，使用完整数据运行
4. **最终**: 生成提交文件，验证格式正确性

**这样既保证了开发效率，又确保了最终结果的完整性！**
