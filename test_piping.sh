#!/bin/bash
# Test script demonstrating piping functionality

echo "Testing piping functionality..."
echo ""
echo "Example 1: Direct piping (URL to audio in one command)"
echo "python3 doc2md-convo.py https://example.com | python3 md-convo2mp3.py - -o output.mp3"
echo ""
echo "Example 2: Using intermediate file"
echo "python3 doc2md-convo.py https://example.com -o article.md"
echo "python3 md-convo2mp3.py article.md -o article.mp3"
echo ""
echo "Example 3: Reading from stdin with custom output"
echo "cat existing-convo.md | python3 md-convo2mp3.py - -o custom-output.mp3"