import os
import json
import atexit
from prompt import prompt
from flask import Flask, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from openai import OpenAI
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
from pytz import timezone
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

# Define the time zone
eastern = timezone('America/New_York')

def generate_chatgpt_topics():
    # ChatGPT prompt to generate topics
    
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
    print(response)
    
    # Extract the assistant's response
    topics_text = response.choices[0].message.content
    topics = topics_text.strip().split("\n")
    
    # Format the topics into a structured list
    formatted_topics = [{"topic": t.split(":")[0], "details": t.split(":")[1].strip()} for t in topics if ":" in t]
    return formatted_topics

@app.route('/generate-topics', methods=['GET'])
def generate_topics():
    today = datetime.now(eastern).strftime("%Y-%m-%d")
    times = ["morning", "midday", "afternoon"]

    for time in times:
        topics = generate_chatgpt_topics()
        db.collection('topics').document(f"{today}-{time}").set({"topics": topics})

    return jsonify({"message": "Topics generated for all time slots"})

def get_time_slot():
    current_hour = datetime.now(eastern).hour
    if 5 <= current_hour < 12:
        return "morning"
    elif 12 <= current_hour < 17:
        return "midday"
    else:
        return "afternoon"

def get_most_recent_topics():
     # Determine the time slot
    time_slot = get_time_slot()

    # Get today's date
    today = datetime.now(eastern).strftime("%Y-%m-%d")

    # Construct the Firestore document ID
    doc_id = f"{today}-{time_slot}"

    # Fetch the document from Firestore
    doc_ref = db.collection('topics').document(doc_id)
    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()  # Return the document's data
    return None  # No data found for the current time slot

@app.route('/send-notification', methods=['GET'])
def send_pushcut_notification():
    # Fetch data from Firestore
    recent_doc = get_most_recent_topics()

    if recent_doc:
        topics = recent_doc.get("topics", [])
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

@app.route('/view-topics', methods=['GET'])
def view_topics():
    recent_doc = get_most_recent_topics()

    if recent_doc:
        return render_template(
            'topics.html',
            topics=recent_doc.get("topics", []),
            date=recent_doc.get("date", "Unknown"),
            error=None
        )
    else:
        return render_template(
            'topics.html',
            topics=None,
            date="No recent topics found",
            error="No topics available."
        )

# Schedule the task with APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=generate_topics, trigger="cron", hour=0, timezone=eastern)  # Run daily at midnight
scheduler.add_job(func=send_pushcut_notification, trigger="cron", hour=8, timezone=eastern)  # Runs at 8 AM daily
scheduler.add_job(func=send_pushcut_notification, trigger="cron", hour=12, timezone=eastern)  # Runs at 12 PM daily
scheduler.add_job(func=send_pushcut_notification, trigger="cron", hour=16, timezone=eastern)  # Runs at 4 PM daily
scheduler.start()

# Ensure the scheduler shuts down gracefully
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True)
