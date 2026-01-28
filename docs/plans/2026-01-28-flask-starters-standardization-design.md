# Flask Starters Standardization Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to create detailed implementation plan, then superpowers:subagent-driven-development to execute.

**Date:** 2026-01-28

**Goal:** Standardize all Flask starters to match the Node.js starter pattern established during recent standardization work.

**Repositories Affected:**
- flask-text-to-speech (REST API)
- flask-transcription (REST API)
- flask-live-text-to-speech (WebSocket)
- flask-live-transcription (WebSocket)

**Excluded:** flask-voice-agent (already standardized)

---

## 1. Repository Structure & Submodule Strategy

**Replace frontend folders with git submodules:**

All 4 Flask starters will replace their current `frontend/` directory with a git submodule pointing to the corresponding `*-html` repository.

**Submodule mappings:**
- flask-text-to-speech → text-to-speech-html
- flask-transcription → transcription-html
- flask-live-text-to-speech → live-text-to-speech-html
- flask-live-transcription → live-transcription-html

**Implementation steps per repo:**
1. Git track existing frontend files (in case we need rollback)
2. Remove frontend folder from git: `git rm -r frontend`
3. Add git submodule: `git submodule add https://github.com/deepgram-starters/[feature]-html frontend`
4. Commit submodule addition
5. Update .gitmodules to track the submodule

**Benefits:**
- Single source of truth for each frontend
- Frontend updates automatically available to all language implementations
- Consistent user experience across Node.js and Python
- Matches flask-voice-agent pattern

---

## 2. File Organization & Configuration

### Community Files
**Move to .github/ folder (like Node starters):**
- CODE_OF_CONDUCT.md → .github/CODE_OF_CONDUCT.md
- CONTRIBUTING.md → .github/CONTRIBUTING.md
- SECURITY.md → .github/SECURITY.md
- Keep README.md and LICENSE in root

### Makefile Addition
Create standardized Makefile with these targets:

```makefile
.PHONY: help init dev build start update clean status

help:              # Show all available commands
init:              # Initialize submodules and install dependencies (Python venv + frontend)
dev:               # Start development servers (Flask + Vite HMR)
build:             # Build frontend for production
start:             # Start production server
update:            # Update submodules to latest
clean:             # Remove venv, node_modules, build artifacts
status:            # Show git and submodule status
```

**Implementation details:**
- `init`: Create venv, install requirements.txt, cd frontend && pnpm install
- `dev`: Set NODE_ENV=development, run Flask with Vite proxy
- `build`: cd frontend && pnpm build
- `start`: Set NODE_ENV=production, run Flask serving frontend/dist
- `update`: git submodule update --remote --merge
- `clean`: Remove venv/, frontend/node_modules/, frontend/dist/

### deepgram.toml Standardization
**Ensure consistent structure:**
```toml
[meta]
title = "Flask [Feature]"
description = "..."
author = "Deepgram DX Team <devrel@deepgram.com> (https://developers.deepgram.com)"
useCase = "[Use Case]"
language = "Python"
framework = "Flask"
repository = "https://github.com/deepgram-starters/flask-[feature]"

[pre-build]
command = "make init"
message = "Dependencies installed (Python + frontend)"

[build]
command = "make build"
message = "Build completed"

[build.config]
sample = "sample.env"
output = ".env"

[post-build]
message = "Run `make start` to get up and running."
```

**Key fixes:**
- Use `[build.config]` not `[config]`
- Set `sample = "sample.env"`
- Use Makefile commands for consistency

### Configuration Files
- `.snyk` - Keep for Python dependency scanning
- `requirements.txt` - Pin exact versions with ==
- `sample.env` - Add if missing, ensure DEEPGRAM_API_KEY documented

---

## 3. .gitignore Standardization

**Create comprehensive .gitignore for all Flask repos:**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# Frontend (submodule)
frontend/node_modules/
frontend/dist/

# Lock files (Flask uses requirements.txt, frontend uses pnpm)
frontend/package-lock.json
frontend/yarn.lock

# Environment
.env
.env.local
*.local

# Logs
*.log

# Editor/OS
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Temporary files
*.tmp
.cache/
```

**Key points:**
- Explicitly ignore package-lock.json and yarn.lock in frontend/
- Match comprehensive pattern from Node.js starters
- Include Python-specific patterns

---

## 4. Architecture Patterns by Starter Type

### REST API Starters (flask-text-to-speech, flask-transcription)

**Simple Flask app architecture:**
- Serve static files from `frontend/dist/` in production
- REST endpoints matching Node.js counterparts:
  - **POST `/tts/synthesize`** - text-to-speech (accepts JSON body with text)
  - **POST `/stt/transcribe`** - transcription (multipart file upload)
- CORS enabled for development (allows Vite dev server)
- Direct Deepgram SDK calls, return results synchronously
- **Port 8080** (matches Node starters)

**Development mode:**
- Flask runs on port 8080
- Proxies frontend requests to Vite dev server on port 5173
- Enables HMR (Hot Module Replacement)

**Code structure:**
```python
from flask import Flask, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='./frontend/dist', static_url_path='/')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/tts/synthesize', methods=['POST'])
def synthesize():
    # Implementation
    pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

### WebSocket Proxy Starters (flask-live-text-to-speech, flask-live-transcription)

**Flask-SocketIO architecture:**
- Flask app with Flask-SocketIO for WebSocket handling
- Proxy pattern matching flask-voice-agent:
  - Accept client WebSocket connections
  - Proxy bidirectionally to Deepgram's WebSocket API
  - Forward all messages (JSON and binary)

