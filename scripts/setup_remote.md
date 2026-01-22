# 设置远程仓库指南

## 方式 1: 手动创建（推荐）

### 步骤 1: 在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `ai-streamer-demo`
   - **Description**: `24/7 AI Streamer Demo - FastAPI + Aliyun Qwen + CosyVoice`
   - **Visibility**: 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"（本地已有文件）
3. 点击 "Create repository"

### 步骤 2: 添加远程仓库并推送

创建仓库后，GitHub 会显示仓库 URL，然后运行：

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin git@github.com:chuxusave/ai-streamer-demo.git

# 推送代码
git push -u origin main
```

## 方式 2: 使用脚本自动创建

如果你有 GitHub Personal Access Token：

1. 获取 Token：
   - 访问 https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 选择 `repo` 权限
   - 复制生成的 token

2. 设置环境变量并运行脚本：

```bash
export GITHUB_USER=your-username
export GITHUB_TOKEN=your-token
./scripts/create_remote_repo.sh
```

## 方式 3: 使用 GitHub CLI

如果安装了 GitHub CLI：

```bash
# 安装 GitHub CLI (macOS)
brew install gh

# 登录
gh auth login

# 创建仓库并推送
gh repo create ai-streamer-demo --public --source=. --remote=origin --push
```

## 验证

推送成功后，访问你的 GitHub 仓库页面确认所有文件都已上传。
