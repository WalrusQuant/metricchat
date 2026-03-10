from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import tiktoken
    logger.debug("tiktoken loaded successfully")
except Exception as _exc:  # pragma: no cover
    tiktoken = None  # type: ignore
    logger.warning("tiktoken is not available, falling back to word-split token counting: %s", _exc)


_DEFAULT_ENCODING = "cl100k_base"
_encoding_cache: dict[Optional[str], object] = {}
_warned_models: set[str] = set()


def _get_encoding(model_name: Optional[str]):
    if tiktoken is None:
        return None
    cache_key = model_name or _DEFAULT_ENCODING
    if cache_key in _encoding_cache:
        return _encoding_cache[cache_key]
    try:
        if model_name and hasattr(tiktoken, "encoding_for_model"):
            enc = tiktoken.encoding_for_model(model_name)
            _encoding_cache[cache_key] = enc
            return enc
    except Exception as e:
        if model_name not in _warned_models:
            logger.debug("tiktoken: no tokenizer for %s, using %s fallback", model_name, _DEFAULT_ENCODING)
            _warned_models.add(model_name)
    try:
        enc = tiktoken.get_encoding(_DEFAULT_ENCODING)
        _encoding_cache[cache_key] = enc
        return enc
    except Exception as e:
        logger.warning("tiktoken failed to load fallback encoding=%s: %s", _DEFAULT_ENCODING, e)
        _encoding_cache[cache_key] = None
        return None


def count_tokens(text: str, model_name: Optional[str] = None) -> int:
    """Count approximate tokens using tiktoken when available; fallback to words.

    Args:
        text: input string
        model_name: optional model identifier for a better encoding match
    """
    if not text:
        return 0
    enc = _get_encoding(model_name)
    if enc is None:
        logger.debug("tiktoken unavailable, using word-split fallback for token count")
        return max(1, len(text.split()))
    try:
        return len(enc.encode(text))
    except Exception as e:
        logger.warning("tiktoken encode failed, using word-split fallback: %s", e)
        return max(1, len(text.split()))
