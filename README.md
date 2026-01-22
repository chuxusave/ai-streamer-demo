# AI Streamer Demo

24/7 AI Digital Human Streamer - 一个自动生成内容并持续播报的数字人演示项目。

## 技术栈

- **Backend**: FastAPI (Python 3.11)
- **Environment**: Conda (Miniconda)
- **AI Services**: 
  - LLM: Aliyun Qwen (via `dashscope`)
  - TTS: Aliyun CosyVoice (via `dashscope`)
- **Frontend**: Simple HTML/JS with `pixi-live2d-display`
- **Storage**: In-memory Python lists (无数据库)

## 快速开始

### 1. 创建 Conda 环境

```bash
conda env create -f environment.yml
conda activate ai-streamer
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的阿里云凭证：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API keys
```

### 3. 启动服务器

```bash
python main.py
```

或者使用 uvicorn 直接运行：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问前端界面

打开浏览器访问: http://localhost:8000/

或者访问 API 文档: http://localhost:8000/docs

## API 端点

### REST API

- `GET /` - 根端点，返回 API 信息
- `GET /health` - 健康检查
- `GET /api/status` - 获取当前流状态
- `POST /api/start_stream` - 启动流（传入 topic 参数）

### WebSocket

- `WS /ws/stream` - 音频流推送端点

## 项目结构

```
ai-streamer-demo/
├── main.py              # FastAPI 主应用
├── config.py            # 配置管理
├── state.py             # 全局状态管理（内存播放列表）
├── ai_service.py        # AI 服务（LLM + TTS）
├── static/              # 前端静态文件
│   ├── index.html      # 前端页面
│   └── app.js          # 前端 JavaScript
├── environment.yml      # Conda 环境定义
├── .env.example         # 环境变量示例
└── README.md           # 本文件
```

## 开发计划

- [x] Step 1.1: 环境配置和基础代码
- [x] Step 2.1: LLM 脚本生成
- [x] Step 2.2: TTS 语音合成
- [x] Step 3.1: WebSocket 流循环（自动补充播放列表）
- [x] Step 4.1: 前端播放器

## 核心功能

### 自动补充播放列表（Auto-Refill）

当播放列表为空时，系统会自动：
1. 检测到播放列表为空（等待 2 秒后触发）
2. 使用当前主题生成新的营销文案（5 条）
3. 将文案转换为语音
4. 自动添加到播放列表
5. 继续流式推送音频

这确保了数字人可以 24/7 不间断播报。

## 前端使用说明

1. **启动流**：在输入框中输入主题（如"咖啡机"），点击"开始直播"
2. **观看直播**：数字人会开始播报相关内容，音频会自动播放
3. **自动补充**：当播放列表为空时，系统会自动生成新内容
4. **停止直播**：点击"停止直播"按钮

### Live2D 模型配置

**重要：** 页面需要 Live2D 模型文件才能显示数字人。

#### 方式 1: 使用测试模型（快速体验）

1. 下载一个免费的 Live2D 测试模型（.model3.json 格式）
2. 将模型文件放到 `static/models/` 目录
3. 在 `static/app.js` 中修改 `getModelPath()` 方法，返回模型路径：

```javascript
getModelPath() {
    return '/static/models/your-model.model3.json';
}
```

#### 方式 2: 使用占位符（当前默认）

如果没有模型文件，页面会显示占位符文本。功能仍然可以正常使用（音频播放、WebSocket 连接等），只是没有数字人动画。

#### 获取 Live2D 模型

- **官方示例模型**: 访问 [Live2D Cubism SDK](https://www.live2d.com/sdk/download/cubism-sdk/) 下载示例模型
- **免费模型**: 搜索 "Live2D free model" 或访问相关社区
- **商业模型**: 从 Live2D 官方商店购买

**注意**: 确保模型文件是 `.model3.json` 格式（Cubism 3.0+），并包含所有相关的纹理和动作文件。

当前前端已集成 `pixi-live2d-display`，但需要提供 Live2D 模型文件（.model3.json）才能显示数字人。

要使用 Live2D 模型：
1. 将 Live2D 模型文件放在 `static/models/` 目录
2. 在 `static/app.js` 中取消注释并配置模型路径：
   ```javascript
   this.model = await Live2DModel.from('/static/models/your-model.model3.json');
   ```

## 注意事项

- 本项目不使用 Docker，所有依赖通过 Conda 管理
- 不使用数据库，所有数据存储在内存中
- 数字人持续播报，不支持用户打断（Barge-in）
- 播放列表为空时自动生成新内容（无限循环）
- WebSocket 连接断开后，播放列表会继续在后台维护
- 前端需要 Live2D 模型文件才能显示数字人（音频播放不受影响）