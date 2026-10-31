"""
Entry point. Start the development server with:

    python run.py

Then open http://127.0.0.1:5000 in your browser.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True gives auto-reload and helpful error pages (local use only).
    app.run(debug=True)
