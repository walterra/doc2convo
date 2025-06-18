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
                 system_prompt: Optional[str] = None, 
                 tts_engine: str = "edge") -> str:
        """Generate a conversation from the given content.
        
        Args:
            title: Title of the content
            content: Main content to convert
            url: Source URL
            system_prompt: Optional custom system prompt
            tts_engine: TTS engine to use ("edge" or "orpheus")
            
        Returns:
            Generated conversation in markdown format
        """
        # Always use the default system prompt
        default_system_prompt = self._get_default_prompt()
        
        # Randomize speaker assignment and roles
        speaker1, speaker2 = self._assign_speakers()
        
        # Randomize role assignment to avoid bias
        if random.choice([True, False]):
            speaker1_role = "more analytical and detail-oriented, acting as the subject matter expert"
            speaker2_role = "more conversational, asking clarifying questions to help the audience understand"
        else:
            speaker1_role = "more conversational, asking clarifying questions to help the audience understand"
            speaker2_role = "more analytical and detail-oriented, acting as the subject matter expert"
        
        # Add custom system prompt section if provided
        system_prompt_section = ""
        if system_prompt:
            system_prompt_section = f"\n\nIMPORTANT: The following additional instructions should be considered with HIGH PRIORITY and can override any of the default requirements. The custom instructions take precedence over the defaults.\n\nBEGIN OF HIGH PRIORITY INSTRUCTIONS\n\n{system_prompt}\n\nEND OF HIGH PRIORITY INSTRUCTIONS\n\n"
        
        # Add Orpheus TTS-specific instructions if selected
        orpheus_section = ""
        if tts_engine == "orpheus":
            orpheus_section = """

Since you're using Orpheus TTS, you can include these special tags for more emotional voices:
<giggle>, <laugh>, <chuckle>, <sigh>, <cough>, <sniffle>, <groan>, <yawn>, <gasp>

Include these tags directly within spoken text to make the conversation more natural and emotive.
For example: "**ALEX:** That's <laugh> really funny! I hadn't thought about it that way."

Use these tags sparingly and naturally - don't overuse them. Only include them when they enhance the conversational flow.

IMPORTANT: Orpheus TTS will create sound snippets no longer than 14 seconds, you must ensure that each line of dialogue is concise and fits within this limit.
"""
        
        prompt = f"""Based on the following article, create a natural, engaging conversation between two people discussing its content.

Key requirements:
- Format as markdown with **SPEAKER:** prefix for each line
- {speaker1} tends to be {speaker1_role}
- {speaker2} tends to be {speaker2_role}
- Include natural conversation elements like reactions, follow-up questions, and transitions
- You must not use any code blocks or markdown formatting other than the **SPEAKER:** prefix
- You must not use any markdown elements like *laughs* or *pauses*; instead, use natural dialogue
- Make it feel like a real podcast discussion, not just reading facts
- Keep it engaging and accessible
- Length should be substantial but not excessive (aim for 15-25 exchanges)
{system_prompt_section}{orpheus_section}
Title: {title}
URL: {url}

Article Content:
{content[:8000]}

Create a conversation between {speaker1} and {speaker2} discussing this article. Make it sound like a natural podcast discussion where they explore the key points, share insights, and occasionally add their own perspectives.

Format the conversation with:
**{speaker1.upper()}:** [their dialogue]
**{speaker2.upper()}:** [their dialogue]"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.7,
                system=default_system_prompt,
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