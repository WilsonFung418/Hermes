# 🦐 Hermes Dashboard

A web-based chat interface for monitoring and chatting with your **Hermes Agent**.

Built for **Kelvin** by 🦐

---

## 🚀 Quick Start

### 1. Run it

```bash
python3 hermes_dashboard.py
```

That's it. Everything is self-contained — no web server, no PHP, no dependencies needed.

### 2. Open in browser

```
http://localhost:8081
```

**Login:** Set your credentials in the `AUTH` variable

---

## ✅ What It Does

| Feature | Description |
|---------|-------------|
| 💬 Chat UI | See conversation history with Hermes in a chat interface |
| 📤 Send Messages | Type a message and send it to Hermes — he'll reply |
| 📡 Force Report | Trigger Hermes to send the daily trading report |
| 🔄 Restart Monitor | Restart the Hermes monitoring service |
| 📋 View Logs | See recent log output from Hermes |
| 🤖 Model Info | Shows which AI model Hermes is using |

### Chat features:
- Messages automatically refresh every 15 seconds
- Platform + user badges on every message (`[WhatsApp] [Wilson Fung]`)
- Date dividers between days
- Mobile responsive

---

## ⚙️ Configuration

### Port
By default it runs on **port 8081**.  
Edit `PORT = 8081` in the file to change it.

### Authentication
Edit the `AUTH` tuple at the top of the file:
```python
AUTH = ("your_username", "your_password")
GATEWAY_HOST = "YOUR_GATEWAY_IP"  # Your gateway IP
```

### SSH / Message Sending
To enable **sending messages** from the dashboard, the script needs:

1. `sshpass` installed on the server
2. SSH access (passwordless/key) to the gateway machine running OpenClaw

Set up SSH key-based auth, or set the password via env var HERMES_SSH_PASS:
```python
SSH_HOST = "YOUR_GATEWAY_IP"
SSH_USER = "YOUR_SSH_USER"
SSH_PASS = ""  # Set password or use SSH key
HERMES_NUMBER = "YOUR_HERMES_NUMBER"
```

Update these to match your setup.

---

## 📁 Files

| File | Size | Purpose |
|------|------|---------|
| `hermes_dashboard.py` | ~22KB | Standalone server with embedded frontend |
| `README.md` | — | This file |

No other files needed.

---

## 📡 API Endpoints

All endpoints require HTTP Basic Auth (set in `AUTH` variable).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ping` | GET | Health check |
| `/api/status` | GET | Check if Hermes monitor is running |
| `/api/chat_history` | GET | Recent conversation history |
| `/api/chat_send` | GET/POST | Send a message to Hermes (`?text=xxx` or POST `body=xxx`) |
| `/api/force_send` | GET | Trigger Hermes to send report |
| `/api/restart` | GET | Restart the Hermes monitor |
| `/api/logs` | GET | View latest log output |

---

## 🐛 Troubleshooting

**Login not working?**
- Make sure you're using the correct credentials
- Check if the port is accessible from your browser

**No messages showing?**
- Hermes needs to have been active (check `agent.log` and `state.db` exist)
- The script reads from `/root/.hermes/state.db` and `/root/.hermes/logs/agent.log`

**Port already in use?**
- Change `PORT` at the top of the file

---

Built with 🦐 by Wilson's AI Assistant
