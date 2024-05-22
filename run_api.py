from flask import Flask, request, send_file, jsonify
from PIL import Image
import numpy as np
import os
import io
import base64
import json
import argparse
from ultralytics import YOLO
from stockfish import Stockfish
import cv2
import board.corners as corners
import board.grid as grid
import board.pieces as pieces
import board.moves as moves

app = Flask(__name__)


UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024

def image_to_FEN(image, white_or_black_top, 
                 corner_model, grid_model, pieces_model,
                 corner_conf, corner_iou,
                 pieces_conf, pieces_iou,
                 offsetx, offsety, num_points):

    # Predict corners
    corners_results = corners.predict_corners(corner_model, image, corner_conf, corner_iou)

    # Transformation 1
    corners4 = corners.get_corner_coordinates(corners_results)
    labeled_corners, sorted_corners = corners.label_and_sort_corners(corners4)
    if labeled_corners is None or sorted_corners is None:
        print("There was an error in detecting the corners of the board. Please try again.")
        exit()
    sorted_corners = corners.add_offset(sorted_corners, offsetx, offsety)
    transformed_image = corners.transform_image_corners(image, sorted_corners)
    transformed_image = cv2.cvtColor(transformed_image, cv2.COLOR_BGR2RGB) # convert image back to rgb
    
    # Grid detection
    grid_results = grid.predict_grid_segmentation(grid_model, transformed_image)
    grid_corners = grid.get_corners_from_grid_segmentation(grid_results)
    transformed_grid, transformation = grid.make_perspective_transform(transformed_image, grid_corners)
    transformed_grid = cv2.cvtColor(transformed_grid, cv2.COLOR_BGR2RGB) # convert image back to rgb
    
    # Grid Orientation
    # If white top, rotate 180 degrees
    if white_or_black_top == 'white':
        transformed_grid = cv2.rotate(transformed_grid, cv2.ROTATE_180)
        transformed_image = cv2.rotate(transformed_image, cv2.ROTATE_180)
        
    # Check if a 90 degree rotation is needed
    need_rotation = grid.correct_orientation_advanced(transformed_grid)
    if need_rotation:
        # transformed_grid = cv2.rotate(transformed_grid, cv2.ROTATE_90_CLOCKWISE)
        # transformed_image = cv2.rotate(transformed_image, cv2.ROTATE_90_CLOCKWISE)
        print("Need to rotate 90 degrees, code not optimized yet")
    
    # Piece detection
    pieces_results = pieces.detect_pieces(pieces_model, transformed_image, pieces_conf, pieces_iou)
    boxes, labels = pieces.extract_boxes_labels(pieces_results)
    sampled_points = pieces.get_sampled_points(boxes, labels, num_points)
    
    mapped_pieces = pieces.get_mapped_pieces(sampled_points, transformation)
    fen_notation = pieces.create_FEN_notation(mapped_pieces)
    
    return fen_notation

