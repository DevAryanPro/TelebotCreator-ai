from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Cache the system prompt in memory so we fetch it only once
SYSTEM_PROMPT = None
SYSTEM_URL = "https://raw.githubusercontent.com/DevAryanPro/docs/refs/heads/main/tbc.md"
WORKER_BASE = "https://kimi.hello-kaiiddo.workers.dev/"

def load_system_prompt():
    global SYSTEM_PROMPT
    if SYSTEM_PROMPT is None:
        try:
            SYSTEM_PROMPT = requests.get(SYSTEM_URL, timeout=30).text
        except Exception as e:
            SYSTEM_PROMPT = f"⚠️ Could not load system prompt: {e}"
    return SYSTEM_PROMPT

@app.route("/ask", methods=["GET"])
def ask():
    content = request.args.get("content", "").strip()
    if not content:
        return jsonify({"error": "Missing 'content' query param"}), 400

    load_system_prompt()

    final_url = f"{WORKER_BASE}?content={requests.utils.quote(content)}"
    try:
        resp = requests.get(final_url, timeout=10)
        resp.raise_for_status()
        answer = resp.text
    except Exception as e:
        answer = f"Worker error: {e}"

    return jsonify({
        "system_prompt": SYSTEM_PROMPT,
        "user_query": content,
        "answer": answer
    })

# Vercel uses WSGI entry-point "app"
# No __main__ guard needed
