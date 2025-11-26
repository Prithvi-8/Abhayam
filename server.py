# ---------------------- IMPORTS ----------------------
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import yagmail
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------- FLASK APP ----------------------
app = Flask(__name__)
CORS(app)

# ---------------------- LLM CONFIG ----------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------------- EMAIL CONFIG ----------------------
YOUR_EMAIL = os.getenv("MAIL_USER")          # from .env
APP_PASSWORD = os.getenv("MAIL_APP_PASSWORD") # from .env

# email client
yag = yagmail.SMTP(YOUR_EMAIL, APP_PASSWORD)


# ======================================================
#                  🤖 CHATBOT ENDPOINT
# ======================================================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get("question", "")
        history = data.get("history", [])

        messages = [
            {
                "role": "system",
                "content": """
You are Abhaya, official assistant of Abhayam Charitable Society.

KNOWN FACTS:
- Abhayam was founded in 2012.
- Conducts free healthcare camps.
- Helps families through funds and services.
- Official Email: abhayam@gmail.com
- Contact Number: 9400601492
- GPay Number: 9400601492

RULES:
- Use only the above details.
- Introduce yourself ONLY on the first message.
- Keep replies short, polite, warm.
"""
            }
        ]

        # add history to memory
        for turn in history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["bot"]})

        # new message
        messages.append({"role": "user", "content": user_msg})

        # Groq API
        url = "https://api.groq.com/openai/v1/chat/completions"

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()

        print("RAW RESPONSE:", res_data)

        reply = res_data["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({"reply": "Something went wrong."})


# ======================================================
#                  📩 EMAIL ENDPOINT
# ======================================================
@app.route("/send_email", methods=["POST"])
def send_email():
    try:
        data = request.json

        name = data.get("name", "Unknown")
        email = data.get("email", "No Email")
        phone = data.get("phone", "No Phone")
        message = data.get("message", "")

        body = f"""
📩 New ABHAYAM Website Message

Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}
"""

        yag.send(
            to=YOUR_EMAIL,
            subject="📬 New ABHAYAM Website Enquiry",
            contents=body
        )

        return jsonify({"status": "success", "msg": "Email sent"})

    except Exception as e:
        print("EMAIL ERROR:", e)
        return jsonify({"status": "error", "msg": str(e)})


# ======================================================
#                    RUN SERVER
# ======================================================
if __name__ == "__main__":
    print("🚀 Running Abhayam backend on port 5000")
    app.run(host="0.0.0.0", port=5000)
