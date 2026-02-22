from __future__ import annotations

from hashlib import blake2b


class DeterministicEmbedder:
    def __init__(self, dimensions: int = 16) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        digest = blake2b(text.encode("utf-8"), digest_size=self.dimensions).digest()
        return [round((byte / 255.0) * 2 - 1, 6) for byte in digest]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
