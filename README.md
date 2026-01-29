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

### Open the App
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
