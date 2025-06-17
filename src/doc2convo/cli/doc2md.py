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
        description='Convert web articles or local files to conversational podcast format'
    )
    parser.add_argument('input', help='URL or local file path to convert')
    parser.add_argument('-o', '--output', help='Output file (default: auto-generated or stdout)')
    parser.add_argument('-s', '--system-prompt', help='Custom system prompt for conversation style')
    
    args = parser.parse_args()
    
    try:
        # Check for API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
            return 1
        
        # Fetch content
        fetcher = ContentFetcher()
        
        if is_url(args.input):
            title, content = fetcher.fetch_url(args.input)
            url = args.input
        else:
            title, content = fetcher.read_local_file(args.input)
            if title is None:
                return 1
            url = f"file://{Path(args.input).absolute()}"
        
        # Generate conversation
        generator = ConversationGenerator(api_key)
        conversation = generator.generate(title, content, url, args.system_prompt)
        
        # Output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(conversation)
            print(f"Conversation saved to: {args.output}", file=sys.stderr)
        else:
            # Always print to stdout when no output file is specified
            print(conversation)
        
        return 0
        
    except Doc2ConvoError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 255


if __name__ == "__main__":
    sys.exit(main())