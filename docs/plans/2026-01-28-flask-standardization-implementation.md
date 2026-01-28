# Flask Starters Standardization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Standardize 4 Flask starters to match Node.js pattern with frontend submodules, Makefiles, and consistent configuration.

**Architecture:** Each Flask starter replaces its frontend folder with a git submodule, adds Makefile for operations, moves community files to .github/, and updates all configuration to match Node.js standards.

**Tech Stack:** Python 3.9+, Flask, Make, git submodules, pnpm

---

### Task 1: Standardize flask-text-to-speech

**Files:**
- Remove: `frontend/` (entire directory)
- Create: `.gitmodules`
- Modify: `.gitignore`
- Create: `Makefile`
- Modify: `deepgram.toml`
- Modify: `README.md`
- Modify: `app.py:29` (change port)
- Move: `CODE_OF_CONDUCT.md` → `.github/CODE_OF_CONDUCT.md`
- Move: `CONTRIBUTING.md` → `.github/CONTRIBUTING.md`
- Move: `SECURITY.md` → `.github/SECURITY.md`

**Step 1: Remove old frontend and add submodule**

Run:
```bash
cd /Users/lukeoliff/Projects/deepgram-starters/flask-text-to-speech
git rm -r frontend
git commit -m "refactor: remove frontend folder to prepare for submodule"
git submodule add https://github.com/deepgram-starters/text-to-speech-html frontend
git commit -m "feat: add text-to-speech-html as git submodule"
```

Expected: frontend/ now tracked as submodule, .gitmodules created

