# Event-Driven Backend — FastAPI + Firebase Cloud Functions (Intern PoC)

This project implements a complete event-driven backend system using FastAPI, Firebase Authentication, Firestore, and Firebase Cloud Functions, fully integrated with Firebase Emulators for local development. It provides a secure and scalable architecture where users can register or log in via Firebase Auth, create events through protected FastAPI endpoints, and automatically trigger Firebase Cloud Functions to handle background processes such as analytics tracking and notification generation. The backend is designed around an event-driven model — whenever an event is created in Firestore, Cloud Functions respond instantly to update analytics or schedule notifications, ensuring a decoupled and asynchronous workflow. Additionally, the system supports real-time WebSocket updates, allowing connected clients to receive immediate event creation alerts. This project demonstrates how modern backend systems can combine serverless design, real-time communication, and asynchronous automation to create an efficient, scalable, and developer-friendly API ecosystem.

---

## Features

| Category | Description | Status |
|-----------|--------------|--------|
| Authentication | Firebase Auth (JWT ID tokens) used for protected endpoints |  Done |
| Event API | POST /events/ (Create) and GET /events/ (List user events) |  Done |
| Event-driven Cloud Function | onEventCreate trigger updates analytics automatically |  Done |
| Analytics Endpoint | /analytics/me returns total events per user |  Done |
| Scheduled Notifications | nightlySummary and manual HTTP function runNotificationJobNow |  Done |
| WebSocket Updates | Real-time event notifications to connected clients |  Done |

---

##  Architecture

```
FastAPI → Firestore (Emulator)
   |             ↑
   |             └── Cloud Functions (onEventCreate, runNotificationJobNow)
   |
   └── Firebase Auth (Emulator)
```

### Data Flow:
1. User authenticates via Firebase Auth (ID token).  
2. Authenticated user hits FastAPI /events/ endpoint.  
3. Event stored in Firestore → triggers Cloud Function.  
4. Cloud Function updates analytics and notification data.  
5. WebSocket pushes a live update to connected clients.

---

##  Setup & Installation

### 1️. System Requirements

| Tool | Version |
|------|----------|
| Node.js | ≥ 18.x |
| npm | ≥ 8.x |
| Python | ≥ 3.11 |
| Firebase CLI | ≥ 12.x |
| Java JDK | ≥ 11 (⚠️ JDK 21+ recommended for Firebase CLI 15+) |

---


### 2. Clone the repository
```
git clone https://github.com/Samridhi260/Event-Backend.git
```

---

### 3️. Create & Activate Virtual Environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

---

### 4️. Install Python Dependencies

```bash
pip install fastapi "uvicorn[standard]" google-cloud-firestore google-auth
# Or use pip install -r requirements.txt
```

---

### 5️. Install Firebase Dependencies (for Cloud Functions)

```bash
cd functions
npm ci
cd ..
```

---

##  Firebase Emulator Setup

### 1️. Start Firebase Emulators

```bash
firebase emulators:start
```

This runs:
- Auth Emulator: localhost:9099  
- Firestore Emulator: localhost:8080  
- Functions Emulator: localhost:5001  
- Emulator UI: http://localhost:4000  

### 2️. Verify in Emulator UI

Open [http://localhost:4000](http://localhost:4000)  
You should see Firestore, Auth, and Functions panels active.

---

##  Run FastAPI Backend

### 1️. Open a new PowerShell window

Activate the virtual environment:

```bash
cd C:\Users\<YourName>\Desktop\Samridhi_event
.\.venv\Scripts\Activate.ps1
```

### 2️. Set Emulator Environment Variables

```bash
$env:GCLOUD_PROJECT = "event1234-701af"
$env:GOOGLE_CLOUD_PROJECT = $env:GCLOUD_PROJECT
$env:FIRESTORE_EMULATOR_HOST = "localhost:8080"
$env:FIREBASE_AUTH_EMULATOR_HOST = "localhost:9099"
Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS -ErrorAction SilentlyContinue
```

### 3️. Start FastAPI

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

---

##  Authentication — Get ID Token

To test endpoints, you need a Firebase ID token.

1. Create a test user via your helper script:
2. ```bash
   python tools/create_user_and_get_id_token.py
   ```
3. Copy the printed `"idToken"` value.

---

##  Testing & Verification

### Swagger UI

Open: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

1. Click **Authorize** (top-right).  
2. Paste your Firebase ID token → click **Authorize**.  
3. Test endpoints:
   - **POST /events/** → creates event in Firestore.  
   - **GET /events/** → lists your events.  
   - **GET /analytics/me** → shows `{ "totalEvents": N }`.

---

##  API Summary

| Endpoint | Method | Auth Required | Description |
|-----------|---------|---------------|--------------|
| /events/ | POST |  Yes | Create an event |
| /events/ | GET |  Yes | List user’s events |
| /analytics/me | GET |  Yes | Returns total events per user |
| /ws | WebSocket | No | Live updates on event creation |

---

##  Cloud Functions Summary

| Function | Type | Trigger | Description |
|-----------|------|----------|-------------|
| onEventCreate | Firestore Trigger | onCreate(events/{eventId}) | Increments user analytics |
| nightlySummary | Scheduled | Every 24h | Generates upcoming event notifications |
| runNotificationJobNow | HTTP | Manual | Triggers notification job manually for testing |

Test manually (in browser or Postman):  
[http://localhost:5001/event1234-701af/us-central1/runNotificationJobNow](http://localhost:5001/event1234-701af/us-central1/runNotificationJobNow)

Expected Response:
```json
{"ok": true, "generated": 1}
```

---

##  WebSocket Real-Time Updates

Connect via browser console:

1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Press **F12 → Console**, paste:
   ```js
   const ws = new WebSocket("ws://127.0.0.1:8000/ws");
   ws.onopen = () => console.log("WS connected");
   ws.onmessage = e => console.log("WS message:", e.data);
   ```
3. Now create a new event in Swagger.
4. Console shows:
   ```
   WS connected
   WS message: {"type":"event_created","id":"...","title":"...","created_at":"..."}
   ```

---

##  Postman Collection

### 1️. Variables

| Variable | Example Value |
|-----------|----------------|
| base_url | http://127.0.0.1:8000 |
| id_token | (paste your Firebase ID token) |

### 2️. Authorization

- **Type:** Bearer Token  
- **Token:** `{{id_token}}`

### 3️. Requests

| Name | Method | URL | Description |
|------|---------|-----|-------------|
| POST Create Event | POST | {{base_url}}/events/ | Create event |
| GET List Events | GET | {{base_url}}/events/ | List events |
| GET My Analytics | GET | {{base_url}}/analytics/me | Analytics per user |
| GET Run Notification Job Now | GET | http://localhost:5001/event1234-701af/us-central1/runNotificationJobNow | Trigger notifications manually |

##  Deliverable (Postman)  

Postman/Event API (Local).postman_collection.json

##  Author

*Samridhi*    
samridhi10043@gmail.com

### Summary

- **1.** This project is an event-driven backend built using FastAPI and Firebase.
- **2.** Users can register or log in with Firebase Authentication.
- **3.** Authenticated users can create and view events through protected API endpoints.
- **4.** Each new event automatically triggers Firebase Cloud Functions to update analytics and send notifications.
- **5.** The system includes real-time updates via WebSockets for instant event alerts.
- **6.** It runs entirely on Firebase Emulators, making setup, testing, and debugging simple and safe.
- **7.** The project demonstrates how to build a scalable, automated, and real-time backend system using modern tools and event-driven design.



