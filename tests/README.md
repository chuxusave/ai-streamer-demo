# 测试脚本说明

本目录包含所有关键节点的测试脚本，用于定位和调试问题。

## 测试脚本列表

### 1. `test_config.py` - 配置测试
测试配置是否能正确加载。
```bash
python tests/test_config.py
```

### 2. `test_state.py` - 状态管理测试
测试播放列表和状态管理功能。
```bash
python tests/test_state.py
```

### 3. `test_llm.py` - LLM 脚本生成测试
测试 Qwen-Turbo 是否能正确生成脚本。
```bash
python tests/test_llm.py
```

### 4. `test_tts_api_direct.py` - TTS API 直接测试
**重要**：这个脚本会测试不同的 TTS API 调用方式，帮助定位 API 调用问题。
```bash
python tests/test_tts_api_direct.py
```

### 5. `test_tts.py` - TTS 合成测试
测试完整的 TTS 合成流程。
```bash
python tests/test_tts.py
```

### 6. `test_api.py` - API 端点测试
测试 FastAPI 端点是否正常工作。
```bash
python tests/test_api.py
```

## 运行所有测试

```bash
python tests/run_all_tests.py
```

## 调试流程

当遇到错误时，按以下顺序运行测试：

1. **首先运行配置测试**：确保环境变量正确
   ```bash
   python tests/test_config.py
   ```

2. **运行状态管理测试**：确保基础功能正常
   ```bash
   python tests/test_state.py
   ```

3. **运行 LLM 测试**：确保脚本生成正常
   ```bash
   python tests/test_llm.py
   ```

4. **运行 TTS API 直接测试**：**这是调试 TTS 问题的关键**
   ```bash
   python tests/test_tts_api_direct.py
   ```
   这个脚本会尝试不同的 API 调用方式，并显示详细的错误信息。

5. **运行完整 TTS 测试**：如果 API 测试通过
   ```bash
   python tests/test_tts.py
   ```

6. **运行 API 端点测试**：测试 HTTP 接口
   ```bash
   python tests/test_api.py
   ```

## 常见问题

### TTS API 返回 400 Bad Request

运行 `test_tts_api_direct.py` 查看详细的错误信息。可能的原因：
- API Key 无效或过期
- 请求格式不正确
- 模型名称不正确
- 参数不匹配 API 要求

### 配置加载失败

检查 `.env` 文件是否存在，并确保包含：
- `DASHSCOPE_API_KEY`
- `ALIYUN_ACCESS_KEY_ID`
- `ALIYUN_ACCESS_KEY_SECRET`
