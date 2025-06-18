# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""Command-line interface for doc2convo."""

from .main import main
from .doc2md import main as doc2md_main
from .md2mp3 import main as md2mp3_main

__all__ = ["main", "doc2md_main", "md2mp3_main"]