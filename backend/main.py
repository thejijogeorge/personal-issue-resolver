# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import json
from datetime import datetime

app = FastAPI()

# In-memory storage for now (switch to DB later)
issues_db = []

class Issue(BaseModel):
    problem: str
    context: str = ""

class Resolution(BaseModel):
    issue_id: str
    solution: str

@app.post("/issues")
def log_issue(issue: Issue):
    issue_record = {
        "id": str(len(issues_db)),
        "problem": issue.problem,
        "context": issue.context,
        "created_at": datetime.now().isoformat(),
        "resolved": False,
        "solution": None
    }
    issues_db.append(issue_record)
    return {"status": "logged", "issue_id": issue_record["id"]}

@app.get("/suggestions")
def get_suggestions(problem: str):
    # Use your RAG here
    # For now, just return similar issues by keyword matching
    similar = [i for i in issues_db if any(word in i['problem'].lower() for word in problem.lower().split())]
    return {"suggestions": similar[:3]}

@app.post("/resolve")
def resolve_issue(resolution: Resolution):
    for issue in issues_db:
        if issue["id"] == resolution.issue_id:
            issue["resolved"] = True
            issue["solution"] = resolution.solution
            return {"status": "resolved"}
    return {"status": "not found"}

@app.get("/issues")
def get_all_issues():
    return {"issues": issues_db}

@app.get("/")
def root():
    return {"status": "running"}