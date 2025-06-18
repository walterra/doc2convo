#!/usr/bin/env python3
# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

import argparse
import asyncio
import glob
import os
import re
import sys
import tempfile
from pathlib import Path

import edge_tts
from pydub import AudioSegment

# Add orpheus-tts-local to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orpheus-tts-local'))
try:
    from gguf_orpheus import generate_speech_from_api, AVAILABLE_VOICES as ORPHEUS_AVAILABLE_VOICES
    ORPHEUS_AVAILABLE = True
except ImportError:
    ORPHEUS_AVAILABLE = False

# Voice options for different TTS engines
EDGE_VOICES = {
    "ALEX": "en-US-ChristopherNeural",  # Male voice
    "JORDAN": "en-US-JennyNeural",  # Female voice
}

# Default Orpheus voices
ORPHEUS_VOICES = {
    "ALEX": "leo",  # Male voice
    "JORDAN": "tara",  # Female voice
}


def parse_conversation(input_source):
    """Parse markdown content and extract speaker lines

    Args:
        input_source: Either a filename or '-' for stdin
    """
    if input_source == "-":
        content = sys.stdin.read()
    else:
        with open(input_source, "r") as f:
            content = f.read()

    lines = content.split("\n")
    conversation = []

    for line in lines:
        match = re.match(r"\*\*([A-Z]+):\*\* (.+)", line)
        if match:
            speaker = match.group(1)
            text = match.group(2)
            conversation.append((speaker, text))

    return conversation


async def generate_speech_edge(text, voice, output_file):
    """Generate speech using edge-tts"""
    communicate = edge_tts.Communicate(text, voice, rate="+25%")
    await communicate.save(output_file)


async def generate_speech_orpheus(text, voice, output_file):
    """Generate speech using orpheus-tts-local"""
    if not ORPHEUS_AVAILABLE:
        print("Error: orpheus-tts-local is not available.")
        print("Make sure to install its requirements: cd orpheus-tts-local && pip install -r requirements.txt")
        sys.exit(1)

    try:
        # Generate audio segments
        print(f"Generating audio using Orpheus TTS with voice '{voice}'")
        segments = generate_speech_from_api(text, voice=voice)

        # Convert to AudioSegment and export as MP3
        audio_data = b''.join(segments)
        import io
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
        print(f"Error generating speech with Orpheus: {e}")
        print("Make sure LM Studio API server is running at http://127.0.0.1:1234")
        sys.exit(1)


async def generate_speech(text, voice, output_file, tts_engine="edge"):
    """Generate speech for a single line"""
    if tts_engine == "orpheus":
        await generate_speech_orpheus(text, voice, output_file)
    else:
        await generate_speech_edge(text, voice, output_file)


async def create_podcast(conversation, output_file="podcast.mp3", tts_engine="edge", alex_voice=None, jordan_voice=None):
    """Create podcast with multiple voices"""
    # Determine which voices to use based on TTS engine
    if tts_engine == "orpheus":
        if not ORPHEUS_AVAILABLE:
            print("Error: orpheus-tts-local is not available.")
            print("Make sure to install its requirements: cd orpheus-tts-local && pip install -r requirements.txt")
            sys.exit(1)

        voices = ORPHEUS_VOICES.copy()
        # Override with custom voices if provided
        if alex_voice and alex_voice in ORPHEUS_AVAILABLE_VOICES:
            voices["ALEX"] = alex_voice
        if jordan_voice and jordan_voice in ORPHEUS_AVAILABLE_VOICES:
            voices["JORDAN"] = jordan_voice

        print(f"Using Orpheus TTS with voices: ALEX={voices['ALEX']}, JORDAN={voices['JORDAN']}")
    else:
        voices = EDGE_VOICES

    # Use secure temporary directory that gets auto-cleaned
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        temp_files = []

        # Generate individual audio files
        for i, (speaker, text) in enumerate(conversation):
            print(f"Generating audio for {speaker}: {text[:50]}...")

            voice = voices.get(speaker, voices["ALEX"])
            temp_file = temp_path / f"temp_{i}.mp3"
            temp_files.append(temp_file)

            await generate_speech(text, voice, str(temp_file), tts_engine)

        # Combine audio files
        print("Combining audio files...")
        combined = AudioSegment.empty()

        for temp_file in temp_files:
            audio = AudioSegment.from_mp3(str(temp_file))
            # Add small pause between lines (300ms)
            combined += audio + AudioSegment.silent(duration=300)

        # Export final audio
        combined.export(output_file, format="mp3")

        print(f"Podcast created: {output_file}")
        # Temporary directory and files are automatically cleaned up when context exits


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
        description="Convert conversation markdown to audio podcast",
        epilog='Use "-" as input to read from stdin. Example: python doc2md-convo.py URL | python md-convo2mp3.py - -o output.mp3',
    )
    parser.add_argument(
        "input",
        nargs="?",
        help='Input markdown file (use "-" for stdin, or leave empty to select from available files)',
    )
    parser.add_argument(
        "--output",
        "-o",
        help='Output MP3 filename (default: based on input filename or "podcast.mp3" for stdin)',
    )
    parser.add_argument(
        "--tts-engine",
        choices=["edge", "orpheus"],
        default="edge",
        help="TTS engine to use (default: edge)",
    )
    parser.add_argument(
        "--alex-voice",
        help="Voice for ALEX (orpheus: tara, leah, jess, leo, dan, mia, zac, zoe)",
    )
    parser.add_argument(
        "--jordan-voice",
        help="Voice for JORDAN (orpheus: tara, leah, jess, leo, dan, mia, zac, zoe)",
    )

    args = parser.parse_args()

    # Determine input source
    if args.input:
        if args.input == "-":
            input_file = "-"
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
    elif input_file == "-":
        output_file = "podcast.mp3"
    else:
        output_file = get_output_filename(input_file)

    print(f"Found {len(conversation)} lines of dialogue")
    await create_podcast(
        conversation,
        output_file,
        tts_engine=args.tts_engine,
        alex_voice=args.alex_voice,
        jordan_voice=args.jordan_voice
    )


if __name__ == "__main__":
    asyncio.run(main())
