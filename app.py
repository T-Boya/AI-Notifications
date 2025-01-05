import os
import json
import atexit
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from openai import OpenAI
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
import requests

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load Firebase credentials from environment variable
service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if not service_account_json:
    raise ValueError("FIREBASE_SERVICE_ACCOUNT environment variable is not set.")
service_account_dict = json.loads(service_account_json)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(service_account_dict)
initialize_app(cred)
db = firestore.client()

# OpenAI API Key
client = OpenAI( api_key = os.getenv("OPENAI_API_KEY") )
if not client.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

PUSHCUT_WEBHOOK_URL = os.getenv("PUSHCUT_WEBHOOK_URL")
if not PUSHCUT_WEBHOOK_URL:
    raise ValueError("PUSHCUT_WEBHOOK_URL environment variable is not set.")

def generate_chatgpt_topics():
    # ChatGPT prompt to generate topics
    prompt = (
        "Generate 3 specific, conversation-friendly topics with a short explanation "
        "that someone can use on a date. Topics should be unique and engaging."
    )
    
    # OpenAI API call for chat models
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
    
    # Extract the assistant's response
    topics_text = response.choices[0].message.content
    topics = topics_text.strip().split("\n")
    
    # Format the topics into a structured list
    formatted_topics = [{"topic": t.split(":")[0], "details": t.split(":")[1].strip()} for t in topics if ":" in t]
    return formatted_topics

@app.route('/generate-topics', methods=['GET'])
def generate_topics():
    today = datetime.now().strftime("%Y-%m-%d")
    times = ["morning", "midday", "afternoon"]

    for time in times:
        topics = generate_chatgpt_topics()
        db.collection('topics').document(f"{today}-{time}").set({"topics": topics})

    return jsonify({"message": "Topics generated for all time slots"})

@app.route('/get-topics/<time>', methods=['GET'])
def get_topics(time):
    today = datetime.now().strftime("%Y-%m-%d")
    doc = db.collection('topics').document(f"{today}-{time}").get()
    if doc.exists:
        return jsonify(doc.to_dict())
    return jsonify({"message": "No topics found for this time slot"}), 404

@app.route('/send-notification/<time_slot>', methods=['GET'])
def send_pushcut_notification(time_slot):
    # Fetch data from Firestore
    today = datetime.now().strftime("%Y-%m-%d")
    doc_ref = db.collection('topics').document(f"{today}-{time_slot}")
    doc = doc_ref.get()

    if doc.exists:
        topics = doc.to_dict().get("topics", [])
        # Format the topics as plain text
        message = "\n".join([f"{i+1}. {t['topic']}: {t['details']}" for i, t in enumerate(topics)])
    else:
        message = "No topics available for this time slot."

    # Send the message to Pushcut using the webhook
    response = requests.post(
        PUSHCUT_WEBHOOK_URL,
        json={"text": message}  # The "text" field contains the notification content
    )

    if response.status_code == 200:
        return jsonify({"message": "Notification sent successfully!"})
    else:
        return jsonify({"error": "Failed to send notification", "details": response.text}), 500

# Schedule the task with APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=generate_topics, trigger="cron", hour=0)  # Run daily at midnight
scheduler.start()

# Ensure the scheduler shuts down gracefully
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True)
