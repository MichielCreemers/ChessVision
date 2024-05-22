from flask import Flask, request, jsonify
from PIL import Image
import base64
import os
from io import BytesIO

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        data = request.json
        image_data = data['image']
        image_data = base64.b64decode(image_data)

        image = Image.open(BytesIO(image_data))
        file_path = os.path.join(UPLOAD_FOLDER, 'uploaded_image.jpg')
        image.save(file_path)
        svg_file_path = './board.svg'

        if os.path.isfile(svg_file_path):
            with open(svg_file_path, 'rb') as image_file:
                # Read and encode the image in base64
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            # Prepare the JSON payload
            data = {
                'image': encoded_string
            }

        if os.path.exists(svg_file_path):
            return jsonify({"message": "File received", "file": data}), 200
        else:
            return jsonify({"error": "SVG file not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/')
def hello_world():
    return jsonify({"message": "Hello_world"}), 200


@app.route('/hello')
def hello():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
