"""Splits raw uploaded text into retrieval-sized chunks.

TODO(ai/ml):
- Simple fixed-size sliding window (e.g. ~200-400 tokens, some overlap) is enough for the hackathon.
- For structured FAQ docs (Q: / A: pairs), consider chunking per Q&A pair instead — likely gives
  cleaner retrieval than arbitrary windows.
"""
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source_document_id: int


def chunk_text(raw_text: str, document_id: int) -> list[Chunk]:
    """TODO(ai/ml): implement chunking. Return a list of Chunk."""
    raise NotImplementedError
