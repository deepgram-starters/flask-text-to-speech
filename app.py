"""
Flask Text-to-Speech Starter - Backend Server

This Flask server provides a REST API endpoint for text-to-speech synthesis
powered by Deepgram's Speak API. It returns binary audio data directly.

Key Features:
- POST endpoint: /api/text-to-speech
- Accepts JSON text input
- Returns raw audio bytes (application/octet-stream)
- JWT session auth with page nonce (production only)
- Serves built frontend from frontend/dist/
"""

import functools
import os
import secrets
import time

import jwt
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from deepgram import DeepgramClient
from dotenv import load_dotenv

# Load .env file (won't override existing environment variables)
load_dotenv(override=False)

# ============================================================================
# CONFIGURATION - Customize these values for your needs
# ============================================================================

# Default TTS model to use when none is specified
DEFAULT_MODEL = "aura-2-thalia-en"

# Server configuration
CONFIG = {
    "port": int(os.environ.get("PORT", 8081)),
    "host": os.environ.get("HOST", "0.0.0.0"),
}

# ============================================================================
# SESSION AUTH - JWT tokens with page nonce for production security
# ============================================================================

SESSION_SECRET = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)
REQUIRE_NONCE = bool(os.environ.get("SESSION_SECRET"))

# In-memory nonce store: nonce -> expiry timestamp
session_nonces = {}
NONCE_TTL = 5 * 60  # 5 minutes
JWT_EXPIRY = 3600  # 1 hour


def generate_nonce():
    """Generates a single-use nonce and stores it with an expiry."""
    nonce = secrets.token_hex(16)
    session_nonces[nonce] = time.time() + NONCE_TTL
    return nonce


def consume_nonce(nonce):
    """Validates and consumes a nonce (single-use). Returns True if valid."""
    expiry = session_nonces.pop(nonce, None)
    if expiry is None:
        return False
    return time.time() < expiry


def cleanup_nonces():
    """Remove expired nonces."""
    now = time.time()
    expired = [k for k, v in session_nonces.items() if now >= v]
    for k in expired:
        del session_nonces[k]


# Read frontend/dist/index.html template for nonce injection
_index_html_template = None
try:
    with open(os.path.join(os.path.dirname(__file__), "frontend", "dist", "index.html")) as f:
        _index_html_template = f.read()
except FileNotFoundError:
    pass  # No built frontend (dev mode)


