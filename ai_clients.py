# ai_clients.py
# This `ai_clients.py` file is designed to provide client interfaces for interacting with two AI-related services: ChromaDB (a vector database) and Ollama (a framework for running large language models).
#
# Here's an outline of its contents:
#
# *   **Imports:**
#     *   `chromadb`: Used for connecting to and interacting with the ChromaDB vector database.
#     *   `ollama`: Used for connecting to and interacting with the Ollama language model server.
#     *   `os`: Standard library module for interacting with the operating system, primarily used here to access environment variables.
#     *   `dotenv.load_dotenv`: Used to load environment variables from a `.env` file, which helps in managing configuration without hardcoding sensitive information.
#
# *   **Configuration (Environment Variables):**
#     The script loads several configuration parameters from environment variables using `os.getenv()`:
#     *   **ChromaDB Configuration:**
#         *   `CHROMA_HOST`: The hostname for the ChromaDB server.
#         *   `CHROMA_PORT`: The port number for the ChromaDB server.
#         *   `CHROMA_TOKEN`: An authorization token for ChromaDB.
#     *   **Ollama Configuration:**
#         *   `OLLAMA_HOST`: The hostname for the Ollama server.
#         *   `OLLAMA_PORT`: The port number for the Ollama server.
#         *   `EMBED_MODEL`: The name of the embedding model to be used with Ollama.
#
# *   **Functions:**
#     *   `get_chroma_client()`:
#         *   Purpose: Initializes and returns a `chromadb.HttpClient` instance.
#         *   Configuration: Uses `CHROMA_HOST`, `CHROMA_PORT`, and `CHROMA_TOKEN` to set up the client, including an authorization header.
#     *   `get_ollama_client()`:
#         *   Purpose: Initializes and returns an `ollama.Client` instance.
#         *   Configuration: Constructs the host URL using `OLLAMA_HOST` and `OLLAMA_PORT`.
#     *   `embed(text: str) -> list`:
#         *   Purpose: Generates a vector embedding for a given text string using the configured Ollama server.
#         *   Process:
#             1.  Obtains an Ollama client using `get_ollama_client()`.
#             2.  Calls the `client.embeddings()` method, passing the `EMBED_MODEL` and the input `text`.
#             3.  Returns the `embedding` field from the Ollama response.

import chromadb
import ollama
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT"))
CHROMA_TOKEN = os.getenv("CHROMA_TOKEN")

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT"))
EMBED_MODEL = os.getenv("EMBED_MODEL")

def get_chroma_client():
    return chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        headers={"Authorization": f"Bearer {CHROMA_TOKEN}"}
    )

#Call Ollama using Ollama API
def get_ollama_client():
    return ollama.Client(
        host=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
    )

def embed(text: str) -> list:
    client = get_ollama_client()
    response = client.embeddings(
        model=EMBED_MODEL,
        prompt=text
    )
    return response["embedding"]

#call ollama using OpenAI API
def get_ollamaOAI_client():
    return OpenAI(
        api_key="ollama",  # dummy key, not needed
        base_url=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/v1"
    )