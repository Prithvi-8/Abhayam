from flask import Flask, request, jsonify
from flask_cors import CORS
import yagmail

app = Flask(__name__)
CORS(app)

# ---------------- EMAIL SETTINGS ----------------
YOUR_EMAIL = "abhayam888@gmail.com"
APP_PASSWORD = "yxwu bjkw ylsw zsvt"  # <-- paste Gmail APP password here

# Initialize email client
yag = yagmail.SMTP(YOUR_EMAIL, APP_PASSWORD)


@app.route("/send_email", methods=["POST"])
def send_email():
    try:
        data = request.json

        name = data.get("name", "Unknown")
        email = data.get("email", "No email given")
        phone = data.get("phone", "No phone given")
        message = data.get("message", "No message provided")

        email_body = f"""
📩 New message from ABHAYAM Website

Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}
"""

        yag.send(
            to=YOUR_EMAIL,
            subject="📬 New ABHAYAM Website Message",
            contents=email_body
        )

        return jsonify({"status": "success", "msg": "Email sent successfully"})

    except Exception as e:
        print("EMAIL ERROR:", e)
        return jsonify({"status": "error", "msg": str(e)})


if __name__ == "__main__":
    print("📨 Email Server running at: http://127.0.0.1:5000/send_email")
    app.run(host="0.0.0.0", port=5000)
