# TTS API 调试指南

## 当前状态

根据测试结果：
- ✅ API 调用成功（返回 200）
- ❌ 无法提取音频数据（响应结构解析问题）

## 问题分析

1. **SDK 响应**：`output.choices` 是 `None`，说明响应结构可能不同
2. **HTTP 响应**：返回 200，但 `output` 结构需要进一步检查

## 调试步骤

### 1. 运行调试脚本查看实际响应结构

```bash
conda activate ai-streamer
python tests/test_tts_debug.py
```

这个脚本会：
- 测试 SDK 方法
- 测试 HTTP API 方法
- 打印完整的响应结构
- 显示所有可用的属性

### 2. 根据输出调整代码

运行 `test_tts_debug.py` 后，查看：
- `audio_url` 是否存在
- `audio` 字段的类型和结构
- `output` 中的其他字段

### 3. 已实现的修复

代码已经更新为：
- ✅ 优先检查 `audio_url`（TTS API 通常返回 URL）
- ✅ 处理 `output.choices` 为 `None` 的情况
- ✅ 添加详细的日志输出
- ✅ 支持多种响应格式

## 下一步

运行 `test_tts_debug.py` 并分享输出，我会根据实际响应结构进一步修复代码。
