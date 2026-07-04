import chromadb

# Create (or connect to) the persistent ChromaDB database
client = chromadb.PersistentClient(path="backend/chroma_db")

# Create (or load) the collection
collection = client.get_or_create_collection(
    name="documents"
)


def store_chunks(chunks, embeddings, document_name):
    """
    Store document chunks along with their embeddings and metadata.
    """

    # Create unique IDs
    ids = [
        f"{document_name}_chunk_{i}"
        for i in range(len(chunks))
    ]

    metadata = []

    for i in range(len(chunks)):
        metadata.append(
            {
                "document": document_name,
                "chunk": i
            }
        )

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadata
    )

    return len(chunks)


def search_chunks(query_embedding, n_results=25):
    """
    Search the vector database.
    """

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    return results