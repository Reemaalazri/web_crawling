"""
Indexer module for COMP3011 Coursework 2.

This module converts page text into tokens and later builds an
inverted index containing frequency and positional information.
"""

from __future__ import annotations

import re


def tokenize(text: str) -> list[str]:
    """
    Convert raw text into lowercase alphanumeric tokens.

    Args:
        text: Raw text extracted from a web page.

    Returns:
        A list of cleaned lowercase tokens.
    """
    if not text:
        return []

    return re.findall(r"[a-zA-Z0-9]+", text.lower())