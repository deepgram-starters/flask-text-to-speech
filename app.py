"""
Flask Text-to-Speech Starter - Backend Server

This Flask server provides a REST API endpoint for text-to-speech synthesis
powered by Deepgram's Speak API. It returns binary audio data directly.

Key Features:
- POST endpoint: /tts/synthesize
- Accepts JSON text input
- Returns raw audio bytes (application/octet-stream)
- Serves built frontend from frontend/dist/
"""

import os
from flask import Flask, request, make_response
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
DEFAULT_PORT = 8080

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

# Initialize Flask app - serve built frontend from frontend/dist/
app = Flask(__name__, static_folder="./frontend/dist", static_url_path="/")

# Enable CORS for development (allows Vite dev server to connect)
CORS(app, resources={
    r"/*": {
        "origins": "*",  # In production, restrict to your domain
        "allow_headers": ["Content-Type", "X-Request-Id"],
        "expose_headers": ["X-Request-Id"],
        "supports_credentials": True
    }
})

# ============================================================================
# ROUTES
# ============================================================================

@app.route("/")
def index():
    """Serve the main frontend HTML file"""
    return app.send_static_file("index.html")

@app.route("/tts/synthesize", methods=["POST"])
def synthesize_speech():
    """
    Synthesize text to speech and return audio bytes

    Request Body (JSON):
        {
            "text": "Text to synthesize"
        }

    Query Parameters:
        model: TTS model (optional, default: aura-2-apollo-en)

    Headers:
        X-Request-Id: Request identifier for tracing (optional)

    Returns:
        200: Binary audio data (application/octet-stream)
        4XX: Error response (application/json)
    """
    # Get X-Request-Id header for tracing
    request_id = request.headers.get('X-Request-Id', '')

    try:
        # Parse JSON request body
        if not request.is_json:
            return json_abort(
                400,
                'INVALID_REQUEST',
                'Request body must be JSON',
                request_id
            )

        data = request.get_json()
        text = data.get('text', '').strip()

        # Validate text input
        if not text:
            return json_abort(
                400,
                'INVALID_REQUEST',
                'Text field is required and cannot be empty',
                request_id
            )

        # Get model from query parameters
        model = request.args.get('model', DEFAULT_MODEL)

        # Validate text length
        if len(text) > 2000:
            return json_abort(
                400,
                'TEXT_TOO_LONG',
                'Text exceeds maximum length of 2000 characters',
                request_id
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

        # Echo back X-Request-Id if provided
        if request_id:
            flask_response.headers['X-Request-Id'] = request_id

        return flask_response

    except ValueError as ve:
        # Handle validation errors (like our text length check)
        print(f"Validation error: {ve}")
        return json_abort(
            400,
            'INVALID_REQUEST',
            str(ve),
            request_id
        )
    except Exception as e:
        # Handle any other errors from Deepgram or processing
        print(f"Error synthesizing speech: {e}")
        error_message = str(e)

        # Check if it's a Deepgram API error about text length
        if 'too long' in error_message.lower() or 'length' in error_message.lower():
            return json_abort(
                400,
                'TEXT_TOO_LONG',
                'Text exceeds maximum allowed length',
                request_id
            )

        return json_abort(
            500,
            'SYNTHESIS_FAILED',
            'Failed to synthesize speech',
            request_id
        )

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def json_abort(status_code, error_code, message, request_id=''):
    """
    Return a JSON error response following the TTS contract

    Args:
        status_code: HTTP status code
        error_code: Error code from the contract
        message: Human-readable error message
        request_id: Request ID for tracing

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

    # Echo back X-Request-Id if provided
    if request_id:
        flask_response.headers['X-Request-Id'] = request_id

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
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    print("\n" + "=" * 70)
    print(f"🚀 Flask Text-to-Speech Server running at http://localhost:{port}")
    print(f"📦 Serving built frontend from frontend/dist")
    print(f"🎤 TTS endpoint: POST http://localhost:{port}/tts/synthesize")
    print(f"🐞 Debug mode: {'ON' if debug else 'OFF'}")
    print("=" * 70 + "\n")

    # Run Flask app
    app.run(
        host=host,
        port=port,
        debug=debug
    )
