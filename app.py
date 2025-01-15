import os
import warnings

from flask import Flask, url_for, send_from_directory, render_template, request

import onnxruntime as ort
import numpy as np
from PIL import Image

BLOB_DIRECTORY = "/blob"
MODEL_NAME = "model.onnx"
MODEL_PATH = os.path.join(BLOB_DIRECTORY, MODEL_NAME)

file_to_inference = "inference_input.png"

DEPLOY = True

app = Flask(__name__)

# Load the ONNX model
session = ort.InferenceSession(MODEL_PATH)

def preprocess_image(image: Image.Image) -> np.ndarray:
    # Convert the image to a numpy array
    image_array = np.array(image).astype(np.float32)
    
    # Get the current dimensions of the image
    height, width, _ = image_array.shape
    
    # Calculate the padding needed to reach 640x640
    pad_height = max(0, 640 - height)
    pad_width = max(0, 640 - width)
    
    # Pad the image
    padded_image = np.pad(
        image_array,
        ((0, pad_height), (0, pad_width), (0, 0)),
        mode='constant',
        constant_values=0
    )
    
    # Resize the image to the expected input size (if necessary)
    if padded_image.shape[0] != 640 or padded_image.shape[1] != 640:
        padded_image = np.array(Image.fromarray(padded_image.astype(np.uint8)).resize((640, 640)))
    
    # Normalize the image (assuming the model expects normalized images)
    padded_image = padded_image / 255.0
    
    # Transpose the image to match the model's input shape (N, C, H, W)
    padded_image = np.transpose(padded_image, (2, 0, 1))
    
    # Add a batch dimension
    padded_image = np.expand_dims(padded_image, axis=0)
    
    return padded_image


def predict(file):
    try:
        image = Image.open(file).convert("RGB")
        # Preprocess the image
        inputs = preprocess_image(image)
        input_name = session.get_inputs()[0].name
        # Run inference
        prediction = session.run(None, {input_name: inputs})
        return {"prediction": prediction[0].tolist()}
    
    except Exception as e:
        raise e

@app.route("/predict")
def predict_route():
    try:
        # Call the predict function with the file to inference
        result = predict(os.path.join(BLOB_DIRECTORY, file_to_inference))
        # Pass the result to the template
        return f"<p>prediction: {result}</p>"
    except Exception as e:
        return f"Could not make a prediction due to the following error: {e}"

if DEPLOY:
    @app.route("/app/WEB/")
    def index():
        return render_template("index.html")

else:
    @app.route("/")
    def index():
        return render_template("index.html") 

    if __name__ == "__main__":
        app.run(debug=True, host="0.0.0.0")