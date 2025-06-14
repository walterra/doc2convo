#!/usr/bin/env python3
import asyncio
import re
import edge_tts
from pydub import AudioSegment
from pathlib import Path
import os

# Voice options from edge-tts
VOICES = {
    'ALEX': 'en-US-ChristopherNeural',    # Male voice
    'JORDAN': 'en-US-JennyNeural'          # Female voice
}

def parse_conversation(markdown_file):
    """Parse markdown file and extract speaker lines"""
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    conversation = []
    
    for line in lines:
        match = re.match(r'\*\*([A-Z]+):\*\* (.+)', line)
        if match:
            speaker = match.group(1)
            text = match.group(2)
            conversation.append((speaker, text))
    
    return conversation

async def generate_speech(text, voice, output_file):
    """Generate speech for a single line"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

async def create_podcast(conversation, output_file='podcast.mp3'):
    """Create podcast with multiple voices"""
    temp_files = []
    
    # Generate individual audio files
    for i, (speaker, text) in enumerate(conversation):
        print(f"Generating audio for {speaker}: {text[:50]}...")
        
        voice = VOICES.get(speaker, VOICES['ALEX'])
        temp_file = f"temp_{i}.mp3"
        temp_files.append(temp_file)
        
        await generate_speech(text, voice, temp_file)
    
    # Combine audio files
    print("Combining audio files...")
    combined = AudioSegment.empty()
    
    for temp_file in temp_files:
        audio = AudioSegment.from_mp3(temp_file)
        # Add small pause between lines
        combined += audio + AudioSegment.silent(duration=300)
    
    # Export final audio
    combined.export(output_file, format="mp3")
    
    # Clean up temp files
    for temp_file in temp_files:
        os.remove(temp_file)
    
    print(f"Podcast created: {output_file}")

async def main():
    conversation = parse_conversation('DAILY-CONVO.md')
    
    if not conversation:
        print("No conversation found!")
        return
    
    print(f"Found {len(conversation)} lines of dialogue")
    await create_podcast(conversation)

if __name__ == "__main__":
    asyncio.run(main())