**Step 2: Move community files to .github/**

Run:
```bash
mkdir -p .github
git mv CODE_OF_CONDUCT.md .github/
git mv CONTRIBUTING.md .github/
git mv SECURITY.md .github/
git commit -m "refactor: move community files to .github folder"
```

Expected: Community files in .github/, root cleaner

**Step 3: Create comprehensive .gitignore**

Create/replace: `.gitignore`

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

Run: `git add .gitignore && git commit -m "chore: standardize .gitignore with comprehensive patterns"`

**Step 4: Create Makefile**

Create: `Makefile`

```makefile
.PHONY: help init dev build start update clean status

help:
	@echo "Available commands:"
	@echo "  make init     - Initialize submodules and install dependencies"
	@echo "  make dev      - Start development servers (Flask + Vite HMR)"
	@echo "  make build    - Build frontend for production"
	@echo "  make start    - Start production server"
	@echo "  make update   - Update submodules to latest"
	@echo "  make clean    - Remove venv, node_modules and build artifacts"
	@echo "  make status   - Show git and submodule status"

init:
	@echo "Initializing submodules..."
	git submodule update --init --recursive
	@echo "Creating Python virtual environment..."
	python3 -m venv venv
	@echo "Installing Python dependencies..."
	./venv/bin/pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && pnpm install
	@echo "Setup complete! Run 'make dev' to start development."

dev:
	@echo "Starting development server..."
	@export NODE_ENV=development && ./venv/bin/python app.py

build:
	@echo "Building frontend for production..."
	cd frontend && pnpm build
	@echo "Build complete!"

start:
	@echo "Starting production server..."
	@export NODE_ENV=production && ./venv/bin/python app.py

update:
	@echo "Updating submodules..."
	git submodule update --remote --merge
	@echo "Submodules updated!"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf venv/
	rm -rf frontend/node_modules/
	rm -rf frontend/dist/
	rm -rf __pycache__/
	rm -rf *.pyc
	@echo "Clean complete!"

status:
	@echo "Git status:"
	@git status --short
	@echo "\nSubmodule status:"
	@git submodule status
```

Run: `git add Makefile && git commit -m "feat: add Makefile for framework-agnostic operations"`

**Step 5: Update deepgram.toml**

Modify: `deepgram.toml`

Change:
```toml
[config]
sample = "sample.env"
output = ".env"
```

To:
```toml
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

Run: `git add deepgram.toml && git commit -m "fix(config): standardize deepgram.toml to use [build.config] and Makefile commands"`

**Step 6: Update app.py port configuration**

Modify: `app.py:29`

Change:
```python
DEFAULT_PORT = 3000
```

To:
```python
DEFAULT_PORT = 8080
```

Run: `git add app.py && git commit -m "fix: change default port from 3000 to 8080 to match Node starters"`

**Step 7: Update README.md**

Replace entire README with:

```markdown
# Flask Text-to-Speech Starter

Text-to-speech demo using Deepgram's API with Python Flask backend and web frontend.

## Prerequisites

- [Deepgram API Key](https://console.deepgram.com/signup?jump=keys) (sign up for free)
- Python 3.9+
- pnpm 10+ (for frontend)

**Note:** This project uses git submodules for the frontend.

## Quick Start

1. **Clone the repository**

Clone the repository with submodules (the frontend is a shared submodule):

```bash
git clone --recurse-submodules https://github.com/deepgram-starters/flask-text-to-speech.git
cd flask-text-to-speech
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

- Enter text to convert to audio
- Multiple model options
- View text-to-speech history

## Architecture

### Backend
- **Stateless API**: Returns audio directly, no file storage
- Flask server with single endpoint: `/tts/synthesize`
- Proxies to Vite dev server in development mode

### Frontend
- **Hybrid Storage**:
  - IndexedDB for audio blobs (efficient binary storage)
  - localStorage for metadata (fast UI rendering)
- Pure vanilla JavaScript (no frameworks)
- Deepgram Design System for styling

## How It Works

- **Backend** (`app.py`): Flask server implementing the `/tts/synthesize` endpoint
- **Frontend** (`frontend/`): Vite-powered web UI (shared submodule)
- **API**: Integrates with [Deepgram's Text-to-Speech API](https://developers.deepgram.com/)

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

- [Open an issue](https://github.com/deepgram-starters/flask-text-to-speech/issues/new)
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

Run: `git add README.md && git commit -m "docs: standardize README to match Node.js pattern with submodule instructions"`

**Step 8: Test the setup**

Run:
```bash
make init
```
Expected: venv created, Python deps installed, frontend deps installed

Run:
```bash
make build
```
Expected: frontend/dist/ created with built files

Run:
```bash
ls frontend/dist/
```
Expected: index.html, assets/, etc.

**Step 9: Push changes**

Run:
```bash
git push origin main
```

Expected: All commits pushed successfully

---

### Task 2: Standardize flask-transcription

**Files:**
- Remove: `frontend/` (entire directory)
- Create: `.gitmodules`
- Modify: `.gitignore`
- Create: `Makefile`
- Modify: `deepgram.toml`
- Modify: `README.md`
- Modify: `app.py` (change port)
- Move: `CODE_OF_CONDUCT.md` → `.github/CODE_OF_CONDUCT.md`
- Move: `CONTRIBUTING.md` → `.github/CONTRIBUTING.md`
- Move: `SECURITY.md` → `.github/SECURITY.md`

**Step 1: Remove old frontend and add submodule**

Run:
```bash
cd /Users/lukeoliff/Projects/deepgram-starters/flask-transcription
git rm -r frontend
git commit -m "refactor: remove frontend folder to prepare for submodule"
git submodule add https://github.com/deepgram-starters/transcription-html frontend
git commit -m "feat: add transcription-html as git submodule"
```

Expected: frontend/ now tracked as submodule

**Step 2: Move community files to .github/**

Run:
```bash
mkdir -p .github
git mv CODE_OF_CONDUCT.md .github/
git mv CONTRIBUTING.md .github/
git mv SECURITY.md .github/
git commit -m "refactor: move community files to .github folder"
```

Expected: Community files in .github/

**Step 3: Create comprehensive .gitignore**

Create/replace: `.gitignore`

(Use same .gitignore content from Task 1 Step 3)

Run: `git add .gitignore && git commit -m "chore: standardize .gitignore with comprehensive patterns"`

**Step 4: Create Makefile**

Create: `Makefile`

(Use same Makefile content from Task 1 Step 4)

Run: `git add Makefile && git commit -m "feat: add Makefile for framework-agnostic operations"`

**Step 5: Update deepgram.toml**

Modify: `deepgram.toml`

Add/modify to include:
```toml
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

Run: `git add deepgram.toml && git commit -m "fix(config): standardize deepgram.toml to use [build.config] and Makefile commands"`

**Step 6: Update app.py port configuration**

Modify: `app.py` (find DEFAULT_PORT line)

Change port from 3000 to 8080

Run: `git add app.py && git commit -m "fix: change default port from 3000 to 8080 to match Node starters"`

**Step 7: Update README.md**

Replace with:

```markdown
# Flask Transcription Starter

Speech-to-text demo using Deepgram's API with Python Flask backend and web frontend.

## Prerequisites

- [Deepgram API Key](https://console.deepgram.com/signup?jump=keys) (sign up for free)
- Python 3.9+
- pnpm 10+ (for frontend)

**Note:** This project uses git submodules for the frontend.

## Quick Start

1. **Clone the repository**

Clone the repository with submodules (the frontend is a shared submodule):

```bash
git clone --recurse-submodules https://github.com/deepgram-starters/flask-transcription.git
cd flask-transcription
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

- Upload audio files or provide URLs for transcription
- Multiple model options
- View transcription history

## Architecture

### Backend
- **Stateless API**: Returns transcription directly, no file storage
- Flask server with single endpoint: `/stt/transcribe`
- Proxies to Vite dev server in development mode

### Frontend
- **Hybrid Storage**:
  - IndexedDB for transcription data (efficient storage)
  - localStorage for metadata (fast UI rendering)
- Pure vanilla JavaScript (no frameworks)
- Deepgram Design System for styling

## How It Works

- **Backend** (`app.py`): Flask server implementing the `/stt/transcribe` endpoint
- **Frontend** (`frontend/`): Vite-powered web UI (shared submodule)
- **API**: Integrates with [Deepgram's Speech-to-Text API](https://developers.deepgram.com/)

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

- [Open an issue](https://github.com/deepgram-starters/flask-transcription/issues/new)
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

Run: `git add README.md && git commit -m "docs: standardize README to match Node.js pattern with submodule instructions"`

**Step 8: Test and push**

Run:
```bash
make init
make build
git push origin main
```

Expected: All working and pushed

---

### Task 3: Standardize flask-live-text-to-speech

**Files:**
- Remove: `frontend/` (entire directory)
- Create: `.gitmodules`
- Modify: `.gitignore`
- Create: `Makefile`
- Modify: `deepgram.toml`
- Modify: `README.md`
- Modify: `app.py` (change port)
- Move: `CODE_OF_CONDUCT.md` → `.github/CODE_OF_CONDUCT.md`
- Move: `CONTRIBUTING.md` → `.github/CONTRIBUTING.md`
- Move: `SECURITY.md` → `.github/SECURITY.md`

**Step 1: Remove old frontend and add submodule**

Run:
```bash
cd /Users/lukeoliff/Projects/deepgram-starters/flask-live-text-to-speech
git rm -r frontend
git commit -m "refactor: remove frontend folder to prepare for submodule"
git submodule add https://github.com/deepgram-starters/live-text-to-speech-html frontend
git commit -m "feat: add live-text-to-speech-html as git submodule"
```

Expected: frontend/ now tracked as submodule

**Step 2: Move community files to .github/**

Run:
```bash
mkdir -p .github
git mv CODE_OF_CONDUCT.md .github/ 2>/dev/null || true
git mv CONTRIBUTING.md .github/ 2>/dev/null || true
git mv SECURITY.md .github/ 2>/dev/null || true
git commit -m "refactor: move community files to .github folder" 2>/dev/null || echo "No files to move"
```

Expected: Community files in .github/ if they exist

**Step 3: Create comprehensive .gitignore**

Create/replace: `.gitignore`

(Use same .gitignore content from Task 1 Step 3)

Run: `git add .gitignore && git commit -m "chore: standardize .gitignore with comprehensive patterns"`

**Step 4: Create Makefile**

Create: `Makefile`

(Use same Makefile content from Task 1 Step 4)

Run: `git add Makefile && git commit -m "feat: add Makefile for framework-agnostic operations"`

**Step 5: Update deepgram.toml**

Modify: `deepgram.toml`

Add/modify to include:
```toml
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

Run: `git add deepgram.toml && git commit -m "fix(config): standardize deepgram.toml to use [build.config] and Makefile commands"`

**Step 6: Update app.py port configuration**

Modify: `app.py` (find DEFAULT_PORT or port configuration)

Change port from 3000 to 8080

Run: `git add app.py && git commit -m "fix: change default port from 3000 to 8080 to match Node starters"`

**Step 7: Update README.md**

Replace with:

```markdown
# Flask Live Text-to-Speech Starter

Live text-to-speech demo using Deepgram's API with Python Flask backend and web frontend.

## Prerequisites

- [Deepgram API Key](https://console.deepgram.com/signup?jump=keys) (sign up for free)
- Python 3.9+
- pnpm 10+ (for frontend)

**Note:** This project uses git submodules for the frontend.

## Quick Start

1. **Clone the repository**

Clone the repository with submodules (the frontend is a shared submodule):

```bash
git clone --recurse-submodules https://github.com/deepgram-starters/flask-live-text-to-speech.git
cd flask-live-text-to-speech
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

- Real-time text-to-speech with live audio playback
- Interactive text input
- Configurable voice models
- Connection statistics

## Architecture

### Backend
- **WebSocket Proxy**: Bidirectional streaming to Deepgram's Live TTS API
- Flask-SocketIO server with WebSocket endpoint: `/tts/stream`
- Proxies to Vite dev server in development mode

### Frontend
- Real-time audio streaming and playback
- Pure vanilla JavaScript (no frameworks)
- Deepgram Design System for styling

## How It Works

- **Backend** (`app.py`): Flask-SocketIO server implementing the `/tts/stream` WebSocket endpoint
- **Frontend** (`frontend/`): Vite-powered web UI (shared submodule)
- **API**: Integrates with [Deepgram's Live Text-to-Speech API](https://developers.deepgram.com/)

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

- [Open an issue](https://github.com/deepgram-starters/flask-live-text-to-speech/issues/new)
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

Run: `git add README.md && git commit -m "docs: standardize README to match Node.js pattern with submodule instructions"`

**Step 8: Test and push**

Run:
```bash
make init
make build
git push origin main
```

Expected: All working and pushed

---

### Task 4: Standardize flask-live-transcription

**Files:**
- Remove: `frontend/` (entire directory)
- Create: `.gitmodules`
- Modify: `.gitignore`
- Create: `Makefile`
- Modify: `deepgram.toml`
- Modify: `README.md`
- Modify: `app.py` (change port)
- Move: `CODE_OF_CONDUCT.md` → `.github/CODE_OF_CONDUCT.md`
- Move: `CONTRIBUTING.md` → `.github/CONTRIBUTING.md`
- Move: `SECURITY.md` → `.github/SECURITY.md`

**Step 1: Remove old frontend and add submodule**

Run:
```bash
cd /Users/lukeoliff/Projects/deepgram-starters/flask-live-transcription
git rm -r frontend
git commit -m "refactor: remove frontend folder to prepare for submodule"
git submodule add https://github.com/deepgram-starters/live-transcription-html frontend
git commit -m "feat: add live-transcription-html as git submodule"
```

Expected: frontend/ now tracked as submodule

**Step 2: Move community files to .github/**

Run:
```bash
mkdir -p .github
git mv CODE_OF_CONDUCT.md .github/ 2>/dev/null || true
git mv CONTRIBUTING.md .github/ 2>/dev/null || true
git mv SECURITY.md .github/ 2>/dev/null || true
git commit -m "refactor: move community files to .github folder" 2>/dev/null || echo "No files to move"
```

Expected: Community files in .github/ if they exist

**Step 3: Create comprehensive .gitignore**

Create/replace: `.gitignore`

(Use same .gitignore content from Task 1 Step 3)

Run: `git add .gitignore && git commit -m "chore: standardize .gitignore with comprehensive patterns"`

**Step 4: Create Makefile**

Create: `Makefile`

(Use same Makefile content from Task 1 Step 4)

Run: `git add Makefile && git commit -m "feat: add Makefile for framework-agnostic operations"`

**Step 5: Update deepgram.toml**

Modify: `deepgram.toml`

Add/modify to include:
```toml
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

Run: `git add deepgram.toml && git commit -m "fix(config): standardize deepgram.toml to use [build.config] and Makefile commands"`

**Step 6: Update app.py port configuration**

Modify: `app.py` (find DEFAULT_PORT or port configuration)

Change port from 3000 to 8080

Run: `git add app.py && git commit -m "fix: change default port from 3000 to 8080 to match Node starters"`

**Step 7: Update README.md**

Replace with:

```markdown
# Flask Live Transcription Starter

Live speech-to-text transcription demo using Deepgram's API with Python Flask backend and web frontend.

## Prerequisites

- [Deepgram API Key](https://console.deepgram.com/signup?jump=keys) (sign up for free)
- Python 3.9+
- pnpm 10+ (for frontend)

**Note:** This project uses git submodules for the frontend.

## Quick Start

1. **Clone the repository**

Clone the repository with submodules (the frontend is a shared submodule):

```bash
git clone --recurse-submodules https://github.com/deepgram-starters/flask-live-transcription.git
cd flask-live-transcription
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

- Real-time speech-to-text transcription
- Live audio streaming with visual feedback
- Multiple model options
- Connection statistics

## Architecture

### Backend
- **WebSocket Proxy**: Bidirectional streaming to Deepgram's Live STT API
- Flask-SocketIO server with WebSocket endpoint: `/stt/stream`
- Proxies to Vite dev server in development mode

### Frontend
- Real-time microphone capture and transcription
- Pure vanilla JavaScript (no frameworks)
- Deepgram Design System for styling

## How It Works

- **Backend** (`app.py`): Flask-SocketIO server implementing the `/stt/stream` WebSocket endpoint
- **Frontend** (`frontend/`): Vite-powered web UI (shared submodule)
- **API**: Integrates with [Deepgram's Live Transcription API](https://developers.deepgram.com/)

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

- [Open an issue](https://github.com/deepgram-starters/flask-live-transcription/issues/new)
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

Run: `git add README.md && git commit -m "docs: standardize README to match Node.js pattern with submodule instructions"`

**Step 8: Test and push**

Run:
```bash
make init
make build
git push origin main
```

Expected: All working and pushed

---

### Task 5: Verify all Flask starters

**Step 1: Verify submodules are tracked**

Run:
```bash
cd /Users/lukeoliff/Projects/deepgram-starters
for repo in flask-text-to-speech flask-transcription flask-live-text-to-speech flask-live-transcription; do
  echo "=== $repo ==="
  cd "$repo"
  git submodule status
  cd ..
done
```

Expected: Each repo shows frontend submodule with commit hash

**Step 2: Verify community files in .github/**

Run:
```bash
for repo in flask-text-to-speech flask-transcription flask-live-text-to-speech flask-live-transcription; do
  echo "=== $repo ==="
  cd "$repo"
  ls -la .github/
  cd ..
done
```

Expected: CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md in each .github/

**Step 3: Verify Makefiles exist**

Run:
```bash
for repo in flask-text-to-speech flask-transcription flask-live-text-to-speech flask-live-transcription; do
  echo "=== $repo ==="
  cd "$repo"
  ls -la Makefile
  cd ..
done
```

Expected: Makefile present in each

**Step 4: Verify all repos pushed**

Run:
```bash
for repo in flask-text-to-speech flask-transcription flask-live-text-to-speech flask-live-transcription; do
  echo "=== $repo ==="
  cd "$repo"
  git status
  cd ..
done
```

Expected: All repos show "nothing to commit, working tree clean" and "Your branch is up to date with 'origin/main'"

**Step 5: Document completion**

Create summary file showing:
- ✅ All 4 Flask starters standardized
- ✅ Frontend submodules added
- ✅ Community files in .github/
- ✅ Makefiles created
- ✅ Port 8080 configured
- ✅ READMEs match Node.js pattern
- ✅ deepgram.toml uses [build.config]

Run:
```bash
echo "Flask Starters Standardization Complete" > /tmp/flask-standardization-complete.txt
echo "All 4 repositories now match Node.js pattern" >> /tmp/flask-standardization-complete.txt
cat /tmp/flask-standardization-complete.txt
```

Expected: Summary file created and displayed
