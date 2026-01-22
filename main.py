"""Main FastAPI application for AI Streamer."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from loguru import logger
import sys
import asyncio
from typing import Optional
import os

from config import settings
from state import global_state, AudioItem
from ai_service import ai_service

# Track if auto-refill is in progress to avoid concurrent refills
_refill_in_progress = False


# Configure loguru
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)


# Create FastAPI app
app = FastAPI(
    title="AI Streamer",
    description="24/7 AI Digital Human Streamer Demo",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("🚀 AI Streamer starting up...")
    logger.info(f"📡 Server will run on {settings.host}:{settings.port}")
    logger.info(f"🔧 Debug mode: {settings.debug}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("👋 AI Streamer shutting down...")


@app.get("/")
async def root():
    """Serve the frontend HTML page."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "AI Streamer API",
        "version": "0.1.0",
        "status": "running",
        "frontend": "Visit /static/index.html for the frontend interface"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    playlist_size = await global_state.get_playlist_size()
    is_streaming = await global_state.is_currently_streaming()
    topic = await global_state.get_topic()
    
    return {
        "status": "healthy",
        "playlist_size": playlist_size,
        "is_streaming": is_streaming,
        "current_topic": topic,
    }


@app.post("/api/start_stream")
async def start_stream(topic: str):
    """Start the streaming with a given topic.
    
    This endpoint will:
    1. Generate marketing scripts using Qwen-Turbo
    2. Convert each script to audio using CosyVoice TTS
    3. Add audio items to the playlist
    """
    try:
        await global_state.set_topic(topic)
        await global_state.set_streaming(True)
        
        logger.info(f"📺 Starting stream with topic: {topic}")
        
        # Step 1: Generate scripts
        scripts = await ai_service.generate_scripts(topic, count=5)
        logger.info(f"✅ Generated {len(scripts)} scripts")
        
        # Step 2: Convert each script to audio
        audio_items = []
        for i, script in enumerate(scripts):
            try:
                logger.info(f"🔊 Synthesizing audio {i+1}/{len(scripts)}: {script[:30]}...")
                tts_result = await ai_service.text_to_speech(script)
                
                # Create AudioItem
                audio_item = AudioItem(
                    text=script,
                    audio_data=tts_result["audio_data"],
                    visemes=tts_result["visemes"],
                    duration_ms=tts_result["duration_ms"],
                    created_at=None,  # Will be set by __post_init__
                )
                audio_items.append(audio_item)
                
            except Exception as e:
                logger.error(f"❌ Failed to synthesize audio for script {i+1}: {e}")
                # Skip failed items, continue with others
                continue
        
        # Step 3: Add all audio items to playlist
        if audio_items:
            await global_state.add_batch_to_playlist(audio_items)
            logger.info(f"✅ Added {len(audio_items)} audio items to playlist")
        else:
            logger.warning("⚠️ No audio items were generated")
        
        return {
            "status": "started",
            "topic": topic,
            "scripts_generated": len(scripts),
            "audio_items_created": len(audio_items),
            "playlist_size": await global_state.get_playlist_size(),
            "message": "Stream started. Connect to /ws/stream to receive audio."
        }
        
    except Exception as e:
        logger.error(f"❌ Error starting stream: {e}")
        await global_state.set_streaming(False)
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to start stream. Please check logs."
        }


@app.get("/api/status")
async def get_status():
    """Get current streaming status."""
    playlist_size = await global_state.get_playlist_size()
    is_streaming = await global_state.is_currently_streaming()
    topic = await global_state.get_topic()
    
    return {
        "is_streaming": is_streaming,
        "playlist_size": playlist_size,
        "current_topic": topic,
    }


