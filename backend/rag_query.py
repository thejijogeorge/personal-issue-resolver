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

from ai_clients import get_chroma_client, get_ollama_client, embed

# Clients
chroma_client = get_chroma_client()
ollama_client = get_ollama_client()

# Collection - same one you already embedded docs into
collection = chroma_client.get_or_create_collection("my_knowledge_base")

def rag_query(question: str, n_results: int = 3) -> str:

    # Step 1 - Search ChromaDB for relevant chunks
    print(f"\n🔍 Searching for relevant context...")
    results = collection.query(
        query_embeddings=[embed(question)],
        n_results=n_results
    )

    # Step 2 - Extract the matching documents
    context_docs = results["documents"][0]
    context = "\n".join(context_docs)

    print(f"📄 Found {len(context_docs)} relevant chunks:")
    for i, doc in enumerate(context_docs):
        print(f"   {i+1}. {doc}")

    # Step 3 - Build prompt with context and question
    prompt = f"""You are a helpful assistant. Use only the context below to answer the question.
If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer:"""

    # Step 4 - Send to Ollama LLM for a real answer
    print(f"\n🤖 Generating answer...")
    response = ollama_client.generate(
        model="llama3.2:latest",   # change to whatever model you have pulled
        prompt=prompt
    )

    return response["response"]

# --- Test Questions (only run when file is executed directly) ---
if __name__ == "__main__":
    questions = [
        "how can AI help with fund management?",
        "what tools can I use for workflow automation?",
        "how do I run AI models without the cloud?",
        "what gaming consoles are available now?",
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"❓ Question: {question}")
        answer = rag_query(question)
        print(f"\n✅ Answer: {answer}")