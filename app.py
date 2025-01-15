import os
import warnings

from flask import Flask, url_for, send_from_directory, render_template

BLOB_DIRECTORY = "/blob"
DEPLOY = True

app = Flask(__name__)

if DEPLOY:
    @app.route("/app/WEB/")
    def index():
        image_filename = "Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi.jpg"
        return render_template("index.html", image_filename=image_filename)

    @app.route("/app/WEB/image/<filename>")
    def serve_file(filename):
        return send_from_directory(BLOB_DIRECTORY, filename)
    
    @app.route("/app/WEB/download/<filename>")
    def download_file_from_blob(filename):
        return send_from_directory(BLOB_DIRECTORY, filename, as_attachment=True)
else:
    @app.route("/")
    def index():
        image_filename = "Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi.jpg"
        return render_template("index.html", image_filename=image_filename)

    @app.route("/image/<filename>")
    def serve_file(filename):
        return send_from_directory(BLOB_DIRECTORY, filename)
    
    @app.route("/download/<filename>")
    def download_file_from_blob(filename):
        return send_from_directory(BLOB_DIRECTORY, filename, as_attachment=True)
    
