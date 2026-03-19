import os
import numpy as np
import faiss
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

EMBEDDING_MODEL = "models/gemini-embedding-001"


def embed_texts(texts: list[str]) -> np.ndarray:
    """Generate embeddings for a list of texts using Gemini."""
    # Gemini embedding API supports batching
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=texts,
        task_type="retrieval_document",
    )
    return np.array(result["embedding"], dtype=np.float32)


def embed_query(query: str) -> np.ndarray:
    """Generate embedding for a single query."""
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=query,
        task_type="retrieval_query",
    )
    return np.array(result["embedding"], dtype=np.float32).reshape(1, -1)


def build_faiss_index(chunks: list[dict], document_id: str) -> tuple[faiss.IndexFlatIP, list[dict]]:
    """Build a FAISS index from chunks and save it."""
    texts = [c["content"] for c in chunks]

    # Embed in batches of 100 (Gemini batch limit)
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = embed_texts(batch)
        all_embeddings.append(embeddings)

    embeddings_matrix = np.vstack(all_embeddings)

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings_matrix)

    # Build index
    dimension = embeddings_matrix.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product = cosine sim after normalization
    index.add(embeddings_matrix)

    # Save index to disk
    store_dir = "faiss_stores"
    os.makedirs(store_dir, exist_ok=True)
    faiss.write_index(index, os.path.join(store_dir, f"{document_id}.index"))

    return index, chunks
