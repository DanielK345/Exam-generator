import faiss
import numpy as np
from services.embedder import embed_query


def retrieve_chunks(
    query: str,
    index: faiss.IndexFlatIP,
    chunks: list[dict],
    top_k: int = 15,
) -> list[dict]:
    """Retrieve the top-K most relevant chunks for a query."""
    query_embedding = embed_query(query)
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, min(top_k, len(chunks)))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        chunk = chunks[idx].copy()
        chunk["score"] = float(score)
        results.append(chunk)

    return results
