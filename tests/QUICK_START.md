# 快速测试指南

## 问题：TTS API 返回 400 "task can not be null"

根据测试结果，dashscope TTS API 需要 `task` 参数。已更新代码尝试多种格式。

## 快速测试步骤

### 1. 确保环境已激活并安装依赖

```bash
conda activate ai-streamer
# 如果 requests 未安装，运行：
pip install requests
```

### 2. 测试配置

```bash
python tests/test_config.py
```

### 3. 测试 TTS API（关键！）

**方法 A：使用 SDK 测试**
```bash
python tests/test_tts_sdk.py
```

**方法 B：直接测试 HTTP API（包含 task 参数）**
```bash
python tests/test_tts_api_direct.py
```

这个脚本会尝试：
1. 包含 `task: "tts"` 参数的格式
2. 使用 `input` 和 `parameters` 结构的格式
3. 使用 dashscope SDK 的格式
4. 原始格式（作为后备）

### 4. 如果找到可用的格式

查看 `test_tts_api_direct.py` 的输出，找到返回 200 的格式，然后：

1. 检查 `ai_service.py` 中的 `text_to_speech` 方法
2. 确保使用了正确的请求格式
3. 代码已经包含了多种格式的尝试，会自动使用第一个成功的格式

## 当前修复

已在 `ai_service.py` 中更新了 TTS API 调用：

1. **优先使用 dashscope SDK**：尝试 `dashscope.Audio.call()`
2. **HTTP 请求后备**：如果 SDK 不可用，尝试三种不同的请求格式：
   - 包含 `task: "tts"` 参数
   - 使用 `input` 和 `parameters` 结构
   - 原始格式

## 下一步

运行测试脚本，查看哪个格式成功，然后我们可以进一步优化代码。
