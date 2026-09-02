"""Splits raw uploaded text into retrieval-sized chunks.

Handles two common layouts:
  - Structured FAQ/policy text with "Q:" / "A:" (or "Question:" / "Answer:") markers:
    chunk per Q&A pair so retrieval keeps the answer with its question.
  - Free-form text: fixed-size sliding window (~WINDOW_WORDS words, some overlap).

No manual cleanup is required — chunking is fully automatic.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

WINDOW_WORDS = 300
OVERLAP_WORDS = 50

_Q_LINE = re.compile(r"^\s*(?:Q(?:uestion)?)\s*\d*\s*[:.\-]?\s*", re.I)
_A_LINE = re.compile(r"^\s*(?:A(?:nswer)?)\s*\d*\s*[:.\-]?\s*", re.I)


@dataclass
class Chunk:
    text: str
    source_document_id: int


def _normalise(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_qa_pairs(text: str) -> list[str]:
    """Chunk structured Q/A text into pairs: a question line plus everything up to
    the next question line (answers, follow-ups and sub-notes stay with their Q)."""
    pairs: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if _Q_LINE.match(line):
            if current:
                pairs.append("\n".join(current).strip())
            cleaned = _Q_LINE.sub("", line).strip()
            current = [cleaned] if cleaned else []
        else:
            current.append(_A_LINE.sub("", line) if _A_LINE.match(line) else line)
    if current:
        pairs.append("\n".join(current).strip())
    return [p for p in pairs if p]


def _sliding_windows(text: str) -> list[str]:
    words = text.split()
    if len(words) <= WINDOW_WORDS:
        return [text]
    step = WINDOW_WORDS - OVERLAP_WORDS
    chunks = []
    for start in range(0, len(words), step):
        window = words[start : start + WINDOW_WORDS]
        if len(window) < WINDOW_WORDS // 2:
            break
        chunks.append(" ".join(window))
    return chunks


def chunk_text(raw_text: str, document_id: int) -> list[Chunk]:
    """Split raw text into retrieval-sized chunks for a single document."""
    text = _normalise(raw_text)
    if not text:
        return []

    segments = _split_qa_pairs(text) if "Q:" in text or "Question:" in text else [text]
    pieces: list[str] = []
    for segment in segments:
        windows = _sliding_windows(segment)
        # Keep windows that are only barely overlapping as-is; dedupe near-identical ones.
        for w in windows:
            if w not in pieces:
                pieces.append(w)

    return [Chunk(text=p, source_document_id=document_id) for p in pieces]