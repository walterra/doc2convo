# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""Main CLI entry point for doc2convo."""

import sys


def main():
    """Main entry point that dispatches to doc2md-convo or md-convo2mp3."""
    print("doc2convo - Convert documents to conversational audio podcasts")
    print()
    print("Usage:")
    print("  doc2md-convo <url-or-file>  - Convert content to conversation markdown")
    print("  md-convo2mp3 <file>         - Convert conversation markdown to audio")
    print()
    print("For more help on each command, run it with --help")
    return 0


if __name__ == "__main__":
    sys.exit(main())