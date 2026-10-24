"""Persistent local vector snapshots with content/model version invalidation.

SQLite stores vectors as JSON; exact cosine search is suitable for a small policy
library. No extension, pickle files or access to HR business tables is required.
"""

import asyncio
from hashlib import sha256
import json
import math
from pathlib import Path
import sqlite3
from app.core.config import settings
from .embeddings import embed_texts, validate_vectors


def _snapshot(namespace, fingerprint, vectors=None):
    path = Path(settings.policy_vector_db)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path, timeout=10) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS policy_vectors(namespace TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, vectors TEXT NOT NULL)")
        if vectors is not None:
            conn.execute(
                "INSERT INTO policy_vectors VALUES(?,?,?) ON CONFLICT(namespace) DO UPDATE SET fingerprint=excluded.fingerprint,vectors=excluded.vectors",
                (namespace, fingerprint, json.dumps(vectors, allow_nan=False)),
            )
            return vectors
        row = conn.execute("SELECT vectors FROM policy_vectors WHERE namespace=? AND fingerprint=?", (namespace, fingerprint)).fetchone()
        return json.loads(row[0]) if row else None


def cosine_scores(vectors, query):
    validate_vectors([query] + vectors, len(vectors) + 1)
    norm = math.sqrt(sum(v * v for v in query))
    return [sum(a*b for a, b in zip(v, query)) / (math.sqrt(sum(x*x for x in v))*norm) for v in vectors]


async def search(chunks, sources, question):
    identity = [settings.ai_embedding_base_url or settings.ai_base_url, settings.ai_embedding_model]
    namespace = sha256(json.dumps(identity).encode()).hexdigest()
    fingerprint = sha256(json.dumps([chunks, sources], sort_keys=True).encode()).hexdigest()
    vectors = await asyncio.to_thread(_snapshot, namespace, fingerprint)
    if vectors is None:
        vectors = validate_vectors(await embed_texts(chunks), len(chunks))
        await asyncio.to_thread(_snapshot, namespace, fingerprint, vectors)
    validate_vectors(vectors, len(chunks))
    query = (await embed_texts([question]))[0]
    scores = cosine_scores(vectors, query)
    selected = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [(i, scores[i]) for i in selected[:3] if scores[i] >= settings.policy_similarity_threshold]
