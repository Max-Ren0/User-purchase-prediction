# 用户购买预测推荐系统

## 🎯 项目简介
基于多路召回的推荐系统，使用贝叶斯优化进行参数调优，从原始CSV数据到最终预测结果的完整管道。实现了智能分层抽样、多路召回、排序模型和留一验证评估。

## 📁 项目结构
```
用户购买预测/
├── 📁 data/                           # 数据目录
│   ├── Antai_hackathon_train.csv      # 训练数据
│   ├── Antai_hackathon_attr.csv       # 商品属性
│   └── dianshang_test.csv             # 测试数据
├── 📁 notebooks/                      # 核心算法
│   ├── 0_prep.ipynb                   # 数据预处理 + 智能抽样
│   ├── 1_recall.ipynb                 # 多路召回算法
│   ├── 2_rank.ipynb                   # 排序模型训练
│   ├── 3_eval.ipynb                   # 评估分析
│   └── 4_online.ipynb                 # 在线推理
├── 📄 smart_sampling.py               # 智能分层抽样算法
├── 📄 leave_one_out_eval.py           # 留一验证评估函数
├── 📄 recall_eval_functions.py        # 召回评估函数
├── 📄 reco_pipeline_utils.py          # 工具函数
├── 📄 competition_config.json         # 配置文件
├── 📄 requirements.txt                # 依赖包
└── 📄 README.md                       # 项目说明
```

## 🚀 快速开始

### 环境配置
```bash
# 安装依赖
pip install -r requirements.txt

# 启动Jupyter
jupyter notebook
```

### 运行流程
```bash
# 1. 数据预处理 + 智能抽样（1万用户）
jupyter notebook notebooks/0_prep.ipynb

# 2. 多路召回
jupyter notebook notebooks/1_recall.ipynb

# 3. 排序模型 + 留一验证评估
jupyter notebook notebooks/2_rank.ipynb

# 4. 评估分析
jupyter notebook notebooks/3_eval.ipynb

# 5. 在线推理 + 生成提交文件
jupyter notebook notebooks/4_online.ipynb
```

## 📊 核心特性

### 智能抽样策略
- **分层抽样**: 按购买活跃度、商品多样性、时间分布分层
- **质量保证**: 分布保持度 > 0.8，确保抽样代表性
- **统一数据**: 所有模块使用相同的抽样数据，避免不一致

### 多路召回策略
1. **🔄 复购召回**: 基于用户历史购买 + 时间衰减
2. **🔗 协同过滤召回**: 基于商品共现关系
3. **🏪 个性化热门**: 用户偏好类目/店铺热门
4. **🌍 全局热门**: 冷启动补充

### 性能优化
- **贝叶斯优化**: 自动调优超参数
- **向量化计算**: 大幅提升计算速度
- **内存优化**: 减少内存占用
- **批处理**: 高效处理大规模数据

### 评估指标
- **HR@50**: 命中率
- **MRR@50**: 平均倒数排名
- **NDCG@50**: 归一化折扣累积增益

## 🔧 环境要求

### Python包依赖
```bash
pip install pandas numpy scikit-learn scikit-optimize lightgbm tqdm
```

### 系统要求
- Python 3.7+
- 内存: 8GB+ (推荐16GB)
- 存储: 2GB+ 可用空间

## 📈 性能表现

### 当前性能
- **HR@50**: 27.88%
- **MRR@50**: 22.32%
- **NDCG@50**: 23.60%
- **综合评分**: 0.258

### 优化后参数
```json
{
  "covisit_window": 4,
  "covisit_top_per_a": 317,
  "recent_k": 4,
  "cand_per_recent": 69,
  "tau_days": 11,
  "per_cate_pool": 38,
  "per_store_pool": 96,
  "pop_pool": 4863,
  "recall_cap": 866
}
```

## 🛠️ 开发指南

### 添加新的召回策略
1. 在 `recall_eval_functions.py` 中添加新函数
2. 在 `build_candidates_ultra_fast` 中集成
3. 更新参数配置

### 自定义评估指标
1. 在 `reco_pipeline_utils.py` 中添加新指标
2. 在 `recall_eval_functions.py` 中调用
3. 更新评估逻辑

### 参数调优
1. 修改 `competition_config.json` 中的搜索空间
2. 运行优化脚本
3. 更新配置文件中的参数

## 📝 使用说明

### 数据格式
- **训练数据**: 用户购买记录，包含用户ID、商品ID、时间等
- **商品属性**: 商品ID、类目ID、店铺ID
- **测试数据**: 待预测的用户商品对

### 输出文件
- **候选文件**: 每个用户的推荐候选商品
- **评估结果**: 性能指标和可视化
- **提交文件**: 最终预测结果

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请创建 Issue 或联系项目维护者。