from __future__ import annotations

import json
from typing import Any


MAX_MESSAGE_BYTES = 512_000


def encode_message(message_type: str, **payload: Any) -> bytes:
    data = {"type": message_type, **payload}
    return (json.dumps(data, separators=(",", ":")) + "\n").encode("utf-8")


def decode_message(raw: bytes) -> dict[str, Any]:
    if len(raw) > MAX_MESSAGE_BYTES:
        raise ValueError("message is too large")
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict) or "type" not in data:
        raise ValueError("invalid protocol message")
    return data

