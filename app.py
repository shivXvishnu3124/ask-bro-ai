import os
import time
import requests
from flask import Flask, request, jsonify, render_template, session

# ---------- OpenAI ----------
from openai import OpenAI

# ---------- Google Gemini ----------
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "ask-bro-secret")

# =========================
# 🔐 Load API Keys
# =========================
OPENAI_API_KEY = os.getenv("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")
GOOGLE_API_KEY = os.getenv("AIzaSyCuZDCq2Z2SSDAT3mb5uNYJiaaWarTn1Es")
DEEPSEEK_API_KEY = os.getenv("sk-401fbd42cf00493b8c28db07f3027460")
GROK_API_KEY = os.getenv("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")

if not any([OPENAI_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY, GROK_API_KEY]):
    raise RuntimeError("No AI API keys found")

# =========================
# 🤖 Initialize Clients
# =========================
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

gemini_model = None
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# 😄 Personality Prompt
# =========================
SYSTEM_PROMPT = (
    "You are a friendly, casual, tech-savvy AI assistant. "
    "Talk like a chill, supportive friend. "
    "Use simple language, light humor, and a motivating tone. "
    "Say things like 'bro', 'yo', 'no worries'. "
    "Keep answers short unless asked for detail."
)

# =========================
# ⏱️ Cooldown Config
# =========================
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
    last_time = session.get("last_request_time", 0)

    # ---------- Cooldown Guard ----------
    if now - last_time < COOLDOWN_SECONDS:
        return jsonify({
            "reply": f"Bro 😅 slow down! Try again in {int(COOLDOWN_SECONDS - (now - last_time))}s.",
            "source": "Cooldown Guard"
        })

    session["last_request_time"] = now

    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({
            "reply": "Yo 😅 type something first!",
            "source": "System"
        })

    # ---------- Chat Memory ----------
    history = session.get("chat_history", [])
    history.append({"role": "user", "content": user_input})
    history = history[-MAX_HISTORY:]
    session["chat_history"] = history

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    # ---------- 1️⃣ OpenAI (GPT-4o) ----------
    if openai_client:
        try:
            response = openai_client.responses.create(
                model="gpt-4o",
                input=messages,
                max_output_tokens=150
            )
            reply = response.output_text
            history.append({"role": "assistant", "content": reply})
            session["chat_history"] = history[-MAX_HISTORY:]

            return jsonify({
                "reply": reply,
                "source": "OpenAI (GPT-4o)"
            })
        except Exception as e:
            print("⚠️ OpenAI failed:", e)

    # ---------- 2️⃣ Google Gemini ----------
    if gemini_model:
        try:
            prompt = SYSTEM_PROMPT + "\n"
            for msg in history:
                prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
            prompt += "AI:"

            response = gemini_model.generate_content(prompt)
            reply = response.text

            history.append({"role": "assistant", "content": reply})
            session["chat_history"] = history[-MAX_HISTORY:]

            return jsonify({
                "reply": reply,
                "source": "Google Gemini"
            })
        except Exception as e:
            print("⚠️ Gemini failed:", e)

    # ---------- 3️⃣ DeepSeek ----------
    if DEEPSEEK_API_KEY:
        try:
            r = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "max_tokens": 150
                },
                timeout=20
            )
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"]

            history.append({"role": "assistant", "content": reply})
            session["chat_history"] = history[-MAX_HISTORY:]

            return jsonify({
                "reply": reply,
                "source": "DeepSeek"
            })
        except Exception as e:
            print("⚠️ DeepSeek failed:", e)

    # ---------- 4️⃣ Grok (xAI) ----------
    if GROK_API_KEY:
        try:
            r = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-2",
                    "messages": messages,
                    "max_tokens": 150
                },
                timeout=20
            )
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"]

            history.append({"role": "assistant", "content": reply})
            session["chat_history"] = history[-MAX_HISTORY:]

            return jsonify({
                "reply": reply,
                "source": "Grok (xAI)"
            })
        except Exception as e:
            print("⚠️ Grok failed:", e)

    # ---------- All failed ----------
    return jsonify({
        "reply": "Bro 😅 all AI servers are busy right now. Try again later.",
        "source": "System"
    })

# =========================
# 🚀 Start Server (Railway)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
