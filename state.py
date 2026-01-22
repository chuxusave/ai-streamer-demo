"""Global state management for in-memory playlist."""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio


@dataclass
class AudioItem:
    """Represents a single audio item in the playlist."""
    text: str
    audio_data: bytes
    visemes: List[Dict]  # List of viseme data for lip-sync
    duration_ms: int
    created_at: datetime
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class GlobalState:
    """Global state manager for the AI Streamer.
    
    This class holds the playlist in memory and manages the streaming state.
    """
    
    def __init__(self):
        self.playlist: List[AudioItem] = []
        self.current_topic: Optional[str] = None
        self.is_streaming: bool = False
        self.lock = asyncio.Lock()
    
    async def add_to_playlist(self, item: AudioItem) -> None:
        """Add an audio item to the playlist."""
        async with self.lock:
            self.playlist.append(item)
    
    async def add_batch_to_playlist(self, items: List[AudioItem]) -> None:
        """Add multiple audio items to the playlist."""
        async with self.lock:
            self.playlist.extend(items)
    
    async def pop_from_playlist(self) -> Optional[AudioItem]:
        """Pop the first item from the playlist."""
        async with self.lock:
            if self.playlist:
                return self.playlist.pop(0)
            return None
    
    async def get_playlist_size(self) -> int:
        """Get the current playlist size."""
        async with self.lock:
            return len(self.playlist)
    
    async def clear_playlist(self) -> None:
        """Clear the entire playlist."""
        async with self.lock:
            self.playlist.clear()
    
    async def set_topic(self, topic: str) -> None:
        """Set the current streaming topic."""
        async with self.lock:
            self.current_topic = topic
    
    async def get_topic(self) -> Optional[str]:
        """Get the current streaming topic."""
        async with self.lock:
            return self.current_topic
    
    async def set_streaming(self, is_streaming: bool) -> None:
        """Set the streaming state."""
        async with self.lock:
            self.is_streaming = is_streaming
    
    async def is_currently_streaming(self) -> bool:
        """Check if currently streaming."""
        async with self.lock:
            return self.is_streaming


# Global state instance
global_state = GlobalState()
