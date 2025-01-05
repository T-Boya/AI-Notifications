import os
import json
import atexit
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from openai import OpenAI
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load Firebase credentials from environment variable
service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if not service_account_json:
    raise ValueError("FIREBASE_SERVICE_ACCOUNT environment variable is not set.")
print(service_account_json)
service_account_dict = json.loads(service_account_json)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(service_account_dict)
initialize_app(cred)
db = firestore.client()

# OpenAI API Key
client = OpenAI( api_key = os.getenv("OPENAI_API_KEY") )
if not client.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

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

# Schedule the task with APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=generate_topics, trigger="cron", hour=0)  # Run daily at midnight
scheduler.start()

# Ensure the scheduler shuts down gracefully
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True)
