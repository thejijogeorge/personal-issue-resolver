# This Python script demonstrates a basic Retrieval Augmented Generation (Chroma Vecor Embedding) setup using ChromaDB for vector storage and Ollama for embeddings.
#
# Here's an outline of its functionality:
#
# *   **Setup and Initialization:**
#     *   Loads environment variables using `dotenv`.
#     *   Imports `get_chroma_client` and `embed` functions from `ai_clients.py`.
#     *   Initializes a ChromaDB client.
#     *   Gets or creates a ChromaDB collection named "my_knowledge_base".
#
# *   **Data Preparation:**
#     *   Defines a list of sample documents, each with an `id` and `text`. These documents represent a small knowledge base.
#
# *   **Adding Documents to ChromaDB:**
#     *   Iterates through the `docs` list.
#     *   For each document, it generates an embedding using the `embed` function (which likely uses Ollama).
#     *   Adds the document's `id`, generated `embedding`, and `text` to the ChromaDB collection.
#     *   Prints a confirmation message indicating the number of documents added.
#
# *   **Query Testing:**
#     *   Defines a list of sample `queries` to test the Chroma Vecor Embedding system.
#     *   Iterates through each `query`:
#         *   Generates an embedding for the `query` using the `embed` function.
#         *   Performs a similarity search in the ChromaDB collection using `collection.query()`, requesting the top 2 results (`n_results=2`).
#         *   Prints the original `query`.
#         *   Prints the retrieved documents (their text content) that are most similar to the query.
import os
import sys

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# If you are in a subfolder, this moves up ONE level to the root
root_dir = os.path.dirname(current_dir)

# Add root to path
sys.path.append(root_dir)


from dotenv import load_dotenv
load_dotenv()



from ai_clients import get_chroma_client, embed

client = get_chroma_client()
collection = client.get_or_create_collection("my_knowledge_base")

# Sample documents
docs = [
    {
        "id": "1",
        "text": "AI is transforming fund management by automating portfolio rebalancing and risk analysis."
    },
    {
        "id": "2",
        "text": "Python is the most popular language for building AI applications and data pipelines."
    },
    {
        "id": "3",
        "text": "ChromaDB is a vector database used to store and search embeddings for AI applications."
    },
    {
        "id": "4",
        "text": "The PlayStation 5 and Xbox Series X are the current generation consoles released in 2020."
    },
    {
        "id": "5",
        "text": "YouTube channels focused on AI tools and automation are growing rapidly in 2024."
    },
    {
        "id": "6",
        "text": "Chroma Vecor Embedding stands for Retrieval Augmented Generation, it gives AI models access to your own data."
    },
    {
        "id": "7",
        "text": "Ollama allows you to run large language models locally without sending data to the cloud."
    },
    {
        "id": "8",
        "text": "Business analysts can use AI to automate repetitive reporting and data summarisation tasks."
    },
    {
        "id": "9",
        "text": "Docker makes it easy to deploy and manage self hosted applications like ChromaDB and Ollama."
    },
    {
        "id": "10",
        "text": "n8n is an open source workflow automation tool that integrates with AI services and APIs."
    },
]

# Add all documents
collection.add(
    ids=[d["id"] for d in docs],
    embeddings=[embed(d["text"]) for d in docs],
    documents=[d["text"] for d in docs]
)

print(f"✅ Added {len(docs)} documents to ChromaDB")

# --- Test Queries ---
queries = [
    "how can AI help with fund management?",
    "what tools can I use for workflow automation?",
    "how do I run AI models without the cloud?",
    "what gaming consoles are available now?",
    "how can I grow a YouTube channel about technology?",
]

print("\n--- Query Results ---\n")
for query in queries:
    results = collection.query(
        query_embeddings=[embed(query)],
        n_results=2
    )
    print(f"🔍 Query: {query}")
    for doc in results["documents"][0]:
        print(f"   → {doc}")
    print()