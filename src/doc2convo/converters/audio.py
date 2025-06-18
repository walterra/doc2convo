# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""Audio converter for markdown conversations."""

import asyncio
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

import edge_tts
from pydub import AudioSegment

from ..exceptions import TTSError

# Try importing Orpheus TTS from local directory
try:
    # Add orpheus-tts-local directory to sys.path for direct import
    orpheus_path = Path(__file__).parent.parent.parent / "orpheus-tts-local"
    if orpheus_path.exists():
        sys.path.insert(0, str(orpheus_path))
    
    from gguf_orpheus import generate_speech_from_api, AVAILABLE_VOICES as ORPHEUS_AVAILABLE_VOICES
    ORPHEUS_AVAILABLE = True
except ImportError:
    ORPHEUS_AVAILABLE = False
    ORPHEUS_AVAILABLE_VOICES = []


class AudioConverter:
    """Convert markdown conversations to audio using Edge TTS or Orpheus TTS."""
    
    # Default voice mappings
    DEFAULT_EDGE_VOICES = {
        'ALEX': 'en-US-ChristopherNeural',
        'JORDAN': 'en-US-JennyNeural'
    }
    
    DEFAULT_ORPHEUS_VOICES = {
        'ALEX': 'leo',
        'JORDAN': 'tara'
    }
    
    def __init__(self, tts_engine: str = "edge", voices: Dict[str, str] = None):
        """Initialize the audio converter.
        
        Args:
            tts_engine: TTS engine to use ("edge" or "orpheus")
            voices: Optional custom voice mapping
        """
        self.tts_engine = tts_engine
        
        if tts_engine == "orpheus":
            if not ORPHEUS_AVAILABLE:
                raise TTSError("orpheus-tts-local is not available. Install with: python3 setup-orpheus.py")
            self.voices = voices or self.DEFAULT_ORPHEUS_VOICES
        else:
            self.voices = voices or self.DEFAULT_EDGE_VOICES
            
        self.rate = "+25%"  # Speed up speech for more natural flow (Edge TTS only)
    
    async def convert_to_audio(self, conversation: str, output_path: str) -> None:
        """Convert conversation markdown to audio file.
        
        Args:
            conversation: Markdown formatted conversation
            output_path: Path for output audio file
        """
        try:
            # Parse conversation
            segments = self._parse_conversation(conversation)
            if not segments:
                raise TTSError("No conversation segments found")
            
            # Generate audio segments
            audio_files = await self._generate_audio_segments(segments)
            
            # Combine audio files
            self._combine_audio_files(audio_files, output_path)
            
        except Exception as e:
            raise TTSError(f"Audio conversion failed: {e}")
    
    def convert_to_audio_sync(self, conversation: str, output_path: str) -> None:
        """Synchronous wrapper for convert_to_audio."""
        asyncio.run(self.convert_to_audio(conversation, output_path))
    
    def _parse_conversation(self, text: str) -> List[Tuple[str, str]]:
        """Parse markdown conversation into segments.
        
        Args:
            text: Markdown formatted conversation
            
        Returns:
            List of (speaker, text) tuples
        """
        pattern = r'\*\*([A-Z]+):\*\* (.+)'
        matches = re.findall(pattern, text, re.MULTILINE)
        return matches
    
    async def _generate_audio_segments(self, segments: List[Tuple[str, str]]) -> List[str]:
        """Generate audio files for each segment.
        
        Args:
            segments: List of (speaker, text) tuples
            
        Returns:
            List of temporary audio file paths
        """
        audio_files = []
        tasks = []
        
        for i, (speaker, text) in enumerate(segments):
            default_voice = (self.DEFAULT_ORPHEUS_VOICES if self.tts_engine == "orpheus" 
                           else self.DEFAULT_EDGE_VOICES)['ALEX']
            voice = self.voices.get(speaker.upper(), default_voice)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{i}.mp3")
            temp_file.close()
            
            # Print progress like the original script
            preview = text[:50] + "..." if len(text) > 50 else text
            print(f"Generating audio for {speaker}: {preview}", file=sys.stderr)
            
            task = self._text_to_speech(text, voice, temp_file.name)
            tasks.append(task)
            audio_files.append(temp_file.name)
        
        await asyncio.gather(*tasks)
        return audio_files
    
    async def _text_to_speech(self, text: str, voice: str, output_file: str) -> None:
        """Convert text to speech using the configured TTS engine.
        
        Args:
            text: Text to convert
            voice: Voice identifier
            output_file: Output file path
        """
        if self.tts_engine == "orpheus":
            await self._generate_speech_orpheus(text, voice, output_file)
        else:
            await self._generate_speech_edge(text, voice, output_file)
    
    async def _generate_speech_edge(self, text: str, voice: str, output_file: str) -> None:
        """Generate speech using edge-tts."""
        communicate = edge_tts.Communicate(text, voice, rate=self.rate)
        await communicate.save(output_file)
    
    async def _generate_speech_orpheus(self, text: str, voice: str, output_file: str) -> None:
        """Generate speech using orpheus-tts-local."""
        if not ORPHEUS_AVAILABLE:
            raise TTSError("orpheus-tts-local is not available. Install with: python3 setup-orpheus.py")

        try:
            # Generate audio segments
            print(f"Generating audio using Orpheus TTS with voice '{voice}'", file=sys.stderr)
            segments = generate_speech_from_api(text, voice=voice)

            # Convert to AudioSegment and export as MP3
            audio_data = b''.join(segments)
            import numpy as np
            # Convert bytes to int16 numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            # Convert to AudioSegment
            audio_segment = AudioSegment(
                audio_np.tobytes(),
                frame_rate=24000,  # Orpheus sample rate
                sample_width=2,    # 16-bit audio
                channels=1         # Mono
            )
            # Export as MP3
            audio_segment.export(output_file, format="mp3")
        except Exception as e:
            raise TTSError(f"Orpheus TTS generation failed: {e}")
    
    def _combine_audio_files(self, audio_files: List[str], output_path: str) -> None:
        """Combine audio segments with pauses.
        
        Args:
            audio_files: List of audio file paths
            output_path: Final output path
        """
        combined = AudioSegment.empty()
        pause = AudioSegment.silent(duration=300)  # 300ms pause
        
        print("Combining audio files...", file=sys.stderr)
        
        try:
            for i, audio_file in enumerate(audio_files):
                audio = AudioSegment.from_mp3(audio_file)
                combined += audio
                
                if i < len(audio_files) - 1:
                    combined += pause
            
            combined.export(output_path, format="mp3")
            
        finally:
            # Clean up temporary files
            for audio_file in audio_files:
                try:
                    os.unlink(audio_file)
                except:
                    pass