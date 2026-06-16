# main.py
#use uvicorn main:app --reload to run the app
# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import os
import sys

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

app = FastAPI()
now = datetime.now()
print("Current time:", now.strftime("%Y-%m-%d %H:%M:%S"))

from ai_clients import get_chroma_client, embed

# ============================================
# INITIALIZE CLIENTS
# ============================================
chroma_client = get_chroma_client()
collection = chroma_client.get_or_create_collection("issue_db")

# In-memory storage for issue metadata (temporary)
issues_db = []


# ============================================
# DATA MODELS
# ============================================
class Issue(BaseModel):
    problem: str
    context: str = ""


class Resolution(BaseModel):
    issue_id: str
    solution: str


# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
def root():
    return {"status": "running"}


# ============================================
# 1. LOG AN ISSUE (WITH EMBEDDINGS)
# ============================================
@app.post("/issues")
def log_issue(issue: Issue):
    """Log a new issue and embed it for RAG"""
    try:
        # Get next ID from ChromaDB collection size
        existing_issues = collection.get()
        issue_id = str(len(existing_issues["ids"]))

        # Combine problem and context for richer embedding
        combined_text = f"{issue.problem}. Context: {issue.context}"

        # Embed using Ollama
        embedding = embed(combined_text)

        # Store in ChromaDB (single source of truth)
        collection.add(
            ids=[issue_id],
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[{
                "problem": issue.problem,
                "context": issue.context,
                "resolved": False,
                "created_at": datetime.now().isoformat()
            }]
        )

        return {"status": "logged", "issue_id": issue_id}

    except Exception as e:
        print(f"ERROR logging issue: {str(e)}")
        return {"status": "error", "message": str(e)}



# ============================================
# 2. GET SUGGESTIONS (USING RAG)
# ============================================
@app.get("/suggestions")
def get_suggestions(problem: str, context: str = ""):
    """Get similar past issues using RAG (embeddings search)"""
    print("Current time(suggestion):", now.strftime("%Y-%m-%d %H:%M:%S"))

    # Combine problem and context (same way as logging)
    combined_text = f"{problem}. Context: {context}"

    # Embed the incoming problem
    query_embedding = embed(combined_text)

    # Query ChromaDB for similar issues
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    return {"suggestions": results}


# ============================================
# 3. RESOLVE AN ISSUE
# ============================================
@app.post("/resolve")
def resolve_issue(resolution: Resolution):
    """Mark an issue as resolved with a solution"""
    try:
        # Get all issues from ChromaDB
        results = collection.get()

        # Flatten the IDs in case they come as nested lists
        ids = results["ids"]
        if ids and isinstance(ids[0], list):
            ids = ids[0]

        # Find the issue by ID
        if resolution.issue_id not in ids:
            return {"status": "not found"}

        # Find the index of this issue
        idx = ids.index(resolution.issue_id)

        # Get current metadata
        # Get current metadata
        metadatas = results["metadatas"]
        if metadatas and isinstance(metadatas[0], list):
            metadatas = metadatas[0]


        current_metadata = metadatas[idx]

        # Update metadata with resolved status and solution
        updated_metadata = {
            "problem": current_metadata.get("problem"),
            "context": current_metadata.get("context"),
            "resolved": True,
            "solution": resolution.solution,
            "created_at": current_metadata.get("created_at")
        }

        # Update in ChromaDB
        collection.update(
            ids=[resolution.issue_id],
            metadatas=[updated_metadata]
        )

        return {"status": "resolved"}

    except Exception as e:
        print(f"ERROR resolving issue: {str(e)}")
        return {"status": "error", "message": str(e)}


# ============================================
# 4. VIEW ALL ISSUES
# ============================================
@app.get("/issues")
def get_all_issues():
    """Get all issues from ChromaDB"""
    try:
        # Get all items from ChromaDB collection
        results = collection.get()

        # Reconstruct issue records from ChromaDB data
        issues = []
        for i, issue_id in enumerate(results["ids"]):
            issue = {
                "id": issue_id,
                "problem": results["metadatas"][i].get("problem", ""),
                "context": results["metadatas"][i].get("context", ""),
                "resolved": results["metadatas"][i].get("resolved", False),
                "solution": results["metadatas"][i].get("solution"),
                "created_at": "N/A"  # ChromaDB doesn't store this, so use N/A
            }
            issues.append(issue)

        return {"issues": issues}
    except Exception as e:
        return {"issues": [], "error": str(e)}