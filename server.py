# ---------------------- IMPORTS ----------------------
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------- FLASK APP ----------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# ---------------------- LLM CONFIG ----------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------------- EMAIL CONFIG ----------------------
# ---------------------- EMAIL CONFIG (BREVO API) ----------------------

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")



# email client



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
- Official Email: abhayam888@gmail.com
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

        name = data.get("name", "")
        email = data.get("email", "")
        phone = data.get("phone", "")
        message = data.get("message", "")

        payload = {
            "sender": {"name": "ABHAYAM Website", "email": RECEIVER_EMAIL},
            "to": [{"email": RECEIVER_EMAIL}],
            "subject": "💌 New Message from ABHAYAM Website",
            "htmlContent": f"""
                <h2>New Website Enquiry</h2>
                <p><b>Name:</b> {name}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Phone:</b> {phone}</p>
                <p><b>Message:</b><br>{message}</p>
            """
        }

        res = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={
                "api-key": BREVO_API_KEY,
                "Content-Type": "application/json"
            }
        )

        if res.status_code == 201:
            return jsonify({"status": "success", "msg": "Email sent"})
        else:
            return jsonify({"status": "error", "msg": res.text})

    except Exception as e:
        print("EMAIL ERROR:", e)
        return jsonify({"status": "error", "msg": str(e)})




# ======================================================
#                    RUN SERVER
# ======================================================
if __name__ == "__main__":
    print("🚀 Running Abhayam backend on port 5000")
    app.run(host="0.0.0.0", port=5000)
