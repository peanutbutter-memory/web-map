import os
import warnings
from dotenv import load_dotenv, find_dotenv

from flask import Flask, url_for, send_from_directory, render_template

# Load environment variables from .env file
dotenv_path = find_dotenv()
if not dotenv_path:
    warnings.warn("No .env file found. Using default environment variables.")
else:
    load_dotenv(dotenv_path)

BLOB_DIRECTORY = "/blob"

app = Flask(__name__)

@app.route("/")
def index():
    image_filename = "Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi.jpg"
    return render_template("index.html", image_filename=image_filename)

if os.getenv("FLASK_ENV") == "production":
    @app.route("/app/WEB/<filename>")
    def serve_file(filename):
        return send_from_directory(BLOB_DIRECTORY, filename)
    
    @app.route("/app/WEB/download/<filename>")
    def download_file_from_blob(filename):
        return send_from_directory(BLOB_DIRECTORY, filename, as_attachment=True)

else:
    @app.route("/<filename>")
    def serve_file(filename):
        return send_from_directory(BLOB_DIRECTORY, filename)

    @app.route("/download/<filename>")
    def download_file_from_blob(filename):
        return send_from_directory(BLOB_DIRECTORY, filename, as_attachment=True)

if os.getenv("FLASK_ENV") == "development":
    if __name__ == "__main__":
        app.run(debug=True, host='0.0.0.0')
