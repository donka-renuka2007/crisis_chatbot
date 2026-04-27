from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
print("KEY:", GROQ_API_KEY)

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are CARA (Crisis Assistance & Response Assistant), an expert AI crisis management chatbot.
Your role is to:
- Provide calm, clear, and actionable guidance during emergencies and crises
- Help users with natural disasters (floods, earthquakes, cyclones, wildfires)
- Guide users through medical emergencies, fire evacuations, and chemical incidents
- Offer mental health support and crisis counseling advice
- Share emergency contact numbers relevant to India (112, 100, 101, 108, 1070)
- Provide step-by-step safety protocols and checklists
- Help with disaster preparedness and prevention

Tone guidelines:
- Always stay calm, reassuring, and professional
- Be concise but thorough — people in crisis need clear instructions
- Use numbered steps for action items
- Prioritize life safety above all else
- If situation is life-threatening, always advise calling 112 first
- Use empathetic language; acknowledge the stress of the situation

Format your responses clearly with:
- Bold key actions using **text**
- Numbered lists for step-by-step instructions
- Relevant emergency numbers when appropriate
- Short paragraphs for readability

You are NOT a replacement for emergency services. Always encourage users to contact official emergency responders when lives are at risk."""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    conversation_history = data.get("history", [])

    if not user_message:
        return jsonify({"response": "Please enter a message.", "status": "error"})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for entry in conversation_history[-10:]:
        messages.append({"role": entry["role"], "content": entry["content"]})

    messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024,
            temperature=0.5,
            stream=False,
        )
        bot_reply = completion.choices[0].message.content
        return jsonify({"response": bot_reply, "status": "ok"})

    except Exception as e:
        print(f"Groq API Error: {type(e).__name__}: {e}")
        return jsonify({
            "response": f"Error: {type(e).__name__}: {str(e)}",
            "status": "error"
        })


@app.route("/emergency-contacts", methods=["GET"])
def emergency_contacts():
    return jsonify({
        "Police": "100",
        "Fire": "101",
        "Ambulance": "108",
        "Disaster Helpline": "1070",
        "Women Helpline": "1091",
        "Child Helpline": "1098",
        "General Emergency": "112"
    })


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)