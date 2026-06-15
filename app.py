from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "log":
            problem = request.form.get("problem")
            context = request.form.get("context", "")

            response = requests.post(
                f"{API_URL}/issues",
                json={"problem": problem, "context": context}
            )
            result = response.json()
            return render_template("index.html", message=f"Issue logged: {result.get('issue_id')}")

        elif action == "search":
            problem = request.form.get("search_problem")
            context = request.form.get("search_context", "")

            response = requests.get(
                f"{API_URL}/suggestions",
                params={"problem": problem, "context": context}
            )
            suggestions = response.json()
            return render_template("index.html", suggestions=suggestions)

    # GET /issues to show all
    issues_response = requests.get(f"{API_URL}/issues")
    issues = issues_response.json().get("issues", [])

    return render_template("index.html", issues=issues)


if __name__ == "__main__":
    app.run(debug=True, port=5000)