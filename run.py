import os

from app import app  # or however you're importing your Flask app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # fallback to 5000 if PORT isn't set
    app.run(host="0.0.0.0", port=port, debug=True)
