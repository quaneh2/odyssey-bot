"""
Flask application for Ask The Odyssey.
Provides web interface and API endpoints for the RAG application.
"""

from flask import Flask, render_template, request, jsonify
from rag_engine import OdysseyRAG
import config
import os

app = Flask(__name__)

# Initialize RAG engine on startup
rag = None
CHROMA_DB_PATH = "data/chroma_db"


def init_rag_engine():
    """Initialize the RAG engine."""
    global rag
    try:
        if not os.path.exists(CHROMA_DB_PATH):
            print(f"Error: Database not found at {CHROMA_DB_PATH}")
            print("Please run setup.py first to create the database.")
            return False

        rag = OdysseyRAG(chroma_db_path=CHROMA_DB_PATH)
        print("✓ RAG engine initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize RAG engine: {e}")
        return False


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/ask', methods=['POST'])
def ask():
    """
    API endpoint to process questions.

    Request JSON:
        {
            "question": "user question here"
        }

    Response JSON:
        {
            "success": true/false,
            "answer": "response text" or null,
            "sources": [...] or null,
            "error": "error message" or null
        }
    """
    try:
        # Check if RAG engine is initialized
        if rag is None:
            return jsonify({
                "success": False,
                "answer": None,
                "sources": None,
                "error": "RAG engine not initialized. Please run setup.py first."
            }), 503

        # Get question from request
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "answer": None,
                "sources": None,
                "error": "Invalid request: JSON body required"
            }), 400

        question = data.get('question', '').strip()

        if not question:
            return jsonify({
                "success": False,
                "answer": None,
                "sources": None,
                "error": "Question cannot be empty"
            }), 400

        # Process question through RAG engine
        result = rag.query(question)

        # Return successful response
        return jsonify({
            "success": True,
            "answer": result['answer'],
            "sources": result['sources'],
            "error": None
        }), 200

    except ValueError as e:
        # Validation errors
        return jsonify({
            "success": False,
            "answer": None,
            "sources": None,
            "error": str(e)
        }), 400

    except RuntimeError as e:
        # Processing errors
        return jsonify({
            "success": False,
            "answer": None,
            "sources": None,
            "error": f"Processing error: {str(e)}"
        }), 500

    except Exception as e:
        # Unexpected errors
        print(f"Unexpected error: {e}")
        return jsonify({
            "success": False,
            "answer": None,
            "sources": None,
            "error": "An unexpected error occurred. Please try again."
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy" if rag is not None else "not_initialized",
        "database_path": CHROMA_DB_PATH,
        "database_exists": os.path.exists(CHROMA_DB_PATH)
    }), 200


# Initialize RAG engine at module level (runs in both development and production)
print("=" * 60)
print("Ask The Odyssey - Initializing Application")
print("=" * 60)
if not init_rag_engine():
    error_msg = (
        f"Failed to initialize RAG engine. "
        f"ChromaDB not found at {CHROMA_DB_PATH}. "
        f"Please run 'python setup.py' first to set up the database."
    )
    print(f"\n✗ ERROR: {error_msg}\n")
    print("=" * 60)
    raise RuntimeError(error_msg)

print("✓ Application initialized successfully")
print("=" * 60)


if __name__ == '__main__':
    print()
    print("Starting Flask development server...")
    print("Access the application at: http://localhost:5000")
    print("=" * 60)
    print()
    app.run(debug=True, port=5000)
