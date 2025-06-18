# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""CLI for document to conversation markdown conversion."""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from ..generators import ConversationGenerator
from ..utils import ContentFetcher
from ..exceptions import Doc2ConvoError


def is_url(input_string):
    """Check if the input string is a URL."""
    try:
        result = urlparse(input_string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def sanitize_filename(filename):
    """Sanitize filename for safe file system usage."""
    import re
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename[:100]


def main():
    """Main entry point for doc2md-convo command."""
    parser = argparse.ArgumentParser(
        description='Convert web articles or local files to conversational podcast format',
        epilog="If no output file is specified, writes to stdout for piping. Supports .txt, .md, and .pdf files."
    )
    parser.add_argument('input', help='URL or local file path to convert')
    parser.add_argument('-o', '--output', help='Output file (default: auto-generated or stdout)')
    parser.add_argument('-s', '--system-prompt', help='Custom system prompt for conversation style')
    
    args = parser.parse_args()
    
    # Only print status messages to stderr when outputting to stdout
    output_to_stdout = args.output is None

    def status_print(msg):
        if output_to_stdout:
            print(msg, file=sys.stderr)
        else:
            print(msg)
    
    try:
        # Check for API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
            print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'", file=sys.stderr)
            return 1
        
        # Fetch content
        fetcher = ContentFetcher()
        
        if is_url(args.input):
            status_print(f"Fetching content from URL: {args.input}")
            title, content = fetcher.fetch_url(args.input)
            if not content:
                status_print("Failed to fetch content from URL")
                return 1
            url = args.input
        else:
            status_print(f"Reading content from file: {args.input}")
            title, content = fetcher.read_local_file(args.input)
            if title is None:
                status_print("Failed to read content from file")
                return 1
            url = f"file://{Path(args.input).absolute()}"
        
        status_print(f"Found content: {title}")
        status_print(f"Content length: {len(content)} characters")
        status_print("Generating conversation with Claude...")
        
        # Generate conversation
        generator = ConversationGenerator(api_key)
        conversation = generator.generate(title, content, url, args.system_prompt)
        
        if not conversation:
            status_print("Failed to generate conversation")
            return 1
        
        # Output
        if args.output:
            # Add header with metadata
            source_type = "URL" if is_url(args.input) else "File"
            header = f"""# Conversational Summary - {title}
## Generated from {source_type}: {args.input}
## Date: {datetime.now().strftime('%B %d, %Y')}

"""
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(header + conversation)
            print(f"Conversation saved to: {args.output}")
            print("\nTo generate audio, run:")
            print("md-convo2mp3")
            output_base = Path(args.output).stem
            if output_base.endswith('-CONVO'):
                podcast_name = output_base[:-6] + '-podcast.mp3'
            else:
                podcast_name = output_base + '-podcast.mp3'
            print(f"\nThis will create: {podcast_name}")
        else:
            # Always print to stdout when no output file is specified
            source_type = "URL" if is_url(args.input) else "File"
            header = f"""# Conversational Summary - {title}
## Generated from {source_type}: {args.input}
## Date: {datetime.now().strftime('%B %d, %Y')}

"""
            print(header + conversation)
        
        return 0
        
    except Doc2ConvoError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 255


if __name__ == "__main__":
    sys.exit(main())