# Implementation Plan (Demo Lite)

## Phase 1: Setup (No DB)
- [ ] **Step 1.1: Environment**
  - Create `environment.yml` (Python 3.11, fastapi, uvicorn, dashscope, websockets, loguru).
  - *Note*: No Docker needed.
- [ ] **Step 1.2: Basic Server**
  - Create `main.py` with FastAPI app.
  - Create `GlobalState` class to hold the playlist in memory.

## Phase 2: The Brain (LLM & TTS)
- [x] **Step 2.1: Script Generator**
  - Implement `AIService.generate_scripts(topic)` using Qwen-Turbo.
  - Prompt: "Generate 5 short, catchy marketing sentences about {topic}."
- [x] **Step 2.2: Voice Generator**
  - Implement `AIService.text_to_speech(text)` using CosyVoice.
  - Return: Audio bytes + Visemes.

## Phase 3: The Broadcaster (WebSocket)
- [x] **Step 3.1: Stream Loop**
  - Implement WebSocket endpoint.
  - Logic: `while True: pop audio from playlist -> send to client -> sleep(duration)`.
  - Handle "Auto-Refill": If playlist is empty, call `generate_scripts` again.

## Phase 4: Frontend
- [x] **Step 4.1: Simple Player**
  - A single HTML page with `pixi-live2d-display`.
  - Connect to WebSocket.
  - Play audio buffer sequentially.