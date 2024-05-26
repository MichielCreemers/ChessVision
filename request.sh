# Sample format of a request.

curl -X POST http://192.168.63.176:5000/process_image \
     -H "Content-Type: application/json" \
     -d '{"image": "base64_encoded_image_data", "player": "b", "white_or_black_top": "black"}'