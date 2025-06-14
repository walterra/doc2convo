#!/usr/bin/env python3
import re
import pyttsx3
import time
from pathlib import Path

def parse_conversation(markdown_file):
    """Parse markdown file and extract speaker lines"""
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    # Find conversation section
    lines = content.split('\n')
    conversation = []
    
    for line in lines:
        # Match speaker lines (bold text followed by colon)
        match = re.match(r'\*\*([A-Z]+):\*\* (.+)', line)
        if match:
            speaker = match.group(1)
            text = match.group(2)
            conversation.append((speaker, text))
    
    return conversation

def setup_voices(engine):
    """Configure different voices for speakers"""
    voices = engine.getProperty('voices')
    
    # Try to get different voices
    voice_map = {}
    if len(voices) >= 2:
        voice_map['ALEX'] = voices[0].id
        voice_map['JORDAN'] = voices[1].id
    else:
        # Use same voice but different properties
        voice_map['ALEX'] = voices[0].id if voices else None
        voice_map['JORDAN'] = voices[0].id if voices else None
    
    return voice_map

def text_to_speech(conversation, output_file='podcast.mp3'):
    """Convert conversation to speech with different voices"""
    try:
        # Try to initialize with the correct driver for macOS
        engine = pyttsx3.init('nsss')
    except:
        try:
            # Fallback to default driver
            engine = pyttsx3.init()
        except Exception as e:
            print(f"Error initializing text-to-speech engine: {e}")
            print("Trying alternative approach...")
            # Use system command as fallback
            use_system_say(conversation)
            return
    
    # Configure voice properties
    engine.setProperty('rate', 175)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume
    
    voice_map = setup_voices(engine)
    
    # Save to file
    temp_files = []
    
    for i, (speaker, text) in enumerate(conversation):
        print(f"Processing: {speaker}: {text[:50]}...")
        
        # Set voice for speaker
        if speaker in voice_map and voice_map[speaker]:
            engine.setProperty('voice', voice_map[speaker])
        
        # Adjust pitch/rate for differentiation
        if speaker == 'ALEX':
            engine.setProperty('rate', 175)
        else:
            engine.setProperty('rate', 165)
        
        # Generate speech
        engine.say(text)
        engine.runAndWait()
    
    print(f"Audio generation complete!")

def use_system_say(conversation):
    """Fallback using macOS 'say' command"""
    import subprocess
    
    for i, (speaker, text) in enumerate(conversation):
        print(f"Processing: {speaker}: {text[:50]}...")
        
        # Use different voices for different speakers
        voice = 'Alex' if speaker == 'ALEX' else 'Samantha'
        
        # Escape quotes in text
        escaped_text = text.replace('"', '\\"')
        
        # Use the macOS 'say' command
        subprocess.run(['say', '-v', voice, escaped_text])
    
    print(f"Audio generation complete!")

def main():
    # Parse conversation
    conversation = parse_conversation('DAILY-CONVO.md')
    
    if not conversation:
        print("No conversation found in markdown file!")
        return
    
    print(f"Found {len(conversation)} lines of dialogue")
    
    # Convert to speech
    text_to_speech(conversation)

if __name__ == "__main__":
    main()