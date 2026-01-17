import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)

# 🔐 Load OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=api_key)

# 😄 Friendly personality prompt
SYSTEM_PROMPT = (
    "You are a friendly, casual, tech-savvy AI assistant. "
    "Talk like a chill, supportive friend. "
    "Use simple language, light humor, and a motivating tone. "
    "You may use words like 'bro', 'yo', 'no worries', etc. "
    "Keep answers short and clear unless the user asks for detail. "
    "Do not be overly formal."
)

# 🏠 Home page
@app.route("/")
def home():
    return render_template("index.html")

# 🤖 AI endpoint
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Yo 😅 type something first!"})

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            max_output_tokens=150  # 🚀 keeps it fast
        )

        return jsonify({"reply": response.output_text})

    except Exception as e:
        # ⚠️ Prevent infinite thinking
        return jsonify({
            "reply": "Bro 😅 the server is a bit slow rn. Try again in a moment."
        })

# 🚀 Start server (Railway / Render / Fly compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
