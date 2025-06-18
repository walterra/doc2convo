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


class AudioConverter:
    """Convert markdown conversations to audio using Edge TTS."""
    
    # Default voice mapping
    DEFAULT_VOICES = {
        'ALEX': 'en-US-ChristopherNeural',
        'JORDAN': 'en-US-JennyNeural'
    }
    
    def __init__(self, voices: Dict[str, str] = None):
        """Initialize the audio converter.
        
        Args:
            voices: Optional custom voice mapping
        """
        self.voices = voices or self.DEFAULT_VOICES
        self.rate = "+25%"  # Speed up speech for more natural flow
    
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
            voice = self.voices.get(speaker.upper(), self.DEFAULT_VOICES['ALEX'])
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
        """Convert text to speech using Edge TTS.
        
        Args:
            text: Text to convert
            voice: Voice identifier
            output_file: Output file path
        """
        communicate = edge_tts.Communicate(text, voice, rate=self.rate)
        await communicate.save(output_file)
    
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