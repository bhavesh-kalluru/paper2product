from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import numpy as np

def cosine_sim_matrix(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    A_norm = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-12)
    b_norm = b / (np.linalg.norm(b) + 1e-12)
    return A_norm @ b_norm

@dataclass
class VectorIndex:
    vectors: np.ndarray
    metadatas: List[Dict[str, Any]]
    texts: List[str]

def build_index(vectors: List[List[float]], metadatas: List[Dict[str, Any]], texts: List[str]) -> VectorIndex:
    mat = np.array(vectors, dtype=np.float32)
    return VectorIndex(vectors=mat, metadatas=metadatas, texts=texts)

def top_k(index: VectorIndex, query_vec: List[float], k: int = 8) -> List[Tuple[float, Dict[str, Any], str]]:
    q = np.array(query_vec, dtype=np.float32)
    sims = cosine_sim_matrix(index.vectors, q)
    k = min(k, len(sims))
    if k <= 0:
        return []
    idxs = np.argpartition(-sims, k - 1)[:k]
    idxs = idxs[np.argsort(-sims[idxs])]
    return [(float(sims[i]), index.metadatas[i], index.texts[i]) for i in idxs]