@app.route('/process_image', methods=['POST'])
def process_image():
    print("ok")
    data = request.json
    if not data:
        return jsonify({"error": "No data sent"}), 400
    
    image_data = data['image']
    image_data = base64.b64decode(image_data)    
    # print(image_data)

    if not image_data:
        return jsonify({"error": "No image has been sent"}), 400
    
    
    image = Image.open(io.BytesIO(image_data))
    file_path = os.path.join(UPLOAD_FOLDER, 'uploaded_image.jpg')
    image.save(file_path)
    image = cv2.imread(file_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        
        
    print("white or black")
    white_or_black_top = data.get('white_or_black_top')
    print(white_or_black_top)
    player = data.get('player')
    print(player)
    # Ensure that player is either 'w' or 'b'
    if player not in ['w', 'b']:
        return jsonify({"error": "Invalid player value"}), 400

    # Assume these variables are defined and loaded correctly in your environment
    # corners_model, grid_model, pieces_model, corner_conf, corner_iou, 
    # pieces_conf, xoffset, yoffset, piece_samples, stockfish
    print("trying fen")
    
    fen = image_to_FEN(
        image, white_or_black_top, corners_model, grid_model, 
        pieces_model, corner_conf, corner_iou, pieces_conf,
        pieces_iou,xoffset, yoffset,num_points)
    
    print("fen is" + fen)
    fen = moves.determineFEN(fen, player)

    if moves.is_valid_fen(fen):
        svg_output = moves.output_board_best_move(fen, stockfish)
    else:
        return jsonify({"error": "Invalid FEN notation"}), 400

    svg_content = svg_output.data
    svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    
    return jsonify({"svg": svg_base64}),200
  

@app.route('/hello', methods=['GET'])
def hello_world():
    return jsonify(message="Hello, World!")

        
def parse_args():
    """Parse input arguments from JSON config file."""
    with open("config.json", "r") as f:
        config = json.load(f)
    args = argparse.Namespace(**config)
    return args

if __name__ == '__main__':
    print('*****************************************************************************')
    print('''                                                                                                              
                   ,--,                                                                            ,----..            ,--. 
 ,----..         ,--.'|    ,---,.  .--.--.    .--.--.                ,---,   .--.--.     ,---,    /   /   \         ,--.'| 
/   /   \     ,--,  | :  ,'  .' | /  /    '. /  /    '.       ,---.,`--.' | /  /    '. ,`--.' |  /   .     :    ,--,:  : | 
|   :     :,---.'|  : ',---.'   ||  :  /`. /|  :  /`. /      /__./||   :  :|  :  /`. / |   :  : .   /   ;.  \,`--.'`|  ' : 
.   |  ;. /|   | : _' ||   |   .';  |  |--` ;  |  |--`  ,---.;  ; |:   |  ';  |  |--`  :   |  '.   ;   /  ` ;|   :  :  | | 
.   ; /--` :   : |.'  |:   :  |-,|  :  ;_   |  :  ;_   /___/ \  | ||   :  ||  :  ;_    |   :  |;   |  ; \ ; |:   |   \ | : 
;   | ;    |   ' '  ; ::   |  ;/| \  \    `. \  \    `.\   ;  \ ' |'   '  ; \  \    `. '   '  ;|   :  | ; | '|   : '  '; | 
|   : |    '   |  .'. ||   :   .'  `----.   \ `----.   \    \  \: ||   |  |  `----.   \|   |  |.   |  ' ' ' :'   ' ;.    ; 
.   | '___ |   | :  | '|   |  |-,  __ \  \  | __ \  \  | ;   \  ' .'   :  ;  __ \  \  |'   :  ;'   ;  \; /  ||   | | \   | 
'   ; : .'|'   : |  : ;'   :  ;/| /  /`--'  //  /`--'  /  \   \   '|   |  ' /  /`--'  /|   |  ' \   \  ',  / '   : |  ; .' 
'   | '/  :|   | '  ,/ |   |    | --'.     /'--'.     /    \   `  ;'   :  |'--'.     / '   :  |  ;   :    /  |   | '`--'   
|   :    / ;   : ;--'  |   :   .'  `--'---'   `--'---'      :   \ |;   |.'   `--'---'  ;   |.'    \   \ .'   '   : |       
\   \ .'   |   ,/      |   | ,'                              '---" '---'               '---'       `---`     ;   |.'       
 `---`     '---'       `----'                                                                                 '---'         
                                                                                                                                
          ''')
    print('*****************************************************************************')
    args = parse_args()

    print('Loading API arguments')
    print('-----------------------------------------------------------------------------')

    piece_model = args.pieces_model
    piece_samples = args.piece_sampling
    corner_conf = args.corner_conf
    corner_iou = args.corner_iou
    pieces_conf = args.pieces_conf  
    pieces_iou = args.pieces_iou
    xoffset = args.offsetx
    yoffset = args.offsety
    stockfish_path = args.stockfish_path
    debugg = args.debug
    num_points = 10

    debug = False
    if debugg == "True":
        debug = True
        
    if piece_model not in ['large', 'nano']:
        raise ValueError(f"Invalid model: {piece_model}")
    
    print(f"Pieces are detected using: {piece_model} YOLO8 model")
    print(f"Mapping pieces to grid is done by using {piece_samples} samples")
    print('-----------------------------------------------------------------------------')
    
    corners_model_path = 'models/corners.pt'
    grid_model_path = 'models/segment_grid.pt'
    if piece_model == 'large':
        pieces_model_path = 'models/pieces_large.pt'
    if piece_model == 'nano':
        pieces_model_path = 'models/pieces_nano.pt'

    corners_model = YOLO(corners_model_path, verbose=False)
    grid_model = YOLO(grid_model_path, verbose=False)
    pieces_model = YOLO(pieces_model_path, verbose=False) 
    
    print('Models loaded')
    print('-----------------------------------------------------------------------------')
    stockfish = Stockfish(stockfish_path)

    app.run(host='0.0.0.0', port=5000, debug=True)