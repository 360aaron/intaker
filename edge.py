from flask import Flask, request, jsonify
import requests
import json

# Lambda RIE URL
LAMBDA_URL = "http://localhost:9000/2015-03-31/functions/function/invocations"

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    content = file.read()
    file_bytes = list(content)

    # Build the same event your Lambda expects
    event = {
        "filename": file.filename,
        "file_bytes": file_bytes,
    }

    # Call the Lambda container
    resp = requests.post(
        LAMBDA_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(event),
    )

    # Lambda RIE returns the handler’s return value as JSON string
    try:
        lambda_result = resp.json()
    except Exception:
        lambda_result = {"raw": resp.text, "status": resp.status_code}

    # Add CORS so browser is happy
    response = jsonify(lambda_result)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9100, debug=True)
