#!/usr/bin/env python3
import asyncio
import re
import edge_tts
from pydub import AudioSegment
from pathlib import Path
import os
import glob
import sys
import argparse

# Voice options from edge-tts
VOICES = {
    'ALEX': 'en-US-ChristopherNeural',    # Male voice
    'JORDAN': 'en-US-JennyNeural'          # Female voice
}

def parse_conversation(input_source):
    """Parse markdown content and extract speaker lines
    
    Args:
        input_source: Either a filename or '-' for stdin
    """
    if input_source == '-':
        content = sys.stdin.read()
    else:
        with open(input_source, 'r') as f:
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
    communicate = edge_tts.Communicate(text, voice, rate='+25%')
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
        combined += audio # + AudioSegment.silent(duration=1)
    
    # Export final audio
    combined.export(output_file, format="mp3")
    
    # Clean up temp files
    for temp_file in temp_files:
        os.remove(temp_file)
    
    print(f"Podcast created: {output_file}")

def select_conversation_file():
    """Find and let user select from available *-CONVO.md files"""
    convo_files = glob.glob("*-CONVO.md")
    
    if not convo_files:
        print("No *-CONVO.md files found in current directory!")
        return None
    
    if len(convo_files) == 1:
        print(f"Found conversation file: {convo_files[0]}")
        return convo_files[0]
    
    print("Available conversation files:")
    for i, file in enumerate(convo_files, 1):
        print(f"{i}. {file}")
    
    while True:
        try:
            choice = input(f"\nSelect file (1-{len(convo_files)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(convo_files):
                return convo_files[index]
            else:
                print(f"Please enter a number between 1 and {len(convo_files)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nCancelled by user")
            return None

def get_output_filename(input_file):
    """Generate output filename based on input file"""
    # Extract prefix from *-CONVO.md to create *-podcast.mp3
    if input_file.endswith("-CONVO.md"):
        prefix = input_file[:-9]  # Remove "-CONVO.md"
        return f"{prefix}-podcast.mp3"
    else:
        # Fallback for unexpected filename format
        return input_file.replace(".md", "-podcast.mp3")

async def main():
    parser = argparse.ArgumentParser(
        description='Convert conversation markdown to audio podcast',
        epilog='Use "-" as input to read from stdin. Example: python url2convo.py URL | python edge_tts_converter.py - -o output.mp3'
    )
    parser.add_argument('input', nargs='?', help='Input markdown file (use "-" for stdin, or leave empty to select from available files)')
    parser.add_argument('--output', '-o', help='Output MP3 filename (default: based on input filename or "podcast.mp3" for stdin)')
    
    args = parser.parse_args()
    
    # Determine input source
    if args.input:
        if args.input == '-':
            input_file = '-'
        else:
            input_file = args.input
            if not os.path.exists(input_file):
                print(f"Error: Input file '{input_file}' not found!")
                return
    else:
        # No input specified, use interactive selection
        input_file = select_conversation_file()
        if not input_file:
            return
    
    # Parse conversation
    conversation = parse_conversation(input_file)
    
    if not conversation:
        print("No conversation found!")
        return
    
    # Determine output filename
    if args.output:
        output_file = args.output
    elif input_file == '-':
        output_file = 'podcast.mp3'
    else:
        output_file = get_output_filename(input_file)
    
    print(f"Found {len(conversation)} lines of dialogue")
    await create_podcast(conversation, output_file)

if __name__ == "__main__":
    asyncio.run(main())