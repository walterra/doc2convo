# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""CLI for conversation markdown to audio conversion."""

import argparse
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


def main():
    """Main entry point for md-convo2mp3 command."""
    parser = argparse.ArgumentParser(
        description='Convert conversation markdown to audio using Edge TTS',
        epilog='Use "-" as input to read from stdin. Example: doc2md-convo URL | md-convo2mp3 - -o output.mp3'
    )
    parser.add_argument('input', help='Input markdown file (use - for stdin)')
    parser.add_argument('-o', '--output', help='Output audio file (default: auto-generated)')
    
    args = parser.parse_args()
    
    try:
        # Read input
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
            if args.input == '-':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"podcast_{timestamp}.mp3"
            else:
                # Replace -CONVO suffix with -podcast
                if input_name.endswith('-CONVO'):
                    base_name = input_name[:-6]
                else:
                    base_name = input_name
                output_file = f"{base_name}-podcast.mp3"
        
        # Convert to audio
        converter = AudioConverter()
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