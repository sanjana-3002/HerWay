"""
HerWay Flask API
Exposes the chatbot as a REST endpoint for map integration.
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import AzureOpenAI

# Allow imports from chatbot directory
sys.path.insert(0, str(Path(__file__).parent))

from knowledge_base import build_knowledge_base, build_context
from herway import detect_neighborhoods, build_prompt_context, ask_herway, SYSTEM_PROMPT

load_dotenv(Path(__file__).parent.parent / ".env")

app = Flask(__name__)
CORS(app)

AZURE_ENDPOINT    = "https://banan-mnffxe8p-eastus2.cognitiveservices.azure.com/"
AZURE_KEY         = os.getenv("AZURE_OPENAI_KEY")
AZURE_DEPLOYMENT  = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_API_VERSION = "2025-01-01-preview"

# Load knowledge base once at startup
kb = build_knowledge_base()

# Azure client
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_KEY,
    api_version=AZURE_API_VERSION,
)

# In-memory session store: {session_id: [history turns]}
sessions: dict[str, list[dict]] = {}


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    question = (data.get("question") or "").strip()
    session_id = (data.get("session_id") or "default").strip()

    if not question:
        return jsonify({"error": "question is required"}), 400

    # Get or create session history
    history = sessions.get(session_id, [])

    # Detect neighborhoods and build context
    neighborhoods = detect_neighborhoods(question, kb)
    context = build_prompt_context(neighborhoods, kb)

    # Get answer
    try:
        answer = ask_herway(question, context, history, client)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Update rolling history (4-turn window)
    history.append({"role": "user",      "content": question})
    history.append({"role": "assistant", "content": answer})
    sessions[session_id] = history[-8:]  # 4 turns = 8 messages

    return jsonify({
        "answer": answer,
        "neighborhoods_detected": neighborhoods,
        "session_id": session_id,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "neighborhoods_loaded": len(kb)})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
