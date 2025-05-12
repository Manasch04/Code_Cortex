from flask import Flask, request, render_template, redirect, url_for, send_file
import requests
import json
import os
import base64
import zipfile
from werkzeug.utils import secure_filename
from datetime import datetime
import chardet
from flask import make_response
import io
from weasyprint import HTML

# API Key and Endpoint
API_KEY = "9Smwva6WhhjOM1V44YKnGTWO53RwSHZVpp82TYGXeAyQJDWwM100JQQJ99BDAAAAAAAAAAAAINFRAZML15eq"
ENDPOINT_URL = "https://codecortex2.eastus.inference.ml.azure.com/score"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

UPLOAD_FOLDER = "uploads"
HISTORY_FOLDER = "history"
USER_SUBMISSIONS_FOLDER = "user_submissions"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)
os.makedirs(USER_SUBMISSIONS_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder="frontend")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

SUPPORTED_EXTENSIONS = (
    ".py", ".cs", ".java", ".js", ".ts",
    ".html", ".css", ".json", ".xml", ".yaml", ".yml",
    ".txt", ".md", ".csv",
    ".c", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php", ".swift",
    ".ini", ".toml", ".cfg"
)

MAX_TOTAL_CHARACTERS = 7500  # Safe limit under Azure 8000 limit

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/input", methods=["GET", "POST"])
def user_input():
    if request.method == "POST":
        developer_name = request.form.get("developer_name")
        code_type = request.form.get("code_type")
        return redirect(url_for("submit_code", developer_name=developer_name, code_type=code_type))
    return render_template("input.html")

@app.route("/submit", methods=["GET", "POST"])
def submit_code():
    developer_name = request.args.get("developer_name")
    code_type = request.args.get("code_type")

    if request.method == "POST":
        code_content = request.form.get("code_content")
        zip_file = request.files.get("zip_file")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_submission_path = os.path.join(USER_SUBMISSIONS_FOLDER, f"{developer_name}_{timestamp}")
        os.makedirs(user_submission_path, exist_ok=True)

        payload = {"developer_name": developer_name, "project_type": code_type, "code_files": []}
        total_characters = 0
        skipped_files = []

        if zip_file and zip_file.filename.endswith(".zip"):
            zip_path = os.path.join(user_submission_path, secure_filename(zip_file.filename))
            zip_file.save(zip_path)

            extracted_folder = os.path.join(user_submission_path, "extracted")
            os.makedirs(extracted_folder, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extracted_folder)

            for root, _, files in os.walk(extracted_folder):
                for file in files:
                    file_path = os.path.join(root, file)

                    if not file.endswith(SUPPORTED_EXTENSIONS):
                        skipped_files.append(file)
                        continue

                    try:
                        with open(file_path, "rb") as f:
                            raw_data = f.read()
                            result = chardet.detect(raw_data)
                            encoding = result["encoding"] if result["encoding"] else "utf-8"

                        with open(file_path, "r", encoding=encoding) as f:
                            content = f.read()

                        if total_characters + len(content) > MAX_TOTAL_CHARACTERS:
                            skipped_files.append(file)
                            continue

                        payload["code_files"].append({"file_name": file, "content": content})
                        total_characters += len(content)

                    except Exception:
                        skipped_files.append(file)

        elif code_content:
            if len(code_content) <= MAX_TOTAL_CHARACTERS:
                code_file_path = os.path.join(user_submission_path, "pasted_code.txt")
                with open(code_file_path, "w", encoding="utf-8") as f:
                    f.write(code_content)
                payload["code_files"].append({"file_name": "pasted_code.txt", "content": code_content})
            else:
                return render_template("result.html", error="Your pasted code exceeds the allowed character limit.")

        try:
            response = requests.post(ENDPOINT_URL, headers=HEADERS, json=payload)
            if response.status_code == 200:
                result = response.json()
                markdown_summary = result.get('answer', '')

                save_result(developer_name, result, timestamp)

                return render_template(
                    "result.html",
                    developer_name=developer_name,
                    timestamp=timestamp,
                    result=result,
                    markdown_summary=markdown_summary,
                    skipped_files=skipped_files
                )
            else:
                error = f"Error: {response.status_code} - {response.text}"
                return render_template("result.html", error=error)

        except requests.exceptions.RequestException as e:
            error = f"Request Exception: {e}"
            return render_template("result.html", error=error)

    return render_template("submit.html", developer_name=developer_name, code_type=code_type)

def save_result(developer_name, result, timestamp):
    history_file = os.path.join(HISTORY_FOLDER, f"{developer_name}_{timestamp}_result.json")
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

@app.route("/download/<developer_name>/<timestamp>")
def download_result(developer_name, timestamp):
    history_file = os.path.join(HISTORY_FOLDER, f"{developer_name}_{timestamp}_result.json")
    if os.path.exists(history_file):
        return send_file(history_file, as_attachment=True)
    return "Result not found", 404

@app.route('/download_pdf')
@app.route('/download_pdf')
def download_pdf():
    developer_name = request.args.get('developer_name')
    timestamp = request.args.get('timestamp')
    history_file = os.path.join(HISTORY_FOLDER, f"{developer_name}_{timestamp}_result.json")  # <-- fix here
    if not os.path.exists(history_file):
        return "No report found.", 404
    with open(history_file, 'r', encoding='utf-8') as f:
        result = json.load(f)
    markdown_summary = result.get('answer', '')
    json_report = json.dumps(result, indent=4, ensure_ascii=False)
    skipped_files = result.get('skipped_files', [])
    skipped_html = ''
    if skipped_files:
        skipped_html = (
            f'''<div style="background:#fff3cd;border:1px solid #ffeeba;padding:16px;border-radius:8px;margin-bottom:24px;">
                <b>Skipped Files (due to size or unsupported type):</b><ul style="margin:8px 0 0 18px;">
                {''.join(f'<li>{fname}</li>' for fname in skipped_files)}
            </ul></div>'''
        )
    html_content = f'''
    <html><head><style>
    body {{ font-family: Arial, sans-serif; margin: 40px; }}
    h1 {{ color: #00d4ff; text-align: center; }}
    .summary {{ background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 24px; }}
    .json-block {{ background: #222; color: #fff; padding: 10px; border-radius: 6px; font-size: 11px; overflow-x: auto; white-space: pre; max-height: none; }}
    </style></head><body>
    <h1>CODECORTEX Report</h1>
    {skipped_html}
    <h2>Markdown Summary</h2>
    <div class="summary">{markdown_summary}</div>
    <h2>JSON Report</h2>
    <pre class="json-block">{json_report}</pre>
    </body></html>
    '''
    pdf = HTML(string=html_content).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=codecortex_report_{developer_name}_{timestamp}.pdf'
    return response

if __name__ == "__main__":
    app.run(debug=True)