async def auto_refill_playlist() -> bool:
    """Automatically refill the playlist when it's empty.
    
    This function:
    1. Checks if there's a current topic
    2. Generates new scripts using the topic
    3. Converts scripts to audio
    4. Adds audio items to the playlist
    
    Returns:
        True if refill was successful, False otherwise
    """
    global _refill_in_progress
    
    # Prevent concurrent refills using a lock
    # Create lock if it doesn't exist (lazy initialization)
    if not hasattr(auto_refill_playlist, '_lock'):
        auto_refill_playlist._lock = asyncio.Lock()
    
    async with auto_refill_playlist._lock:
        if _refill_in_progress:
            logger.debug("⏳ Auto-refill already in progress, skipping...")
            return False
        
        _refill_in_progress = True
    
    try:
        # Check if we have a topic
        topic = await global_state.get_topic()
        if not topic:
            logger.warning("⚠️ No topic set, cannot auto-refill playlist")
            return False
        
        # Check if streaming is enabled
        is_streaming = await global_state.is_currently_streaming()
        if not is_streaming:
            logger.debug("⏸️ Streaming is not active, skipping auto-refill")
            return False
        
        logger.info(f"🔄 Auto-refilling playlist with topic: {topic}")
        
        # Step 1: Generate scripts
        scripts = await ai_service.generate_scripts(topic, count=5)
        logger.info(f"✅ Generated {len(scripts)} scripts for auto-refill")
        
        if not scripts:
            logger.warning("⚠️ No scripts generated for auto-refill")
            return False
        
        # Step 2: Convert each script to audio
        audio_items = []
        for i, script in enumerate(scripts):
            try:
                logger.debug(f"🔊 Synthesizing audio {i+1}/{len(scripts)}: {script[:30]}...")
                tts_result = await ai_service.text_to_speech(script)
                
                # Create AudioItem
                audio_item = AudioItem(
                    text=script,
                    audio_data=tts_result["audio_data"],
                    visemes=tts_result["visemes"],
                    duration_ms=tts_result["duration_ms"],
                    created_at=None,  # Will be set by __post_init__
                )
                audio_items.append(audio_item)
                
            except Exception as e:
                logger.error(f"❌ Failed to synthesize audio for script {i+1}: {e}")
                # Skip failed items, continue with others
                continue
        
        # Step 3: Add all audio items to playlist
        if audio_items:
            await global_state.add_batch_to_playlist(audio_items)
            logger.info(f"✅ Auto-refilled playlist with {len(audio_items)} audio items")
            return True
        else:
            logger.warning("⚠️ No audio items were generated for auto-refill")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in auto-refill: {e}")
        return False
    finally:
        _refill_in_progress = False


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """WebSocket endpoint for streaming audio to clients.
    
    This will continuously send audio chunks from the playlist.
    When playlist is empty, it will automatically trigger refill to generate new content.
    """
    await websocket.accept()
    logger.info("🔌 WebSocket client connected")
    
    # Track consecutive empty checks to avoid too frequent refill attempts
    empty_check_count = 0
    max_empty_checks_before_refill = 2  # Wait 2 checks (2 seconds) before refilling
    
    try:
        while True:
            # Pop audio item from playlist
            item = await global_state.pop_from_playlist()
            
            if item is None:
                # Playlist is empty
                empty_check_count += 1
                playlist_size = await global_state.get_playlist_size()
                
                # Check if we should trigger auto-refill
                if empty_check_count >= max_empty_checks_before_refill:
                    # Check if streaming is still active
                    is_streaming = await global_state.is_currently_streaming()
                    if is_streaming:
                        logger.info("📭 Playlist empty, triggering auto-refill...")
                        
                        # Send a status message to client
                        status_message = {
                            "type": "status",
                            "message": "Playlist empty, generating new content...",
                            "status": "refilling"
                        }
                        try:
                            await websocket.send_json(status_message)
                        except:
                            pass  # Client may have disconnected
                        
                        # Trigger auto-refill in background
                        # Don't await it to avoid blocking the loop
                        refill_task = asyncio.create_task(auto_refill_playlist())
                        
                        # Wait a bit for refill to complete, but don't block too long
                        try:
                            await asyncio.wait_for(refill_task, timeout=30.0)
                            if refill_task.result():
                                logger.info("✅ Auto-refill completed successfully")
                                empty_check_count = 0  # Reset counter
                            else:
                                logger.warning("⚠️ Auto-refill completed but no items were added")
                        except asyncio.TimeoutError:
                            logger.warning("⏱️ Auto-refill timed out, continuing...")
                        except Exception as e:
                            logger.error(f"❌ Auto-refill error: {e}")
                    else:
                        # Streaming is not active, just wait
                        logger.debug("⏸️ Streaming not active, waiting...")
                
                # Wait before checking again
                await asyncio.sleep(1)
                continue
            
            # Reset empty check counter when we get an item
            empty_check_count = 0
            
            # Send audio data to client
            # Format: JSON with audio data and visemes
            message = {
                "type": "audio_chunk",
                "text": item.text,
                "audio_data": item.audio_data.hex(),  # Convert bytes to hex string for JSON
                "visemes": item.visemes,
                "duration_ms": item.duration_ms,
                "timestamp": item.created_at.isoformat(),
            }
            
            try:
                await websocket.send_json(message)
                logger.debug(f"📤 Sent audio chunk: {item.text[:50]}...")
            except Exception as e:
                logger.error(f"❌ Failed to send audio chunk: {e}")
                # Put the item back in the playlist if send failed
                await global_state.add_to_playlist(item)
                break  # Exit loop on send failure
            
            # Wait for the duration of the audio before sending next chunk
            # This simulates real-time playback
            await asyncio.sleep(item.duration_ms / 1000.0)
            
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    import asyncio
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
