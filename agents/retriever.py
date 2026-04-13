from xml.parsers.expat import model

from utils.embeddings import retrieve

def retrieve_context(query, index, chunks, model, k=3):
    query = f"{query} explanation concept definition"
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, k)

    retrieved = [chunks[i] for i in I[0]]
    return "\n\n".join(retrieved)