**Endpoints:**
- **WebSocket `/tts/stream`** - live text-to-speech
- **WebSocket `/stt/stream`** - live transcription

**Port 8080** (matches Node starters)

**Development mode:**
- Backend runs on port 8080 with WebSocket support
- Proxies HTTP requests to Vite on port 5173
- Vite HMR via WebSocket (separate from API WebSocket)

**Code structure:**
```python
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import websocket

app = Flask(__name__, static_folder='./frontend/dist', static_url_path='/')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    # Setup proxy to Deepgram WebSocket
    pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    socketio.run(app, host='0.0.0.0', port=port)
```

---

## 5. README.md Standardization

**Match Node.js README structure exactly:**

```markdown
# Flask [Feature] Starter

[Feature description] using Deepgram's API with Python Flask backend and web frontend.

## Prerequisites

- [Deepgram API Key](https://console.deepgram.com/signup?jump=keys) (sign up for free)
- Python 3.9+
- pnpm 10+ (for frontend)

**Note:** This project uses git submodules for the frontend.

## Quick Start

1. **Clone the repository**

Clone the repository with submodules (the frontend is a shared submodule):

```bash
git clone --recurse-submodules https://github.com/deepgram-starters/flask-[feature].git
cd flask-[feature]
```

2. **Install dependencies**

```bash
# Option 1: Use Makefile (recommended)
make init

# Option 2: Manual install
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd frontend && pnpm install && cd ..
```

3. **Set your API key**

Create a `.env` file:

```bash
DEEPGRAM_API_KEY=your_api_key_here
```

4. **Run the app**

**Development mode** (with hot reload):

```bash
make dev
```

**Production mode** (build and serve):

```bash
make build
make start
```

### 🌐 Open the App
[http://localhost:8080](http://localhost:8080)

## Features

- [Feature list]

## Architecture

### Backend
- **[Architecture details]**
- Flask server with endpoint(s): `/[endpoint]`
- Proxies to Vite dev server in development mode

### Frontend
- **[Frontend details]**
- Pure vanilla JavaScript (no frameworks)
- Deepgram Design System for styling

## How It Works

- **Backend** (`app.py`): Flask server implementing the `/[endpoint]` endpoint
- **Frontend** (`frontend/`): Vite-powered web UI (shared submodule)
- **API**: Integrates with [Deepgram's [...] API](https://developers.deepgram.com/)

## Makefile Commands

This project includes a Makefile for framework-agnostic operations:

```bash
make help              # Show all available commands
make init              # Initialize submodules and install dependencies
make dev               # Start development servers
make build             # Build frontend for production
make start             # Start production server
make update            # Update submodules to latest
make clean             # Remove venv, node_modules and build artifacts
make status            # Show git and submodule status
```

Use `make` commands for a consistent experience regardless of language.

## Getting Help

- [Open an issue](https://github.com/deepgram-starters/flask-[feature]/issues/new)
- [Join our Discord](https://discord.gg/xWRaCDBtW4)
- [Deepgram Documentation](https://developers.deepgram.com/)

## Security

This project implements security best practices including:
- Dependency pinning to exact versions
- Automated vulnerability scanning with Snyk
- Environment variable management

See [SECURITY.md](./.github/SECURITY.md) for complete security documentation and reporting procedures.

## Contributing

Contributions are welcome! Please review:
- [Contributing Guidelines](./.github/CONTRIBUTING.md)
- [Code of Conduct](./.github/CODE_OF_CONDUCT.md)
- [Security Policy](./.github/SECURITY.md)

## License

MIT - See [LICENSE](./LICENSE)
```

**Key elements:**
- Submodule clone instructions prominent
- Makefile documented prominently
- Port 8080 (not 3000)
- Architecture + How It Works sections
- Security section before Contributing
- Community file paths reference .github/
- Emoji in "Open the App"

---

## 6. Implementation Checklist

**Per repository (x4):**

- [ ] Create feature branch
- [ ] Remove frontend folder, add as submodule
- [ ] Move community files to .github/
- [ ] Create/update Makefile
- [ ] Update .gitignore
- [ ] Update deepgram.toml
- [ ] Update README.md
- [ ] Verify app.py has correct port (8080) and endpoints
- [ ] Test: `make init` works
- [ ] Test: `make dev` works (frontend HMR functional)
- [ ] Test: `make build && make start` works
- [ ] Commit all changes
- [ ] Push and create PR

**Testing checklist per repo:**
1. Clone with `--recurse-submodules` works
2. `make init` installs all dependencies
3. `make dev` runs with frontend HMR
4. Frontend can call backend API successfully
5. `make build` produces frontend/dist/
6. `make start` serves from frontend/dist/
7. All endpoints return correct responses

---

## 7. Success Criteria

**Consistency achieved:**
- ✅ All Flask starters use frontend submodules
- ✅ Community files in .github/ folders
- ✅ Makefiles present with standard targets
- ✅ .gitignore comprehensive and consistent
- ✅ Port 8080 across all starters
- ✅ README structure matches Node.js pattern
- ✅ deepgram.toml uses [build.config]

**Multi-language ecosystem ready:**
- ✅ Same frontend reused in Node.js and Python
- ✅ Consistent developer experience
- ✅ Pattern established for future languages (Go, Rust, etc.)

---

## Tech Stack

**Backend:** Python 3.9+, Flask, Deepgram Python SDK
**Frontend:** Vanilla JavaScript, Vite, Deepgram Design System (via submodule)
**Build Tools:** Make, pnpm
**Testing:** Manual testing (API endpoints, frontend integration)
