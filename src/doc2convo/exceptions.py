# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""Custom exceptions for doc2convo package."""


class Doc2ConvoError(Exception):
    """Base exception for doc2convo package."""
    pass


class ConversionError(Doc2ConvoError):
    """Raised when conversion fails."""
    pass


class TTSError(Doc2ConvoError):
    """Raised when text-to-speech conversion fails."""
    pass


class ContentFetchError(Doc2ConvoError):
    """Raised when content fetching fails."""
    pass