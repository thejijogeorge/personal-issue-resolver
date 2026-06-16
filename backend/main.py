# Outline:
# 1. Imports and Path Configuration
# 2. FastAPI App Initialization
# 3. AI Clients Initialization (ChromaDB)
# 4. Data Models Definition (Pydantic)
# 5. API Endpoints
#    a. Root Endpoint
#    b. Log an Issue Endpoint (POST /issues)
#    c. Get Suggestions Endpoint (GET /suggestions)
#    d. Resolve an Issue Endpoint (POST /resolve)
#    e. Get All Issues Endpoint (GET /issues)

# --- 1. Imports and Path Configuration ---
# main.py
# Use `uvicorn main:app --reload` to run the app in development mode.

# Import FastAPI for building the API
from fastapi import FastAPI
# Import BaseModel from Pydantic for data validation and serialization
from pydantic import BaseModel
# Import datetime for handling timestamps
from datetime import datetime
# Import os for interacting with the operating system, e.g., path manipulation
import os
# Import sys for system-specific parameters and functions, e.g., modifying the Python path
import sys

# Get the directory of the current file (main.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the root directory of the project by going up one level from the current directory
root_dir = os.path.dirname(current_dir)
# Add the root directory to the Python system path. This allows importing modules from the root,
# such as 'ai_clients' which is likely located there.
sys.path.append(root_dir)

# --- 2. FastAPI App Initialization ---
# Create a FastAPI application instance
app = FastAPI()
# Get the current time, primarily for logging purposes
now = datetime.now()
print("Current time:", now.strftime("%Y-%m-%d %H:%M:%S"))

# Import AI client functions from the 'ai_clients' module.
# `get_chroma_client` is used to initialize the ChromaDB client.
# `embed` is used to generate embeddings for text.
from ai_clients import get_chroma_client, embed

# --- 3. AI Clients Initialization (ChromaDB) ---
# Initialize the ChromaDB client. ChromaDB is used as a vector database
# to store and retrieve issue embeddings.
chroma_client = get_chroma_client()
# Get or create a collection named "issue_db" in ChromaDB.
# This collection will store the issues, their embeddings, and metadata.
collection = chroma_client.get_or_create_collection("issue_db")

# In-memory storage for issue metadata (temporary).
# This variable appears to be unused in the current implementation, as ChromaDB is the primary storage.
issues_db = []


# --- 4. Data Models Definition (Pydantic) ---
# Define the data model for an 'Issue' using Pydantic's BaseModel.
# This ensures that incoming request bodies conform to this structure.
class Issue(BaseModel):
    problem: str  # The core problem description (required)
    context: str = ""  # Additional context for the problem (optional, defaults to empty string)

# Define the data model for a 'Resolution'.
# This is used when an issue is being marked as resolved.
class Resolution(BaseModel):
    issue_id: str  # The unique identifier of the issue to be resolved
    solution: str  # The solution provided for the issue


# --- 5. API Endpoints ---

# --- 5.a. Root Endpoint ---
# Defines a GET endpoint for the root URL ("/").
# This is a simple health check to confirm the API is running.
@app.get("/")
def root():
    return {"status": "running"}


# --- 5.b. Log an Issue Endpoint (POST /issues) ---
# Defines a POST endpoint to log a new issue.
# It expects an 'Issue' object in the request body.
@app.post("/issues")
def log_issue(issue: Issue):
    """Log a new issue and embed it for RAG"""
    try:
        # Get the next available ID for the new issue.
        # This is determined by the current number of items in the ChromaDB collection.
        existing_issues = collection.get()
        issue_id = str(len(existing_issues["ids"]))

        # Combine the problem and context into a single string for embedding.
        # This creates a richer representation for similarity search.
        combined_text = f"{issue.problem}. Context: {issue.context}"

        # Generate an embedding (vector representation) of the combined text using the 'embed' function.
        # This function likely interfaces with an AI model (e.g., Ollama).
        embedding = embed(combined_text)

        # Store the issue in ChromaDB.
        # Each issue is stored with its ID, embedding, the original combined text (document),
        # and additional metadata including problem, context, resolved status, and creation timestamp.
        collection.add(
            ids=[issue_id],
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[{
                "problem": issue.problem,
                "context": issue.context,
                "resolved": False,  # New issues are initially unresolved
                "created_at": datetime.now().isoformat() # Record creation time
            }]
        )

        # Return a success response with the ID of the newly logged issue.
        return {"status": "logged", "issue_id": issue_id}

    except Exception as e:
        # If an error occurs during the logging process, return an error status and message.
        print(f"ERROR logging issue: {str(e)}")
        return {"status": "error", "message": str(e)}


