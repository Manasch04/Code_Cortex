from flask import Flask, request, render_template, redirect, url_for, send_file
import requests
import json
import os
import zipfile
from werkzeug.utils import secure_filename
from datetime import datetime

# Replace with your actual Standard Flow API Key
API_KEY = "38ZkLSbFljRqfxu6y4vB0NCBrMwAY0lVRgU81A90o7b6kArlRM3ZJQQJ99BDAAAAAAAAAAAAINFRAZML38nM"  # Use your Standard Flow API Key
ENDPOINT_URL = "https://codecortexpipeline.eastus.inference.ml.azure.com/score"  # Replace with your correct endpoint

# Correct header for Standard Flow
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"  # Ensure the correct key format
}

# Create necessary folders
UPLOAD_FOLDER = "uploads"
HISTORY_FOLDER = "history"
USER_SUBMISSIONS_FOLDER = "user_submissions"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)
os.makedirs(USER_SUBMISSIONS_FOLDER, exist_ok=True)

# Flask setup
app = Flask(__name__, template_folder="frontend")  # Updated to use the "frontend" folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Landing Page
@app.route("/")
def home():
    return render_template("home.html")

# User Input Page
@app.route("/input", methods=["GET", "POST"])
def user_input():
    if request.method == "POST":
        developer_name = request.form.get("developer_name")
        code_type = request.form.get("code_type")
        return redirect(url_for("submit_code", developer_name=developer_name, code_type=code_type))
    return render_template("input.html")

# Code Submission Page
@app.route("/submit", methods=["GET", "POST"])
def submit_code():
    developer_name = request.args.get("developer_name")
    code_type = request.args.get("code_type")
    if request.method == "POST":
        code_content = request.form.get("code_content")
        zip_file = request.files.get("zip_file")

        # Save user submission
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_submission_path = os.path.join(USER_SUBMISSIONS_FOLDER, f"{developer_name}_{timestamp}")
        os.makedirs(user_submission_path, exist_ok=True)

        if zip_file and zip_file.filename.endswith(".zip"):
            zip_path = os.path.join(user_submission_path, secure_filename(zip_file.filename))
            zip_file.save(zip_path)

            # Extract ZIP file
            extracted_folder = os.path.join(user_submission_path, "extracted")
            os.makedirs(extracted_folder, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extracted_folder)

            # Prepare payload for all files in the ZIP
            code_files = []
            for root, _, files in os.walk(extracted_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        code_files.append({"file_name": file, "content": f.read()})

            payload = {
                "developer_name": developer_name,
                "code_files": code_files,
                "code_type": code_type
            }
        else:
            # Save code content
            if code_content:
                with open(os.path.join(user_submission_path, "code.txt"), "w", encoding="utf-8") as f:
                    f.write(code_content)

            # Prepare payload for single file or content
            payload = {
                "developer_name": developer_name,
                "code_files": [{"content": code_content}],
                "code_type": code_type
            }

        # Send the request
        try:
            response = requests.post(ENDPOINT_URL, headers=HEADERS, json=payload)
            if response.status_code == 200:
                result = response.json()
                formatted_result = json.dumps(result, indent=4)
                save_result(developer_name, result)
                return render_template("result.html", result=formatted_result, markdown_summary=generate_markdown(result))
            else:
                error = f"Error: {response.status_code} - {response.text}"
                return render_template("result.html", error=error)
        except requests.exceptions.RequestException as e:
            error = f"Request Exception: {e}"
            return render_template("result.html", error=error)
    return render_template("submit.html", developer_name=developer_name, code_type=code_type)

# Save Result
def save_result(developer_name, result):
    """Save the result to a JSON file in the history folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = os.path.join(HISTORY_FOLDER, f"{developer_name}_{timestamp}_result.json")
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

# Generate Markdown Summary
def generate_markdown(result):
    """Generate a Markdown summary from the result."""
    summary = "# Code Analysis Summary\n\n"
    for key, value in result.items():
        summary += f"## {key}\n\n{value}\n\n"
    return summary

# Download Result
@app.route("/download/<developer_name>/<timestamp>")
def download_result(developer_name, timestamp):
    """Download the result JSON file."""
    history_file = os.path.join(HISTORY_FOLDER, f"{developer_name}_{timestamp}_result.json")
    if os.path.exists(history_file):
        return send_file(history_file, as_attachment=True)
    return "Result not found", 404

if __name__ == "__main__":
    app.run(debug=True)
