#!/bin/bash
# 创建 GitHub 远程仓库并推送代码

set -e

REPO_NAME="ai-streamer-demo"
GITHUB_USER="${GITHUB_USER:-}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

if [ -z "$GITHUB_USER" ]; then
    echo "❌ 请设置 GITHUB_USER 环境变量"
    echo "   export GITHUB_USER=your-username"
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 请设置 GITHUB_TOKEN 环境变量"
    echo "   获取 Token: https://github.com/settings/tokens"
    echo "   需要权限: repo"
    exit 1
fi

echo "📦 创建 GitHub 仓库: $REPO_NAME"

# 创建仓库
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"private\":false,\"description\":\"24/7 AI Streamer Demo - FastAPI + Aliyun Qwen + CosyVoice\"}")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$REPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 201 ]; then
    echo "✅ 仓库创建成功"
    
    # 添加远程仓库
    git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git" 2>/dev/null || \
    git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
    
    echo "✅ 已添加远程仓库"
    
    # 推送代码
    echo "📤 推送代码到远程仓库..."
    git push -u origin main
    
    echo "✅ 完成！仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
else
    echo "❌ 创建仓库失败 (HTTP $HTTP_CODE)"
    echo "$BODY"
    exit 1
fi
