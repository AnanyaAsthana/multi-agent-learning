from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_vector_store(chunks):
    embeddings = model.encode(chunks)
    dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    return index, chunks, model

def retrieve(query, index, chunks, model, k=3):
    q_emb = model.encode([query])
    D, I = index.search(np.array(q_emb), k)

    return [chunks[i] for i in I[0]]