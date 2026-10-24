"""Batched semantic embeddings via an OpenAI-compatible embeddings endpoint."""

import math
import httpx
from app.core.config import settings


def validate_vectors(vectors, count):
    if len(vectors) != count:
        raise ValueError("Embedding count mismatch")
    size = None
    for vector in vectors:
        if not isinstance(vector, list) or not vector:
            raise ValueError("Invalid embedding")
        if size is None:
            size = len(vector)
        if len(vector) != size or any(
            isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
            for v in vector
        ) or not any(vector):
            raise ValueError("Invalid embedding dimensions or values")
    return vectors


async def embed_texts(texts):
    if not texts:
        return []
    key = settings.ai_embedding_api_key or settings.ai_api_key
    if not key:
        raise ValueError("An embedding API key is required")
    base = settings.ai_embedding_base_url or settings.ai_base_url
    vectors = []
    async with httpx.AsyncClient(timeout=30) as client:
        for start in range(0, len(texts), 32):
            batch = texts[start:start + 32]
            response = await client.post(
                base.rstrip("/") + "/embeddings",
                headers={"Authorization": "Bearer " + key},
                json={"model": settings.ai_embedding_model, "input": batch, "encoding_format": "float"},
            )
            response.raise_for_status()
            data = sorted(response.json()["data"], key=lambda item: item["index"])
            if [item["index"] for item in data] != list(range(len(batch))):
                raise ValueError("Embedding indexes mismatch")
            vectors.extend(item["embedding"] for item in data)
    return validate_vectors(vectors, len(texts))
