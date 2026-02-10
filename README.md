# Homeguard AI

FastAPI backend for home automation and knowledge base with Dialogflow integration.

## 🛠️ Technologies

- **FastAPI** - Web framework
- **uvicorn** - ASGI server
- **uv** - Package manager
- **ngrok** - HTTPS tunnel for development
- **Dialogflow (GCP)**

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Run Server (locally)

```bash
uv run uvicorn main:app --reload
```

Server runs at: http://localhost:8000

### 3. Run with ngrok (for Dialogflow)

```bash
# Terminal 1: start server
uv run uvicorn main:app --reload

# Terminal 2: start ngrok
ngrok http 8000
```

## Connect to Dialogflow

1. Run ngrok manually
2. Copy the HTTPS URL from ngrok (e.g., `https://1234-abcd.ngrok-free.app`)
3. In Dialogflow Console:
   - Go to **Fulfillment** or **Webhook**
   - Enter: `https://YOUR-NGROK-URL/webhook`
   - Enable webhook for intents you want to process

## 🏠 Home Knowledge Base

Current knowledge:

- Plants: kaktus, monstera
- Bathroom: TBD
- Books: TBD
- WiFi: TBD

## Project Management

```bash
# Add dependency
uv add package-name

# Update dependencies
uv sync

# Run Python command
uv run python script.py
```
