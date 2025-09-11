#!/bin/bash
# Git工作流程脚本

# 获取提交信息
read -p "请输入提交信息: " commit_msg

# 获取分支名
branch=$(git branch --show-current)

# 添加文件
git add .

# 提交
git commit -m "$commit_msg"

# 推送
git push origin $branch

echo "✅ 提交完成！"
echo "📊 当前分支: $branch"
echo "💬 提交信息: $commit_msg"
