# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""Conversation generator using Claude AI."""

import random
import sys
from typing import Optional, Tuple

from anthropic import Anthropic

from ..exceptions import ConversionError


class ConversationGenerator:
    """Generate conversational content from documents using Claude AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the conversation generator.
        
        Args:
            api_key: Anthropic API key. If not provided, will use ANTHROPIC_API_KEY env var.
        """
        try:
            self.client = Anthropic(api_key=api_key)
        except Exception as e:
            raise ConversionError(f"Failed to initialize Anthropic client: {e}")
    
    def generate(self, title: str, content: str, url: str, 
                 system_prompt: Optional[str] = None) -> str:
        """Generate a conversation from the given content.
        
        Args:
            title: Title of the content
            content: Main content to convert
            url: Source URL
            system_prompt: Optional custom system prompt
            
        Returns:
            Generated conversation in markdown format
        """
        if not system_prompt:
            system_prompt = self._get_default_prompt()
        
        # Randomize speaker assignment
        speaker1, speaker2 = self._assign_speakers()
        
        prompt = f"""Based on the following article, create a natural, engaging conversation between two people discussing its content.

Title: {title}
URL: {url}

Article Content:
{content}

Create a conversation between {speaker1} and {speaker2} discussing this article. Make it sound like a natural podcast discussion where they explore the key points, share insights, and occasionally add their own perspectives. Include:

- A natural introduction mentioning the article title and what caught their attention
- Discussion of the main points with genuine reactions
- Questions and clarifications between the speakers
- Some light analysis or speculation about implications
- A brief wrap-up of key takeaways

Format the conversation with:
**{speaker1.upper()}:** [their dialogue]
**{speaker2.upper()}:** [their dialogue]

Make the conversation feel authentic, with natural speech patterns, occasional interruptions, and genuine interest in the topic."""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            raise ConversionError(f"Failed to generate conversation: {e}")
    
    def _get_default_prompt(self) -> str:
        """Get the default system prompt."""
        return """You are an AI that creates engaging podcast-style conversations between two speakers discussing articles and documents. Your conversations should:

1. Sound natural and conversational, like a real podcast
2. Include genuine reactions, questions, and insights
3. Break down complex topics in an accessible way
4. Maintain an engaging, friendly tone throughout
5. Use natural speech patterns including occasional filler words
6. Show both speakers contributing meaningfully to the discussion"""
    
    def _assign_speakers(self) -> Tuple[str, str]:
        """Randomly assign speaker names to avoid gender bias."""
        speakers = ["Alex", "Jordan"]
        random.shuffle(speakers)
        return speakers[0], speakers[1]