def require_session(f):
    """Decorator that validates JWT from Authorization header."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": {
                    "type": "AuthenticationError",
                    "code": "MISSING_TOKEN",
                    "message": "Authorization header with Bearer token is required",
                }
            }), 401
        token = auth_header[7:]
        try:
            jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": {
                    "type": "AuthenticationError",
                    "code": "INVALID_TOKEN",
                    "message": "Session expired, please refresh the page",
                }
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "error": {
                    "type": "AuthenticationError",
                    "code": "INVALID_TOKEN",
                    "message": "Invalid session token",
                }
            }), 401
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# API KEY VALIDATION
# ============================================================================

def validate_api_key():
    """Validates that the Deepgram API key is configured"""
    api_key = os.environ.get("DEEPGRAM_API_KEY")

    if not api_key:
        print("\n" + "="*70)
        print("ERROR: Deepgram API key not found!")
        print("="*70)
        print("\nPlease set your API key using one of these methods:")
        print("\n1. Create a .env file (recommended):")
        print("   DEEPGRAM_API_KEY=your_api_key_here")
        print("\n2. Environment variable:")
        print("   export DEEPGRAM_API_KEY=your_api_key_here")
        print("\nGet your API key at: https://console.deepgram.com")
        print("="*70 + "\n")
        raise ValueError("DEEPGRAM_API_KEY environment variable is required")

    return api_key

# Validate on startup
API_KEY = validate_api_key()

# ============================================================================
# SETUP - Initialize Flask and CORS
# ============================================================================

# Initialize Flask app (API server only)
app = Flask(__name__)

# Enable CORS for frontend communication
CORS(app)

# ============================================================================
# SESSION ROUTES - Auth endpoints (unprotected)
# ============================================================================

@app.route("/", methods=["GET"])
def serve_index():
    """Serve index.html with injected session nonce (production only)."""
    if not _index_html_template:
        return "Frontend not built. Run make build first.", 404
    cleanup_nonces()
    nonce = generate_nonce()
    html = _index_html_template.replace(
        "</head>",
        f'<meta name="session-nonce" content="{nonce}">\n</head>'
    )
    response = make_response(html)
    response.headers["Content-Type"] = "text/html"
    return response


@app.route("/api/session", methods=["GET"])
def get_session():
    """Issues a JWT. In production, requires valid nonce via X-Session-Nonce header."""
    if REQUIRE_NONCE:
        nonce = request.headers.get("X-Session-Nonce")
        if not nonce or not consume_nonce(nonce):
            return jsonify({
                "error": {
                    "type": "AuthenticationError",
                    "code": "INVALID_NONCE",
                    "message": "Valid session nonce required. Please refresh the page.",
                }
            }), 403

    token = jwt.encode(
        {"iat": int(time.time()), "exp": int(time.time()) + JWT_EXPIRY},
        SESSION_SECRET,
        algorithm="HS256",
    )
    return jsonify({"token": token})


# ============================================================================
# ROUTES
# ============================================================================

@app.route("/api/text-to-speech", methods=["POST"])
@require_session
def synthesize_speech():
    """
    Synthesize text to speech and return audio bytes

    Request Body (JSON):
        {
            "text": "Text to synthesize"
        }

    Query Parameters:
        model: TTS model (optional, default: aura-2-apollo-en)

    Returns:
        200: Binary audio data (application/octet-stream)
        4XX: Error response (application/json)
    """
    try:
        # Parse JSON request body
        if not request.is_json:
            return json_abort(
                400,
                'INVALID_REQUEST',
                'Request body must be JSON'
            )

        data = request.get_json()
        text = data.get('text', '').strip()

        # Validate text input
        if not text:
            return json_abort(
                400,
                'INVALID_REQUEST',
                'Text field is required and cannot be empty'
            )

        # Get model from query parameters
        model = request.args.get('model', DEFAULT_MODEL)

        # Validate text length
        if len(text) > 2000:
            return json_abort(
                400,
                'TEXT_TOO_LONG',
                'Text exceeds maximum length of 2000 characters'
            )

        # Initialize Deepgram client
        client = DeepgramClient(api_key=API_KEY)

        # Generate speech using Deepgram Speak API v1
        # This returns an iterator of audio bytes
        audio_generator = client.speak.v1.audio.generate(
            text=text,
            model=model
        )

        # Convert the iterator to bytes for the response
        # The generator yields chunks of audio data
        audio_bytes = b''.join(audio_generator)

        # Return audio bytes with appropriate headers
        flask_response = make_response(audio_bytes)
        flask_response.headers['Content-Type'] = 'application/octet-stream'

        return flask_response

    except ValueError as ve:
        # Handle validation errors (like our text length check)
        print(f"Validation error: {ve}")
        return json_abort(
            400,
            'INVALID_REQUEST',
            str(ve)
        )
    except Exception as e:
        # Handle any other errors from Deepgram or processing
        print(f"Error synthesizing speech: {e}")
        return json_abort(
            500,
            'SYNTHESIS_FAILED',
            'Failed to synthesize speech'
        )

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def json_abort(status_code, error_code, message):
    """
    Return a JSON error response following the TTS contract

    Args:
        status_code: HTTP status code
        error_code: Error code from the contract
        message: Human-readable error message

    Returns:
        Flask Response with JSON error body
    """
    response_data = {
        'error': {
            'type': 'SynthesisError',
            'code': error_code,
            'message': message
        }
    }

    flask_response = make_response(response_data, status_code)
    flask_response.headers['Content-Type'] = 'application/json'

    return flask_response

@app.route("/api/metadata", methods=["GET"])
def get_metadata():
    """
    GET /api/metadata

    Returns metadata about this starter application from deepgram.toml
    Required for standardization compliance
    """
    try:
        import toml
        with open('deepgram.toml', 'r') as f:
            config = toml.load(f)

        if 'meta' not in config:
            return json_abort(
                500,
                'INTERNAL_SERVER_ERROR',
                'Missing [meta] section in deepgram.toml'
            )

        response = make_response(config['meta'], 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    except FileNotFoundError:
        return json_abort(
            500,
            'INTERNAL_SERVER_ERROR',
            'deepgram.toml file not found'
        )

    except Exception as e:
        print(f"Error reading metadata: {e}")
        return json_abort(
            500,
            'INTERNAL_SERVER_ERROR',
            f'Failed to read metadata from deepgram.toml: {str(e)}'
        )

# ============================================================================
# SERVER START
# ============================================================================

if __name__ == "__main__":
    port = CONFIG["port"]
    host = CONFIG["host"]
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    nonce_status = " (nonce required)" if REQUIRE_NONCE else ""
    print("\n" + "=" * 70)
    print(f"🚀 Flask Text To Speech Server (Backend API)")
    print("=" * 70)
    print(f"🚀 Backend API Server running at http://localhost:{port}")
    print(f"")
    print(f"📡 GET  /api/session{nonce_status}")
    print(f"📡 POST /api/text-to-speech (auth required)")
    print(f"📡 GET  /api/metadata")
    print(f"Debug:    {'ON' if debug else 'OFF'}")
    print("=" * 70 + "\n")

    # Run Flask app
    app.run(
        host=host,
        port=port,
        debug=debug
    )
