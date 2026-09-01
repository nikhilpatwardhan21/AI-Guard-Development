# 🛡️ AI Guard — Real-Time Computer Vision Zone Intrusion Detection System

An intelligent, real-time AI security surveillance system built with **YOLOv8**, **ByteTrack**, **OpenCV**, **FastAPI**, and **React (Vite)**.

![AI Guard Shield](https://img.shields.io/badge/AI%20Guard-v1.0.0-06b6d4?style=for-the-badge&logo=shield)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00ffff?style=for-the-badge)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)

---

## 🌟 Key Features

- 🤖 **YOLOv8 Person Detection**: Real-time human detection filtered specifically for persons.
- 🔍 **ByteTrack Multi-Object Tracking**: Assigns persistent IDs to individuals across frames to prevent duplicate alerts.
- 📐 **Interactive Polygon Zone**: Define custom restricted areas (e.g. Room Entrance, Counter, Private Area, Doorway). The system evaluates bottom-center foot position against the polygon.
- 🚨 **Intelligent Alert Dispatch**:
  - Visual breach indicator and pulsing radar banner on live feed
  - Real-time Web Audio tactical siren
  - High-resolution intrusion snapshot evidence capture
  - Background SMTP Email alerts with embedded CID screenshots
  - Configurable cooldown timers to prevent notification spam
- 🖥️ **Dark Glassmorphism Web Dashboard**: React + Vite SPA with live MJPEG stream, FPS gauge, real-time telemetry over WebSocket, evidence browser, and in-browser zone editor.
- 🛠️ **Dual Zone Configuration**: Draw and adjust zones interactively in the web browser or using the standalone OpenCV CLI tool.
- 🔄 **Zero-Lag Camera Architecture**: Dedicated producer-consumer camera capture thread with synthetic fallback test card when camera is offline.

---

## 🏗️ System Architecture

```
                                  ┌───────────────────────────┐
                                  │      Webcam / RTSP /      │
                                  │       Video Source        │
                                  └─────────────┬─────────────┘
                                                │ (Raw Frames)
                                                ▼
                                  ┌───────────────────────────┐
                                  │   CameraCapture Thread    │
                                  │     (Zero-Lag Buffer)     │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │      YOLOv8 Detector      │
                                  │   (Person Class Filter)   │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │     ByteTrack Tracker     │
                                  │  (Persistent Tracker IDs) │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │    PolygonZone Engine     │
                                  │ (Point-in-Polygon Check)  │
                                  └──────┬─────────────┬──────┘
                                         │             │
                    No Breach (Secure)   │             │   Breach Detected
                                         │             │
                                         ▼             ▼
                           ┌──────────────────┐  ┌───────────────────────────┐
                           │ Normal HUD Video │  │       Alert Manager       │
                           └─────────┬────────┘  │  - Cooldown Check         │
                                     │           │  - Screenshot Capture     │
                                     │           │  - Email Dispatch (SMTP)  │
                                     │           │  - WebSocket Broadcast    │
                                     │           └─────────────┬─────────────┘
                                     │                         │
                                     └───────────┬─────────────┘
                                                 ▼
                                   ┌───────────────────────────┐
                                   │      FastAPI Backend      │
                                   │  - /api/stream (MJPEG)    │
                                   │  - /ws/alerts (WebSocket) │
                                   │  - /api/zone (REST)       │
                                   └─────────────┬─────────────┘
                                                 │
                                                 ▼
                                   ┌───────────────────────────┐
                                   │    React + Vite Dashboard │
                                   │  (Tactical Security UI)   │
                                   └───────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\activate      # On Windows
# source .venv/bin/activate   # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run backend server
python run.py
```
> The backend server starts at `http://localhost:8000`. API Docs available at `http://localhost:8000/docs`.

---

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install node packages
npm install

# Start Vite development server
npm run dev
```
> The dashboard will open at `http://localhost:5173`.

---

## 📍 Defining the Restricted Zone

You can define and adjust the restricted zone in two ways:

### Option A: In the Web Dashboard (Recommended)
1. Open the dashboard at `http://localhost:5173`.
2. Click **"Edit Zone"** in the top navigation bar.
3. Click on the camera snapshot to place polygon vertices (or choose from presets like *Center Box*, *Lower Half*, *Left Wing*).
4. Drag points to fine-tune the boundary.
5. Click **"Apply Zone"** to instantly update the AI core.

### Option B: Using the OpenCV CLI Tool
```bash
cd backend
python tools/zone_drawer.py --source 0
```
- **Left-Click**: Add polygon point
- **Right-Click**: Undo last point
- **S**: Save zone to `data/zones/default_zone.json`
- **R**: Reset / Clear points
- **Q / ESC**: Exit

---

## ⚙️ Configuration (`.env`)

You can customize camera source, YOLO models, and email notifications in `backend/.env`:

| Variable | Default | Description |
|---|---|---|
| `CAMERA_SOURCE` | `0` | `0` for default webcam, RTSP URL (`rtsp://...`), or video file path |
| `YOLO_MODEL` | `yolov8n.pt` | `yolov8n.pt` (fastest), `yolov8s.pt`, or `yolov8m.pt` |
| `CONFIDENCE_THRESHOLD` | `0.45` | YOLO detection confidence threshold (0.10 - 0.90) |
| `ALERT_COOLDOWN_SECONDS` | `30` | Cooldown period between duplicate alerts |
| `EMAIL_ENABLED` | `false` | Set to `true` to enable SMTP email alerts |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP host server |
| `SMTP_PORT` | `587` | SMTP port |
| `SMTP_USER` | `""` | Sender email address |
| `SMTP_PASSWORD` | `""` | SMTP App Password |
| `ALERT_RECIPIENT` | `""` | Recipient email address |

---

## 📡 REST API & WebSocket Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/stream` | Real-time MJPEG video stream with bounding boxes and zone overlay |
| `GET` | `/api/snapshot` | High-res JPEG snapshot of current camera view |
| `GET` | `/api/status` | Real-time system health, FPS, and detection telemetry |
| `GET` | `/api/alerts` | Paginated intrusion alert history |
| `GET` | `/api/alerts/{id}/screenshot` | Full-resolution screenshot captured during an intrusion |
| `DELETE` | `/api/alerts` | Clear alert history |
| `GET` | `/api/zone` | Get current restricted polygon zone definition |
| `POST` | `/api/zone` | Update restricted polygon zone coordinates |
| `POST` | `/api/settings` | Update detection parameters, cooldown, and camera source |
| `POST` | `/api/test-alert` | Manually trigger a test alert |
| `WS` | `/ws/alerts` | WebSocket feed for real-time alerts and telemetry push |

---

## 🧪 Testing the Pipeline

1. Launch both Backend and Frontend.
2. Click **"Test Alert"** in the top bar to verify the alert banner, evidence thumbnail capture, audio alarm, and email dispatch.
3. Stand in front of your camera and step into the defined zone. Watch the system track your ID and trigger an instant intrusion alert!
