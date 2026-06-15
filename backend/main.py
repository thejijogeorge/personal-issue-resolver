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
    print("Current time(log issue):", now.strftime("%Y-%m-%d %H:%M:%S"))
    try:
        issue_record = {
            "id": str(len(issues_db)),
            "problem": issue.problem,
            "context": issue.context,
            "created_at": datetime.now().isoformat(),
            "resolved": False,
            "solution": None
        }
        issues_db.append(issue_record)

        # ===== NEW: EMBED AND STORE IN CHROMADB =====

        # Combine problem and context for richer embedding
        combined_text = f"{issue.problem}. Context: {issue.context}"

        # Embed using Ollama (via ai_clients.embed())
        embedding = embed(combined_text)

        # Store in ChromaDB
        collection.add(
            ids=[issue_record["id"]],
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[{
                "problem": issue.problem,
                "context": issue.context,
                "resolved": False,
             #   "solution": None
            }]
        )

        return {"status": "logged", "issue_id": issue_record["id"]}

    except Exception as e:
        print(f"ERROR: {str(e)}")
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
    print("Current time(resolve):", now.strftime("%Y-%m-%d %H:%M:%S"))

    for issue in issues_db:
        if issue["id"] == resolution.issue_id:
            issue["resolved"] = True
            issue["solution"] = resolution.solution

            # TODO: Update in ChromaDB too

            return {"status": "resolved"}

    return {"status": "not found"}


# ============================================
# 4. VIEW ALL ISSUES
# ============================================
@app.get("/issues")

def get_all_issues():
    print("Current time(get all issues):", now.strftime("%Y-%m-%d %H:%M:%S"))
    """View all logged issues"""
    return {"issues": issues_db}