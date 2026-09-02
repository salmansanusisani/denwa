"""Embeds chunk text into fixed-size vectors — free, fast and light for this laptop.

Provider strategy:
  1. fastembed (ONNX Runtime) — real semantic embeddings, runs locally on CPU,
     no GPU/CUDA, no API key. Model BAAI/bge-small-en-v1.5 (384-dim, ~30MB) is
     downloaded once to ~/.cache/fastembed. Override with the EMBEDDING_MODEL
     env var (any SentenceTransformer/ONNX model fastembed supports).
  2. Deterministic offline hashing fallback (no model download at all) if the
     model can't be loaded — keeps the pipeline runnable anywhere.

All vectors are L2-normalised so cosine similarity == plain dot product.
Vector dimension is constant within a run; check embedding_dim() if you need it.
"""
from __future__ import annotations

import hashlib
import os
import re

import numpy as np

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

try:
    from fastembed import TextEmbedding
except Exception:
    TextEmbedding = None

LOCAL_DIM = 300
_DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"

_STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "with", "is", "are",
    "do", "does", "you", "your", "we", "our", "i", "what", "how", "can", "any", "all",
    "at", "be", "it", "this", "that", "from", "as", "by", "up", "s",
}

_model = None
_model_name: str | None = None
_initialising = False


def _get_model():
    global _model, _model_name, _initialising
    if _model is not None:
        return _model
    if TextEmbedding is None or _initialising:
        return None
    _initialising = True
    try:
        name = os.getenv("EMBEDDING_MODEL", _DEFAULT_MODEL)
        _model = TextEmbedding(model_name=name)
        _model_name = name
    except Exception:
        _model = None
    finally:
        _initialising = False
    return _model


def _embed_with_fastembed(texts: list[str]) -> list[list[float]] | None:
    model = _get_model()
    if model is None or not texts:
        return None
    try:
        vectors = [np.asarray(v, dtype=np.float32) for v in model.embed(texts)]
        normed = []
        for v in vectors:
            norm = float(np.linalg.norm(v))
            normed.append((v / norm if norm > 0 else v).tolist())
        return normed
    except Exception:
        return None


def _tokenise(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _hash_token(token: str, dim: int) -> int:
    return int(hashlib.md5(token.encode("utf-8")).hexdigest()[:8], 16) % dim


def _local_embed(text: str) -> np.ndarray:
    counts = np.zeros(LOCAL_DIM, dtype=np.float32)
    tokens = _tokenise(text)
    for token in tokens:
        if token not in _STOPWORDS:
            counts[_hash_token(token, LOCAL_DIM)] += 1.0
    for first, second in zip(tokens, tokens[1:]):  # word bigrams carry word-order signal
        if first not in _STOPWORDS or second not in _STOPWORDS:
            counts[_hash_token(first + " " + second, LOCAL_DIM)] += 0.8
    norm = float(np.linalg.norm(counts))
    return counts / norm if norm > 0 else counts


def embed(text: str) -> list[float]:
    """Embed a single string into an L2-normalised vector."""
    return embed_batch([text])[0]


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Batch version — tries fastembed, falls back to local hashing."""
    if not texts:
        return []
    vectors = _embed_with_fastembed(texts)
    if vectors is not None and len(vectors) == len(texts):
        return vectors
    return [_local_embed(t).tolist() for t in texts]


def embedding_dim() -> int:
    """Actual vector dimension used by the active provider, for runtime checks."""
    sample = embed("just checking")
    return len(sample)