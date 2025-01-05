# AI-Notifications Project

**AI-Notifications** is a Flask-based web application that integrates with Firebase Firestore and the OpenAI API to deliver conversation-friendly topics for different times of the day. These topics can be triggered and sent via Pushcut notifications.

## Live Project

Visit the live project at: [AI-Notifications](https://ai-notifications.onrender.com)

---

## Features

- Dynamically generate unique topics using OpenAI's GPT-3.5/4 models.
- Store and retrieve topics from Firebase Firestore for "morning," "midday," and "afternoon" slots.
- Seamless integration with Pushcut for sending notifications with AI-generated content.
- Secure management of sensitive data using environment variables.

---

## Endpoints

### Generate Topics

- **URL**: `/generate-topics`
- **Method**: `GET`
- **Description**: Generates and stores conversation topics for "morning," "midday," and "afternoon" in Firestore.
- **Response**:
  ```json
  {
    "message": "Topics generated for all time slots"
  }
  ```

### Get Topics

- **URL**: `/get-topics/<time_slot>`
- **Method**: `GET`
- **Parameters**:
  - `<time_slot>`: The time slot to fetch topics for (`morning`, `midday`, `afternoon`).
  - `date` (optional): Query parameter to specify the date (default: today's date).
- **Example**:
  ```
  https://ai-notifications.onrender.com/get-topics/morning?date=2025-01-01
  ```
- **Response** (if topics exist):
  ```json
  {
    "topics": [
      {
        "topic": "Netflix Releases",
        "details": "Top 5 shows to watch this weekend."
      },
      {
        "topic": "AI Trends",
        "details": "The latest advancements in generative AI."
      }
    ]
  }
  ```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-notifications.git
cd ai-notifications
```

### 2. Set Up Environment

- Create a `.env` file in the project root with the following variables:
  ```plaintext
  FIREBASE_SERVICE_ACCOUNT='{"type": "service_account", "project_id": "your-project-id", ...}'
  OPENAI_API_KEY=your-openai-api-key
  ```

- Ensure `.env` is added to `.gitignore`:
  ```plaintext
  .env
  ```

### 3. Install Dependencies

Set up a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run Locally

Start the Flask app locally:

```bash
flask run
```

Visit the app at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Deployment

### Deploy to Render

1. Push your code to a GitHub repository.
2. Go to [Render](https://render.com) and create a new **Web Service**.
3. Configure Render:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Add environment variables (`FIREBASE_SERVICE_ACCOUNT` and `OPENAI_API_KEY`) in the Render dashboard.

---

## How It Works

1. **Data Flow**:
   - OpenAI generates conversation topics based on predefined prompts.
   - Topics are stored in Firebase Firestore under the `topics` collection.
   - Flask endpoints allow clients or Pushcut to retrieve data via HTTP requests.

2. **Pushcut Integration**:
   - Pushcut Webhook triggers the Flask endpoint to fetch and include topics in notifications.

---

## Technologies Used

- **Python**: Core backend logic.
- **Flask**: Web server for handling API requests.
- **Firebase Firestore**: NoSQL database for storing topics.
- **OpenAI API**: Generates AI-powered content.
- **Pushcut**: Triggers notifications with AI-generated content.

---

## Future Enhancements

- Add user authentication for personalized topics.
- Improve topic generation with user-provided context.
- Support for additional time slots or custom notifications.

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m "Add feature"`.
4. Push to the branch: `git push origin feature-name`.
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact

For questions or suggestions, contact [your-email@example.com].
