# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""CLI for conversation markdown to audio conversion."""

import argparse
import glob
import sys
from datetime import datetime
from pathlib import Path

from ..converters import AudioConverter
from ..exceptions import Doc2ConvoError


def sanitize_filename(filename):
    """Sanitize filename for safe file system usage."""
    import re
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename[:100]


def select_conversation_file():
    """Select a conversation file interactively from available *-CONVO.md files."""
    # Find all *-CONVO.md files in current directory
    convo_files = glob.glob("*-CONVO.md")
    
    if not convo_files:
        print("No *-CONVO.md files found in current directory!")
        return None
    
    print("Available conversation files:")
    for i, file in enumerate(convo_files, 1):
        print(f"{i}. {file}")
    
    # Get user choice
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


def main():
    """Main entry point for md-convo2mp3 command."""
    parser = argparse.ArgumentParser(
        description='Convert conversation markdown to audio using Edge TTS or Orpheus TTS',
        epilog='Use "-" as input to read from stdin. Example: doc2md-convo URL | md-convo2mp3 - -o output.mp3'
    )
    parser.add_argument('input', 
                       nargs='?',
                       help='Input markdown file (use - for stdin, or leave empty to select from available files)')
    parser.add_argument('-o', '--output', help='Output audio file (default: auto-generated)')
    parser.add_argument('--tts-engine',
                       choices=['edge', 'orpheus'],
                       default='edge',
                       help='TTS engine to use (default: edge)')
    parser.add_argument('--alex-voice',
                       help='Voice for ALEX (orpheus: tara, leah, jess, leo, dan, mia, zac, zoe)')
    parser.add_argument('--jordan-voice',
                       help='Voice for JORDAN (orpheus: tara, leah, jess, leo, dan, mia, zac, zoe)')
    
    args = parser.parse_args()
    
    try:
        # Determine input source
        if args.input:
            if args.input == '-':
                conversation = sys.stdin.read()
                input_name = "conversation"
                print("Reading conversation from stdin...", file=sys.stderr)
            else:
                if not Path(args.input).exists():
                    print(f"Error: Input file '{args.input}' not found!", file=sys.stderr)
                    return 1
                with open(args.input, 'r', encoding='utf-8') as f:
                    conversation = f.read()
                input_name = Path(args.input).stem
                print(f"Reading conversation from file: {args.input}", file=sys.stderr)
        else:
            # No input specified, use interactive selection
            input_file = select_conversation_file()
            if not input_file:
                return 1
            with open(input_file, 'r', encoding='utf-8') as f:
                conversation = f.read()
            input_name = Path(input_file).stem
            print(f"Reading conversation from file: {input_file}", file=sys.stderr)
        
        # Parse conversation to count dialogue lines
        import re
        dialogue_lines = re.findall(r'\*\*([A-Z]+):\*\* (.+)', conversation)
        if not dialogue_lines:
            print("No conversation found in input!", file=sys.stderr)
            return 1
        
        print(f"Found {len(dialogue_lines)} lines of dialogue", file=sys.stderr)
        
        # Determine output file
        if args.output:
            output_file = args.output
        else:
            if args.input == '-' or not args.input:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"podcast_{timestamp}.mp3"
            else:
                # Replace -CONVO suffix with -podcast
                if input_name.endswith('-CONVO'):
                    base_name = input_name[:-6]
                else:
                    base_name = input_name
                output_file = f"{base_name}-podcast.mp3"
        
        # Prepare voice configuration
        voices = {}
        if args.tts_engine == "orpheus":
            # Import orpheus available voices for validation
            from ..converters.audio import ORPHEUS_AVAILABLE_VOICES
            
            # Use custom voices if provided and valid
            if args.alex_voice:
                if args.alex_voice in ORPHEUS_AVAILABLE_VOICES:
                    voices['ALEX'] = args.alex_voice
                else:
                    print(f"Warning: '{args.alex_voice}' is not a valid Orpheus voice, using default", file=sys.stderr)
            
            if args.jordan_voice:
                if args.jordan_voice in ORPHEUS_AVAILABLE_VOICES:
                    voices['JORDAN'] = args.jordan_voice
                else:
                    print(f"Warning: '{args.jordan_voice}' is not a valid Orpheus voice, using default", file=sys.stderr)
            
            print(f"Using {args.tts_engine.upper()} TTS", file=sys.stderr)
        
        # Convert to audio
        converter = AudioConverter(tts_engine=args.tts_engine, voices=voices if voices else None)
        print(f"Converting to audio: {output_file}", file=sys.stderr)
        converter.convert_to_audio_sync(conversation, output_file)
        
        print(f"Podcast created: {output_file}", file=sys.stderr)
        return 0
        
    except Doc2ConvoError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 255


if __name__ == "__main__":
    sys.exit(main())