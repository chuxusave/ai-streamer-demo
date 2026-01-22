# Live2D 库加载问题解决方案

## 问题

如果 `pixi-live2d-display` 库无法从 CDN 加载，你需要手动下载并本地托管。

## 解决方案

### 方式 1: 下载并本地托管（推荐）

1. **下载库文件**：
   ```bash
   # 在项目根目录执行
   mkdir -p static/libs/pixi-live2d-display
   cd static/libs/pixi-live2d-display
   
   # 下载 UMD 构建文件
   curl -O https://unpkg.com/pixi-live2d-display@0.4.0/dist/index.umd.js
   ```

2. **或者使用 npm**：
   ```bash
   npm install pixi-live2d-display@0.4.0
   cp node_modules/pixi-live2d-display/dist/index.umd.js static/libs/pixi-live2d-display/
   ```

3. **更新 HTML**：
   代码已经配置为自动尝试本地文件路径：`/static/libs/pixi-live2d-display/index.umd.js`

### 方式 2: 使用不同的 CDN

如果 unpkg 和 jsdelivr 都不可用，可以尝试：
- 使用其他 CDN 服务
- 从 GitHub 直接加载（如果项目有构建文件）

### 方式 3: 使用 npm 和打包工具

如果你使用 webpack 或 vite 等打包工具：
```bash
npm install pixi-live2d-display
```

然后在代码中导入：
```javascript
import { Live2DModel } from 'pixi-live2d-display';
```

## 验证

加载成功后，浏览器控制台应该显示：
- ✅ `pixi-live2d-display loaded from: [source]`
- ✅ `Live2D 命名空间已就绪`
- ✅ `PIXI.live2d.display.Live2DModel` 可用

## 当前状态

代码已经配置为：
1. 自动尝试多个 CDN 源
2. 如果 CDN 失败，尝试本地文件
3. 提供详细的错误信息和调试日志

如果所有源都失败，请按照方式 1 手动下载库文件。
