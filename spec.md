# AI Streamer - Product Spec

## Core Concept
An automated "Digital Human Streamer" that generates its own script based on a topic and broadcasts it 24/7.

## User Stories
- As a user, I want to input a topic (e.g., "Selling Coffee"), and have the AI immediately start streaming relevant content.
- As a viewer, I want to see the digital human's lip-sync match the audio perfectly.
- As a developer, I want the stream to never stop (auto-loop or auto-generate).

## Architecture: The "Playlist" Loop
1. **Script Generation**: 
   - User inputs topic.
   - LLM generates 5 short scripts (e.g., Intro, Pain Point, Solution, Price, CTA).
2. **Audio Synthesis**:
   - Backend converts scripts to Audio + Visemes (Lip-sync data).
   - Saved to an in-memory queue.
3. **Broadcasting**:
   - WebSocket pushes audio chunks to frontend one by one.
   - When queue is empty, trigger generation of new scripts.

## API Design (Simple)
- `POST /api/start_stream`: Body `{ "topic": "string" }` -> Starts the generation loop.
- `WS /ws/stream`: The frontend connects here to receive the continuous audio stream.