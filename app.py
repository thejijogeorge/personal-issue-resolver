#Run this after running the FAST API
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from datetime import datetime
import os

app = Flask(__name__)

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"
#API_URL = "http://fastapi:8000"


@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    suggestions = None
    now = datetime.now()

    # Always fetch issues
    issues_response = requests.get(f"{API_URL}/issues")
    issues = issues_response.json().get("issues", [])
    print("Current time(index):", now.strftime("%Y-%m-%d %H:%M:%S"))
    if request.method == "POST":
        action = request.form.get("action")
        print("Current time(app/POST):", now.strftime("%Y-%m-%d %H:%M:%S"))

        if action == "log":
            print("Current time(app/log issue):", now.strftime("%Y-%m-%d %H:%M:%S"))
            problem = request.form.get("problem")
            context = request.form.get("context", "")

            response = requests.post(
                f"{API_URL}/issues",
                json={"problem": problem, "context": context}
            )
            result = response.json()
            message = f"✅ Issue logged: {result.get('issue_id')}"
            # Redirect instead of rendering
            return redirect(url_for("index"))

        elif action == "search":
            print("Current time(app/search issue):", now.strftime("%Y-%m-%d %H:%M:%S"))
            problem = request.form.get("search_problem")
            context = request.form.get("search_context", "")

            response = requests.get(
                f"{API_URL}/suggestions",
                params={"problem": problem, "context": context}
            )
            suggestions = response.json()

        elif action == "resolve":
            print("Current time(app/resolve issue):", now.strftime("%Y-%m-%d %H:%M:%S"))
            issue_id = request.form.get("issue_id")
            solution = request.form.get("solution")

            response = requests.post(
                f"{API_URL}/resolve",
                json={"issue_id": issue_id, "solution": solution}
            )
            result = response.json()
            message = f"✅ Issue {issue_id} resolved: {result.get('status')}"
            # Redirect instead of rendering
            return redirect(url_for("index"))

    return render_template("index.html", issues=issues, message=message, suggestions=suggestions)

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")  # ← Add host="0.0.0.0"