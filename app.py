import os
import time
import requests
from flask import Flask, request, jsonify, render_template, session
from openai import OpenAI
from google import genai   # ✅ NEW Gemini SDK

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "ask-bro-secret")

# =========================
# 🔐 Load API Keys (CORRECT)
# =========================
OPENAI_API_KEY = os.getenv("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
")
GOOGLE_API_KEY = os.getenv("AIzaSyCuZDCq2Z2SSDAT3mb5uNYJiaaWarTn1Es")
DEEPSEEK_API_KEY = os.getenv("sk-401fbd42cf00493b8c28db07f3027460")
GROK_API_KEY = os.getenv("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")

# =========================
# 🤖 Init Clients (SAFE)
# =========================
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
gemini_client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

# =========================
# 😄 Personality Prompt
# =========================
SYSTEM_PROMPT = (
    "You are a friendly, casual, tech-savvy AI assistant. "
    "Talk like a chill, supportive friend. "
    "Use simple language, light humor, and motivation. "
    "Say things like 'bro', 'yo', 'no worries'."
)

COOLDOWN_SECONDS = 8
MAX_HISTORY = 10

# =========================
# 🏠 Home
# =========================
@app.route("/")
def home():
    session.setdefault("chat_history", [])
    session.setdefault("last_request_time", 0)
    return render_template("index.html")

# =========================
# 🤖 Ask Endpoint
# =========================
@app.route("/ask", methods=["POST"])
def ask():
    now = time.time()
    if now - session.get("last_request_time", 0) < COOLDOWN_SECONDS:
        return jsonify({
            "reply": "Bro 😅 chill for a few seconds.",
            "source": "Cooldown"
        })

    session["last_request_time"] = now
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Yo 😅 type something first!"})

    history = session.get("chat_history", [])
    history.append({"role": "user", "content": user_input})
    history = history[-MAX_HISTORY:]
    session["chat_history"] = history

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    # ---------- OpenAI (GPT-4o) ----------
    if openai_client:
        try:
            r = openai_client.responses.create(
                model="gpt-4o",
                input=messages,
                max_output_tokens=150
            )
            reply = r.output_text
            history.append({"role": "assistant", "content": reply})
            session["chat_history"] = history[-MAX_HISTORY:]
            return jsonify({"reply": reply, "source": "OpenAI (GPT-4o)"})
        except Exception as e:
            print("OpenAI failed:", e)

    # ---------- Gemini ----------
    if gemini_client:
        try:
            prompt = SYSTEM_PROMPT + "\n"
            for m in history:
                prompt += f"{m['role']}: {m['content']}\n"
            reply = gemini_client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            ).text
            history.append({"role": "assistant", "content": reply})
            session["chat_history"] = history[-MAX_HISTORY:]
            return jsonify({"reply": reply, "source": "Google Gemini"})
        except Exception as e:
            print("Gemini failed:", e)

    # ---------- DeepSeek ----------
    if DEEPSEEK_API_KEY:
        try:
            r = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                json={"model": "deepseek-chat", "messages": messages, "max_tokens": 150},
                timeout=15
            )
            reply = r.json()["choices"][0]["message"]["content"]
            return jsonify({"reply": reply, "source": "DeepSeek"})
        except Exception as e:
            print("DeepSeek failed:", e)

    # ---------- Grok ----------
    if GROK_API_KEY:
        try:
            r = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROK_API_KEY}"},
                json={"model": "grok-2", "messages": messages, "max_tokens": 150},
                timeout=15
            )
            reply = r.json()["choices"][0]["message"]["content"]
            return jsonify({"reply": reply, "source": "Grok"})
        except Exception as e:
            print("Grok failed:", e)

    return jsonify({
        "reply": "Bro 😅 all AI servers are busy.",
        "source": "System"
    })

# =========================
# 🚀 Start Server (Railway)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
