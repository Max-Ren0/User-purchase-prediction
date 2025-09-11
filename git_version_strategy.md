# 📚 Git版本管理策略 - 算法比赛项目

## 🎯 **版本管理最佳实践**

### **核心原则：**
1. **每个重要里程碑都要提交**
2. **清晰的提交信息**
3. **合理的分支策略**
4. **标签管理重要版本**

---

## 🚀 **推荐的分支策略**

### **主分支结构：**
```
main (生产分支)
├── develop (开发分支)
├── feature/optimization (优化分支)
├── feature/parameter-tuning (参数调优分支)
├── feature/bayesian-optimization (贝叶斯优化分支)
└── hotfix/ (紧急修复分支)
```

### **分支用途：**
- **main**: 稳定可运行版本
- **develop**: 开发集成分支
- **feature/**: 功能开发分支
- **hotfix/**: 紧急修复分支

---

## 📋 **提交策略**

### **提交频率：**
| 阶段 | 提交频率 | 提交内容 |
|------|----------|----------|
| **开发阶段** | 每2-3小时 | 功能完成、测试通过 |
| **调优阶段** | 每次调优 | 参数更新、结果记录 |
| **优化阶段** | 每次优化 | 性能提升、代码重构 |
| **生产阶段** | 每次部署 | 最终版本、提交文件 |

### **提交信息格式：**
```bash
# 功能开发
feat: 添加贝叶斯优化参数调优功能

# 性能优化
perf: 优化召回算法性能，提升3倍速度

# 参数调优
tune: 调优covisit_window参数，从3改为4

# 修复bug
fix: 修复KeyError: 'irank'错误

# 文档更新
docs: 更新README和参数调优指南

# 重构代码
refactor: 重构候选生成函数，提高可读性
```

---

## 🏷️ **标签管理策略**

### **版本标签：**
```bash
# 开发版本
v0.1.0-dev          # 初始开发版本
v0.2.0-dev          # 基础功能完成
v0.3.0-dev          # 性能优化完成

# 调优版本
v0.4.0-tune         # 参数调优完成
v0.5.0-tune         # 贝叶斯优化完成

# 生产版本
v1.0.0-prod         # 生产环境版本
v1.1.0-prod         # 最终提交版本
```

### **标签创建：**
```bash
# 创建标签
git tag -a v0.1.0-dev -m "初始开发版本：基础召回功能"
git tag -a v0.2.0-dev -m "性能优化版本：3倍速度提升"
git tag -a v1.0.0-prod -m "生产版本：最终提交"

# 推送标签
git push origin --tags
```

---

## 📊 **具体实施步骤**

### **第1步: 初始化Git仓库**
```bash
# 初始化仓库
git init

# 添加远程仓库
git remote add origin https://github.com/yourusername/recommendation-system.git

# 创建.gitignore
echo "*.pyc
__pycache__/
.ipynb_checkpoints/
*.log
.DS_Store
env/
venv/
*.pkl
*.parquet
x/
" > .gitignore
```

### **第2步: 创建分支结构**
```bash
# 创建主分支
git checkout -b main
git add .
git commit -m "feat: 初始项目结构"

# 创建开发分支
git checkout -b develop
git push -u origin develop

# 创建功能分支
git checkout -b feature/optimization
git checkout -b feature/parameter-tuning
git checkout -b feature/bayesian-optimization
```

### **第3步: 开发阶段提交**
```bash
# 功能开发完成
git add .
git commit -m "feat: 完成多路召回算法实现"
git push origin feature/optimization

# 性能优化完成
git add .
git commit -m "perf: 优化召回算法，提升3倍性能"
git push origin feature/optimization

# 合并到开发分支
git checkout develop
git merge feature/optimization
git push origin develop
```

### **第4步: 调优阶段提交**
```bash
# 参数调优完成
git add .
git commit -m "tune: 完成参数调优，recall@50提升15%"
git push origin feature/parameter-tuning

# 贝叶斯优化完成
git add .
git commit -m "tune: 完成贝叶斯优化，找到最佳参数组合"
git push origin feature/bayesian-optimization
```

### **第5步: 生产阶段提交**
```bash
# 合并到主分支
git checkout main
git merge develop
git tag -a v1.0.0-prod -m "生产版本：最终提交"
git push origin main --tags
```

---

## 📝 **README版本管理**

### **版本历史记录：**
```markdown
## 📚 版本历史

### v1.0.0-prod (2024-01-15)
- ✅ 完成多路召回算法
- ✅ 完成参数调优
- ✅ 完成贝叶斯优化
- ✅ 生成最终提交文件

### v0.5.0-tune (2024-01-14)
- ✅ 完成贝叶斯优化实现
- ✅ 智能FAST_MODE策略
- ✅ 参数调优指南

### v0.4.0-tune (2024-01-13)
- ✅ 完成参数调优
- ✅ 性能优化完成
- ✅ 调优结果记录

### v0.3.0-dev (2024-01-12)
- ✅ 性能优化完成
- ✅ 3倍速度提升
- ✅ 内存优化

### v0.2.0-dev (2024-01-11)
- ✅ 基础功能完成
- ✅ 多路召回实现
- ✅ 基础测试通过

### v0.1.0-dev (2024-01-10)
- ✅ 项目初始化
- ✅ 基础结构搭建
- ✅ 数据预处理完成
```

---

## 🎯 **比赛项目特殊考虑**

### **提交文件管理：**
```bash
# 提交文件不提交到Git
echo "submit_*.csv" >> .gitignore
echo "*.pkl" >> .gitignore
echo "x/" >> .gitignore

# 但可以提交示例文件
echo "submit_example.csv" >> .gitignore
```

### **敏感信息管理：**
```bash
# 创建环境变量文件
echo "NOTION_API_KEY=your_key_here" > .env
echo ".env" >> .gitignore

# 创建配置模板
cp .env .env.example
# 编辑.env.example，移除敏感信息
```

### **结果文件管理：**
```bash
# 创建结果目录
mkdir results/
echo "results/*.csv" >> .gitignore
echo "results/*.json" >> .gitignore

# 但可以提交示例结果
echo "results/example_*.csv" >> .gitignore
```

---

## 🚀 **自动化脚本**

### **提交脚本：**
```bash
#!/bin/bash
# commit.sh - 自动化提交脚本

# 获取提交信息
read -p "请输入提交信息: " commit_msg

# 添加文件
git add .

# 提交
git commit -m "$commit_msg"

# 推送
git push origin $(git branch --show-current)

echo "✅ 提交完成！"
```

### **版本发布脚本：**
```bash
#!/bin/bash
# release.sh - 版本发布脚本

# 获取版本号
read -p "请输入版本号 (如 v1.0.0): " version

# 创建标签
git tag -a $version -m "Release $version"

# 推送标签
git push origin $version

echo "✅ 版本 $version 发布完成！"
```

---

## 📊 **最佳实践总结**

### **✅ 应该提交的：**
- 源代码文件
- 配置文件
- 文档文件
- 测试文件
- 示例文件

### **❌ 不应该提交的：**
- 提交文件 (submit_*.csv)
- 模型文件 (*.pkl)
- 数据文件 (*.parquet)
- 环境变量 (.env)
- 临时文件

### **🎯 提交频率建议：**
- **开发阶段**: 每2-3小时提交一次
- **调优阶段**: 每次调优完成后提交
- **优化阶段**: 每次优化完成后提交
- **生产阶段**: 每次部署前提交

### **📝 提交信息建议：**
- 使用清晰的动词开头
- 描述具体做了什么
- 包含性能提升数据
- 包含测试结果

**这样既保证了代码版本管理，又展示了项目进展！**
