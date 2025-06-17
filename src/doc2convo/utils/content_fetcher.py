# Copyright (c) 2025 Walter M. Rafelsberger
# Licensed under the MIT License. See LICENSE file for details.

"""Content fetching utilities for URLs and local files."""

import sys
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from ..exceptions import ContentFetchError


class ContentFetcher:
    """Fetch content from URLs and local files."""
    
    @staticmethod
    def fetch_url(url: str) -> Tuple[str, str]:
        """Fetch content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Tuple of (title, content)
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.string if title else urlparse(url).netloc
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return title_text, text
            
        except requests.RequestException as e:
            raise ContentFetchError(f"Failed to fetch URL {url}: {e}")
        except Exception as e:
            raise ContentFetchError(f"Error processing URL {url}: {e}")
    
    @staticmethod
    def read_local_file(file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Read content from local file (txt, md, pdf).
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (title, content) or (None, None) if error
        """
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
                    print("Error: PyPDF2 not installed. Install with: pip install PyPDF2", 
                          file=sys.stderr)
                    return None, None
                except Exception as e:
                    print(f"Error reading PDF: {e}", file=sys.stderr)
                    return None, None
                    
            elif file_extension in ['.txt', '.md']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        title = path.stem
                        return title, content
                except Exception as e:
                    print(f"Error reading file: {e}", file=sys.stderr)
                    return None, None
                    
            else:
                print(f"Error: Unsupported file type: {file_extension}", file=sys.stderr)
                return None, None
                
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return None, None