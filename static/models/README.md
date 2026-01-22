# Live2D 模型目录

## 如何添加 Live2D 模型

1. **下载 Live2D 模型文件**
   - 模型文件格式：`.model3.json` (Cubism 3.0+)
   - 确保包含所有相关的纹理文件（.png）和动作文件

2. **放置模型文件**
   - 将整个模型文件夹（包含 .model3.json 和所有资源文件）放到此目录
   - 例如：`static/models/my-model/model.model3.json`

3. **配置模型路径**
   - 在 `static/app.js` 中修改 `getModelPath()` 方法：
   ```javascript
   getModelPath() {
       return '/static/models/my-model/model.model3.json';
   }
   ```

## 获取免费 Live2D 模型

### 官方示例模型
- 访问 [Live2D Cubism SDK](https://www.live2d.com/sdk/download/cubism-sdk/)
- 下载 SDK 后，示例模型在 `Samples/Resources` 目录

### 社区资源
- 搜索 "Live2D free model download"
- 访问 Live2D 相关社区和论坛

## 注意事项

- 模型文件必须支持 Cubism 3.0+ 格式（.model3.json）
- 确保所有资源文件（纹理、动作等）都在同一目录或正确路径
- 模型文件可能较大，注意加载时间

## 当前状态

如果没有模型文件，页面会显示占位符文本，但所有其他功能（音频播放、WebSocket 连接等）仍然正常工作。
