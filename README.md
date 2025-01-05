# AI-Notifications Project

**AI-Notifications** is a Flask-based web application that integrates with Firebase Firestore and the OpenAI API to deliver conversation-friendly topics for different times of the day. These topics can be triggered and sent via Pushcut notifications.

## **Live Project**
Visit the live project at: [AI-Notifications](https://ai-notifications.onrender.com)

---

## **Features**
- Dynamically generate unique topics using OpenAI's GPT-3.5/4 models.
- Store and retrieve topics from Firebase Firestore for "morning," "midday," and "afternoon" slots.
- Seamless integration with Pushcut for sending notifications with AI-generated content.
- Secure management of sensitive data using environment variables.

---

## **Endpoints**

### **Generate Topics**
- **URL**: `/generate-topics`
- **Method**: `GET`
- **Description**: Generates and stores conversation topics for "morning," "midday," and "afternoon" in Firestore.
- **Response**:
  ```json
  {
    "message": "Topics generated for all time slots"
  }
