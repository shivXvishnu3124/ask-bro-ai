import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)

# 🔐 API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 😄 Friendly personality
SYSTEM_PROMPT = (
    "You are a friendly, casual, tech-savvy AI assistant. "
    "Talk like a chill, supportive friend. "
    "Use simple language, light humor, and a motivating tone. "
    "You may use words like 'bro', 'yo', 'no worries', etc. "
    "Keep answers concise unless the user asks for detail. "
    "Do not be overly formal."
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message", "")

    if not user_input:
        return jsonify({"reply": "Yo 😅 you gotta type something first!"})

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        max_output_tokens=150
    )

    return jsonify({"reply": response.output_text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
