#!/usr/bin/env python3
# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.



"""
url2convo: URL/File to Conversation Generator
Uses Claude SDK to convert web content or local files into conversational podcast format
Supports URLs, .txt, .md, and .pdf files
"""


import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from anthropic import Anthropic
from bs4 import BeautifulSoup


def read_local_file(file_path):
    """Read content from local file (txt, md, pdf)"""
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            return None, None
        
        file_extension = path.suffix.lower()
        
        if file_extension == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    title = path.stem
                    return title, text.strip()
            except ImportError:
                print("Error: PyPDF2 not installed. Install with: pip install PyPDF2", file=sys.stderr)
                return None, None
        
        elif file_extension in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                title = path.stem
                return title, content.strip()
        
        else:
            print(f"Error: Unsupported file type: {file_extension}. Supported: .txt, .md, .pdf", file=sys.stderr)
            return None, None
            
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return None, None


def is_url(string):
    """Check if string is a URL"""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False


def fetch_url_content(url):
    """Fetch and clean content from URL"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        # Get text content
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        # Get title
        title = soup.title.string if soup.title else "Web Article"

        return title.strip(), text

    except Exception as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        return None, None


def generate_conversation(title, content, source, system_prompt=None):
    """Generate conversational summary using Claude"""

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        print(
            "Please set your API key: export ANTHROPIC_API_KEY='your-key-here'",
            file=sys.stderr,
        )
        return None

    client = Anthropic(api_key=api_key)

    # Add custom system prompt if provided
    system_prompt_section = ""
    if system_prompt:
        system_prompt_section = f"{system_prompt}\n\n"

    prompt_template = """You are tasked with creating a conversational podcast transcript from web content.

Create a dialogue between two podcast hosts named ALEX and JORDAN. They should discuss the content in an engaging, informative way with natural conversation flow.

Key requirements:
- Format as markdown with **SPEAKER:** prefix for each line
- ALEX tends to be more analytical and detail-oriented
- JORDAN is more conversational and asks clarifying questions, for example asking for explaining acronyms, technical terms, a person's background, etc.
- Include natural conversation elements like reactions, follow-up questions, and transitions
- You must not use any code blocks or markdown formatting other than the **SPEAKER:** prefix
- You must not use any markdown elements like *laughs* or *pauses*; instead, use natural dialogue
- Make it feel like a real podcast discussion, not just reading facts
- Keep it engaging and accessible
- Length should be substantial but not excessive (aim for 15-25 exchanges)

{system_prompt_section}Source: {source}
Title: {title}

Content to discuss:
{content}...

Generate the podcast transcript:"""

    prompt = prompt_template.format(
        system_prompt_section=system_prompt_section,
        source=source,
        title=title,
        content=content[:8000],
    )

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text

    except Exception as e:
        print(f"Error calling Claude API: {e}", file=sys.stderr)
        return None


def save_conversation(conversation, source, title):
    """Save conversation to markdown file"""
    # Create filename from title or source
    if title and title != "Web Article":
        filename = re.sub(r"[^\w\s-]", "", title)
        filename = re.sub(r"[-\s]+", "-", filename)
        filename = filename.strip("-").lower()
    else:
        if is_url(source):
            # Use domain name from URL
            domain = urlparse(source).netloc
            filename = domain.replace(".", "-")
        else:
            # Use file name without extension
            filename = Path(source).stem

    filename = f"{filename}-CONVO.md"

    # Add header with metadata
    source_type = "URL" if is_url(source) else "File"
    header = f"""# Conversational Summary - {title}
## Generated from {source_type}: {source}
## Date: {datetime.now().strftime('%B %d, %Y')}

"""

    full_content = header + conversation

    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_content)

    print(f"Conversation saved to: {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(
        description="Generate conversational podcast from URL or local file",
        epilog="If no output file is specified, writes to stdout for piping. Supports .txt, .md, and .pdf files.",
    )
    parser.add_argument("source", help="URL or local file path (.txt, .md, .pdf) to convert to conversation")
    parser.add_argument(
        "--output", "-o", help="Output filename (if not specified, writes to stdout)"
    )
    parser.add_argument(
        "--system-prompt",
        "-s",
        help="Additional system prompt to influence the conversation style",
    )

    args = parser.parse_args()

    # Only print status messages to stderr when outputting to stdout
    output_to_stdout = args.output is None

    def status_print(msg):
        if output_to_stdout:
            print(msg, file=sys.stderr)
        else:
            print(msg)

    # Determine if source is URL or file
    if is_url(args.source):
        status_print(f"Fetching content from URL: {args.source}")
        title, content = fetch_url_content(args.source)
        if not content:
            status_print("Failed to fetch content from URL")
            return 1
    else:
        status_print(f"Reading content from file: {args.source}")
        title, content = read_local_file(args.source)
        if not content:
            status_print("Failed to read content from file")
            return 1

    status_print(f"Found content: {title}")
    status_print(f"Content length: {len(content)} characters")
    status_print("Generating conversation with Claude...")

    conversation = generate_conversation(title, content, args.source, args.system_prompt)

    if not conversation:
        status_print("Failed to generate conversation")
        return 1

    if args.output:
        filename = args.output
        with open(filename, "w", encoding="utf-8") as f:
            source_type = "URL" if is_url(args.source) else "File"
            header = f"""# Conversational Summary - {title}
## Generated from {source_type}: {args.source}
## Date: {datetime.now().strftime('%B %d, %Y')}

"""
            f.write(header + conversation)
        print(f"Conversation saved to: {filename}")
        print("\nTo generate audio, run:")
        print("python3 edge_tts_converter.py")
        print(f"\nThis will create: {filename.replace('-CONVO.md', '-podcast.mp3')}")
    else:
        # Output to stdout for piping
        source_type = "URL" if is_url(args.source) else "File"
        header = f"""# Conversational Summary - {title}
## Generated from {source_type}: {args.source}
## Date: {datetime.now().strftime('%B %d, %Y')}

"""
        print(header + conversation)

    return 0


if __name__ == "__main__":
    sys.exit(main())
