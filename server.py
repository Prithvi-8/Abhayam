from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get("question", "")
        history = data.get("history", [])

        # Build messages for LLM
        messages = [
            {
                "role": "system",
                "content": """You are Abhaya, the official assistant of Abhayam Charitable Society.

                Your permanent known details:
                    - Abhayam was found in 2012 and helped hundreds of families till today
                    - does free health care camps each year,helps via funds and other things
                    - Official Email: abhayam@gmail.com
                    - Contact Number: 9400601492
                    - GPay Number: 9400601492

                Rules:
                    - Always use these exact details when asked.
                    - Never guess or generate new contact info.
                    - Introduce yourself ONLY on the first message.
                    - Be polite, short, and helpful.
                    - Answer ONLY about Abhayam charity-related topics unless the user talks casually."""
}

        ]

        # Add previous chat turns
        for turn in history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["bot"]})

        # Add latest question
        messages.append({"role": "user", "content": user_msg})

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

        print("RAW RESPONSE --->", res_data)

        reply = res_data["choices"][0]["message"]["content"]

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Sorry, something went wrong."})



if __name__ == "__main__":
    app.run(debug=True)







