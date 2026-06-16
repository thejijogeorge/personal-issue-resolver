# Outline:
# 1. Imports
# 2. Flask App Initialization
# 3. Configuration (FastAPI backend URL)
# 4. Route Definition for the main page ("/")
#    a. Handles GET requests to display issues and suggestions
#    b. Handles POST requests for:
#       i. Logging new issues
#       ii. Searching for issue suggestions
#       iii. Resolving existing issues
# 5. Main execution block to run the Flask app

# --- 1. Imports ---
# Import necessary modules from Flask for web application development
from flask import Flask, render_template, request, jsonify, redirect, url_for
# Import the requests library to make HTTP requests to the FastAPI backend
import requests
# Import datetime for handling timestamps
from datetime import datetime
# Import os for operating system related functionalities (though not heavily used here)
import os

# --- 2. Flask App Initialization ---
# Create a Flask web application instance
app = Flask(__name__)

# --- 3. Configuration (FastAPI backend URL) ---
# Define the URL for the FastAPI backend service.
# This allows the Flask app to communicate with the FastAPI service to manage issues.
# The commented-out line is for local development, while the active one is for Dockerized environments.
API_URL = "http://127.0.0.1:8000"
#API_URL = "http://fastapi:8000"


# --- 4. Route Definition for the main page ("/") ---
# Decorator to define a route for the root URL ("/")
# This function will handle both GET and POST requests to this URL.
@app.route("/", methods=["GET", "POST"])
def index():
    # Initialize variables to store messages and suggestions, which will be passed to the template
    message = None
    suggestions = None
    # Get the current time for logging purposes
    now = datetime.now()

    # Always fetch issues when the index page is loaded or refreshed.
    # This ensures the list of issues is up-to-date.
    issues_response = requests.get(f"{API_URL}/issues")
    # Parse the JSON response and extract the 'issues' list, defaulting to an empty list if not found
    issues = issues_response.json().get("issues", [])
    print("Current time(index):", now.strftime("%Y-%m-%d %H:%M:%S"))

    # Check if the request method is POST, indicating a form submission
    if request.method == "POST":
        # Get the 'action' field from the form data to determine which operation to perform
        action = request.form.get("action")
        print("Current time(app/POST):", now.strftime("%Y-%m-%d %H:%M:%S"))

        # --- 4.b.i. Handling 'log' action (Logging new issues) ---
        if action == "log":
            print("Current time(app/log issue):", now.strftime("%Y-%m-%d %H:%M:%S"))
            # Extract 'problem' and 'context' from the form
            problem = request.form.get("problem")
            context = request.form.get("context", "")

            # Send a POST request to the FastAPI backend to log a new issue
            response = requests.post(
                f"{API_URL}/issues",
                json={"problem": problem, "context": context}
            )
            # Parse the response from the backend
            result = response.json()
            # Set a success message
            message = f"✅ Issue logged: {result.get('issue_id')}"
            # Redirect to the index page to prevent form resubmission on refresh and display updated issues
            return redirect(url_for("index"))

        # --- 4.b.ii. Handling 'search' action (Searching for issue suggestions) ---
        elif action == "search":
            print("Current time(app/search issue):", now.strftime("%Y-%m-%d %H:%M:%S"))
            # Extract 'search_problem' and 'search_context' from the form
            problem = request.form.get("search_problem")
            context = request.form.get("search_context", "")

            # Send a GET request to the FastAPI backend to get suggestions based on the problem and context
            response = requests.get(
                f"{API_URL}/suggestions",
                params={"problem": problem, "context": context}
            )
            # Store the suggestions received from the backend
            suggestions = response.json()

        # --- 4.b.iii. Handling 'resolve' action (Resolving existing issues) ---
        elif action == "resolve":
            print("Current time(app/resolve issue):", now.strftime("%Y-%m-%d %H:%M:%S"))
            # Extract 'issue_id' and 'solution' from the form
            issue_id = request.form.get("issue_id")
            solution = request.form.get("solution")

            # Send a POST request to the FastAPI backend to resolve an issue
            response = requests.post(
                f"{API_URL}/resolve",
                json={"issue_id": issue_id, "solution": solution}
            )
            # Parse the response from the backend
            result = response.json()
            # Set a success message
            message = f"✅ Issue {issue_id} resolved: {result.get('status')}"
            # Redirect to the index page to prevent form resubmission on refresh and display updated issues
            return redirect(url_for("index"))

    # --- 4.a. Handles GET requests to display issues and suggestions ---
    # Render the 'index.html' template, passing the fetched issues, any messages, and suggestions
    # This is executed for initial page loads (GET requests) or after POST requests that don't redirect.
    return render_template("index.html", issues=issues, message=message, suggestions=suggestions)

# --- 5. Main execution block to run the Flask app ---
# This ensures the Flask development server runs only when the script is executed directly
if __name__ == "__main__":
    # Run the Flask application
    # debug=True enables debug mode, providing detailed error messages and auto-reloading
    # port=5000 sets the port the application listens on
    # host="0.0.0.0" makes the server accessible from any IP address, useful in Docker or network environments
    app.run(debug=True, port=5000, host="0.0.0.0")