# --- 5.c. Get Suggestions Endpoint (GET /suggestions) ---
# Defines a GET endpoint to retrieve suggestions for a given problem.
# It takes 'problem' and 'context' as query parameters.
@app.get("/suggestions")
def get_suggestions(problem: str, context: str = ""):
    """Get similar past issues using RAG (embeddings search)"""
    print("Current time(suggestion):", now.strftime("%Y-%m-%d %H:%M:%S"))

    # Combine the incoming problem and context, similar to how issues are logged.
    combined_text = f"{problem}. Context: {context}"

    # Generate an embedding for the query text.
    query_embedding = embed(combined_text)

    # Query ChromaDB to find issues that are semantically similar to the query embedding.
    # It requests the top 3 most similar results.
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    # Return the suggestions found by ChromaDB.
    return {"suggestions": results}


# --- 5.d. Resolve an Issue Endpoint (POST /resolve) ---
# Defines a POST endpoint to mark an existing issue as resolved.
# It expects a 'Resolution' object in the request body.
@app.post("/resolve")
def resolve_issue(resolution: Resolution):
    """Mark an issue as resolved with a solution"""
    try:
        # Retrieve all issues from the ChromaDB collection.
        results = collection.get()

        # Extract issue IDs. Handle potential nested list format from ChromaDB.
        ids = results["ids"]
        if ids and isinstance(ids[0], list):
            ids = ids[0]

        # Check if the provided issue_id exists in the collection.
        if resolution.issue_id not in ids:
            return {"status": "not found"}

        # Find the index of the issue to be resolved.
        idx = ids.index(resolution.issue_id)

        # Extract metadata. Handle potential nested list format from ChromaDB.
        metadatas = results["metadatas"]
        if metadatas and isinstance(metadatas[0], list):
            metadatas = metadatas[0]

        # Get the current metadata for the specific issue.
        current_metadata = metadatas[idx]

        # Create updated metadata, setting 'resolved' to True and adding the 'solution'.
        # It preserves existing 'problem', 'context', and 'created_at' fields.
        updated_metadata = {
            "problem": current_metadata.get("problem"),
            "context": current_metadata.get("context"),
            "resolved": True,
            "solution": resolution.solution,
            "created_at": current_metadata.get("created_at")
        }

        # Update the issue's metadata in ChromaDB.
        collection.update(
            ids=[resolution.issue_id],
            metadatas=[updated_metadata]
        )

        # Return a success response.
        return {"status": "resolved"}

    except Exception as e:
        # If an error occurs during resolution, return an error status and message.
        print(f"ERROR resolving issue: {str(e)}")
        return {"status": "error", "message": str(e)}


# --- 5.e. Get All Issues Endpoint (GET /issues) ---
# Defines a GET endpoint to retrieve all issues stored in ChromaDB.
@app.get("/issues")
def get_all_issues():
    """Get all issues from ChromaDB"""
    try:
        # Retrieve all items (IDs, documents, and metadatas) from the ChromaDB collection.
        results = collection.get(include=['metadatas']) # Explicitly include metadatas

        # Reconstruct a list of issue dictionaries from the retrieved ChromaDB data.
        issues = []
        # Iterate through the IDs and their corresponding metadata.
        for i, issue_id in enumerate(results["ids"]):
            # Create an issue dictionary, populating it with data from metadata.
            issue = {
                "id": issue_id,
                "problem": results["metadatas"][i].get("problem", ""),
                "context": results["metadatas"][i].get("context", ""),
                "resolved": results["metadatas"][i].get("resolved", False),
                "solution": results["metadatas"][i].get("solution"),
                "created_at": results["metadatas"][i].get("created_at", "N/A") # Use stored created_at or N/A
            }
            issues.append(issue)

        # Return the list of issues.
        return {"issues": issues}
    except Exception as e:
        # If an error occurs, return an empty list of issues and an error message.
        return {"issues": [], "error": str(e)}
