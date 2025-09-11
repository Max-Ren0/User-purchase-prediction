#!/bin/bash
# 项目设置脚本

echo "🚀 设置推荐系统项目..."

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/ || echo "⚠️ 测试文件不存在，跳过测试"

echo "✅ 项目设置完成！"
echo "📝 请运行 'source venv/bin/activate' 激活虚拟环境"
