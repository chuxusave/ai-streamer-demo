/**
 * AI Streamer Frontend Application
 * Handles WebSocket connection, audio playback, and Live2D lip-sync
 */

class AIStreamer {
    constructor() {
        this.ws = null;
        this.audioContext = null;
        this.currentAudioSource = null;
        this.isPlaying = false;
        this.isConnected = false;
        this.app = null;
        this.model = null;
        this.currentVisemes = [];
        this.visemeAnimationId = null;
        
        // API base URL (adjust if needed)
        this.apiBase = window.location.origin;
        // Use wss:// for secure connections, ws:// for local development
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.wsUrl = `${protocol}//${window.location.host}/ws/stream`;
        
        this.init();
    }

    init() {
        this.setupUI();
        this.setupAudio();
        this.setupLive2D();
    }

    setupUI() {
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        const topicInput = document.getElementById('topic-input');

        startBtn.addEventListener('click', () => {
            const topic = topicInput.value.trim();
            if (topic) {
                this.startStream(topic);
            } else {
                this.showError('请输入主题');
            }
        });

        stopBtn.addEventListener('click', () => {
            this.stopStream();
        });
    }

    async setupAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.updateStatus('audio', 'ready', '音频系统就绪');
        } catch (error) {
            console.error('Failed to initialize audio context:', error);
            this.showError('音频系统初始化失败');
        }
    }

    async setupLive2D() {
        try {
            // Initialize Pixi.js
            this.app = new PIXI.Application({
                view: document.getElementById('live2d-canvas'),
                width: 800,
                height: 600,
                backgroundColor: 0xffffff,
                backgroundAlpha: 0.1,
                antialias: true,
            });

            // Load Live2D model
            // Note: You need to provide a Live2D model file (.model3.json)
            // For demo purposes, we'll create a placeholder
            this.updateStatus('live2d', 'ready', 'Live2D 就绪（需要模型文件）');
            
            // If you have a Live2D model, uncomment and configure:
            /*
            const { Live2DModel } = PIXI.live2d.display;
            this.model = await Live2DModel.from('path/to/your/model.model3.json');
            this.app.stage.addChild(this.model);
            this.model.scale.set(0.5);
            this.model.x = this.app.screen.width / 2;
            this.model.y = this.app.screen.height / 2;
            */
            
        } catch (error) {
            console.error('Failed to setup Live2D:', error);
            this.showError('Live2D 初始化失败: ' + error.message);
        }
    }

    async startStream(topic) {
        try {
            // Step 1: Start the stream on backend
            const response = await fetch(`${this.apiBase}/api/start_stream?topic=${encodeURIComponent(topic)}`, {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error(`Failed to start stream: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('Stream started:', data);

            // Step 2: Connect WebSocket
            this.connectWebSocket();

            // Update UI
            document.getElementById('start-btn').disabled = true;
            document.getElementById('stop-btn').disabled = false;
            document.getElementById('topic-input').disabled = true;

        } catch (error) {
            console.error('Failed to start stream:', error);
            this.showError('启动失败: ' + error.message);
        }
    }

    connectWebSocket() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return;
        }

        this.ws = new WebSocket(this.wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.updateStatus('connection', 'connected', '已连接');
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('Failed to parse message:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showError('WebSocket 连接错误');
            this.updateStatus('connection', 'disconnected', '连接错误');
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.updateStatus('connection', 'disconnected', '已断开');
            
            // Try to reconnect after 3 seconds
            if (this.isPlaying) {
                setTimeout(() => {
                    this.connectWebSocket();
                }, 3000);
            }
        };
    }

    handleMessage(message) {
        switch (message.type) {
            case 'audio_chunk':
                this.handleAudioChunk(message);
                break;
            case 'status':
                this.handleStatusMessage(message);
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    }

    async handleAudioChunk(message) {
        try {
            // Update UI
            document.getElementById('current-text').textContent = message.text;
            document.getElementById('current-script').textContent = message.text.substring(0, 30) + '...';
            this.updateStatus('playback', 'playing', '播放中');

            // Convert hex string back to bytes
            const audioBytes = this.hexToBytes(message.audio_data);
            
            // Convert PCM bytes to AudioBuffer
            // Assuming PCM format: 16-bit, mono, 24000 Hz sample rate
            const sampleRate = 24000;
            const numChannels = 1;
            const bytesPerSample = 2;
            const numSamples = audioBytes.length / bytesPerSample;
            
            const audioBuffer = this.audioContext.createBuffer(
                numChannels,
                numSamples,
                sampleRate
            );
            
            // Convert PCM bytes to float32 samples
            const channelData = audioBuffer.getChannelData(0);
            const view = new DataView(audioBytes.buffer);
            
            for (let i = 0; i < numSamples; i++) {
                // Read 16-bit signed integer and convert to float32 (-1.0 to 1.0)
                const sample = view.getInt16(i * bytesPerSample, true); // little-endian
                channelData[i] = sample / 32768.0;
            }
            
            // Play audio
            await this.playAudio(audioBuffer);
            
            // Update visemes for lip-sync
            if (message.visemes && message.visemes.length > 0) {
                this.currentVisemes = message.visemes;
                this.startVisemeAnimation(message.duration_ms);
            }

        } catch (error) {
            console.error('Failed to handle audio chunk:', error);
            this.showError('音频播放失败: ' + error.message);
        }
    }

    handleStatusMessage(message) {
        if (message.status === 'refilling') {
            this.updateStatus('playback', 'refilling', '生成新内容中...');
            document.getElementById('status-text').textContent = message.message;
        }
    }

    async playAudio(audioBuffer) {
        return new Promise((resolve) => {
            // Stop current audio if playing
            if (this.currentAudioSource) {
                this.currentAudioSource.stop();
            }

            // Create new audio source
            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(this.audioContext.destination);

            source.onended = () => {
                this.currentAudioSource = null;
                this.stopVisemeAnimation();
                this.updateStatus('playback', 'waiting', '等待下一段');
                resolve();
            };

            source.start(0);
            this.currentAudioSource = source;
            this.isPlaying = true;
        });
    }

    startVisemeAnimation(durationMs) {
        // Stop previous animation
        this.stopVisemeAnimation();

        if (!this.model || !this.currentVisemes || this.currentVisemes.length === 0) {
            return;
        }

        const startTime = Date.now();
        const duration = durationMs;

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Find current viseme based on elapsed time
            const currentViseme = this.currentVisemes.find(
                (v, i) => {
                    const nextViseme = this.currentVisemes[i + 1];
                    if (!nextViseme) return true;
                    return elapsed >= v.offset * 1000 && elapsed < nextViseme.offset * 1000;
                }
            ) || this.currentVisemes[this.currentVisemes.length - 1];

            if (currentViseme && currentViseme.coefficients) {
                // Apply viseme coefficients to Live2D model
                // This depends on your specific Live2D model's parameter names
                // Example (adjust based on your model):
                /*
                if (this.model.internalModel) {
                    const coreModel = this.model.internalModel.coreModel;
                    currentViseme.coefficients.forEach((value, index) => {
                        // Map coefficient index to Live2D parameter
                        // This is model-specific
                        const paramId = `ParamMouthOpenY_${index}`;
                        coreModel.setParameterValueById(paramId, value);
                    });
                }
                */
            }

            if (progress < 1) {
                this.visemeAnimationId = requestAnimationFrame(animate);
            }
        };

        animate();
    }

    stopVisemeAnimation() {
        if (this.visemeAnimationId) {
            cancelAnimationFrame(this.visemeAnimationId);
            this.visemeAnimationId = null;
        }
    }

    stopStream() {
        // Close WebSocket
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        // Stop audio
        if (this.currentAudioSource) {
            this.currentAudioSource.stop();
            this.currentAudioSource = null;
        }

        this.stopVisemeAnimation();
        this.isPlaying = false;
        this.isConnected = false;

        // Update UI
        document.getElementById('start-btn').disabled = false;
        document.getElementById('stop-btn').disabled = true;
        document.getElementById('topic-input').disabled = false;
        this.updateStatus('connection', 'disconnected', '已断开');
        this.updateStatus('playback', 'waiting', '已停止');
        document.getElementById('current-text').textContent = '已停止';
        document.getElementById('status-text').textContent = '';
    }

    updateStatus(type, status, text) {
        const statusElement = document.getElementById(`${type}-status`);
        const textElement = document.getElementById(`${type}-text`);

        if (statusElement) {
            statusElement.className = `status-indicator ${status}`;
        }
        if (textElement) {
            textElement.textContent = text;
        }
    }

    showError(message) {
        const errorEl = document.getElementById('error-message');
        errorEl.textContent = message;
        errorEl.classList.add('show');
        setTimeout(() => {
            errorEl.classList.remove('show');
        }, 5000);
    }

    hexToBytes(hex) {
        const bytes = new Uint8Array(hex.length / 2);
        for (let i = 0; i < hex.length; i += 2) {
            bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
        }
        return bytes;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.streamer = new AIStreamer();
});
