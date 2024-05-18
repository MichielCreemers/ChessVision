import numpy as np
import cv2
import random
from ultralytics import YOLO

grid_coords = {
    'A8': [(0, 0), (80, 80)], 'B8': [(80, 0), (160, 80)], 'C8': [(160, 0), (240, 80)], 'D8': [(240, 0), (320, 80)],
    'E8': [(320, 0), (400, 80)], 'F8': [(400, 0), (480, 80)], 'G8': [(480, 0), (560, 80)], 'H8': [(560, 0), (640, 80)],
    'A7': [(0, 80), (80, 160)], 'B7': [(80, 80), (160, 160)], 'C7': [(160, 80), (240, 160)], 'D7': [(240, 80), (320, 160)],
    'E7': [(320, 80), (400, 160)], 'F7': [(400, 80), (480, 160)], 'G7': [(480, 80), (560, 160)], 'H7': [(560, 80), (640, 160)],
    'A6': [(0, 160), (80, 240)], 'B6': [(80, 160), (160, 240)], 'C6': [(160, 160), (240, 240)], 'D6': [(240, 160), (320, 240)],
    'E6': [(320, 160), (400, 240)], 'F6': [(400, 160), (480, 240)], 'G6': [(480, 160), (560, 240)], 'H6': [(560, 160), (640, 240)],
    'A5': [(0, 240), (80, 320)], 'B5': [(80, 240), (160, 320)], 'C5': [(160, 240), (240, 320)], 'D5': [(240, 240), (320, 320)],
    'E5': [(320, 240), (400, 320)], 'F5': [(400, 240), (480, 320)], 'G5': [(480, 240), (560, 320)], 'H5': [(560, 240), (640, 320)],
    'A4': [(0, 320), (80, 400)], 'B4': [(80, 320), (160, 400)], 'C4': [(160, 320), (240, 400)], 'D4': [(240, 320), (320, 400)],
    'E4': [(320, 320), (400, 400)], 'F4': [(400, 320), (480, 400)], 'G4': [(480, 320), (560, 400)], 'H4': [(560, 320), (640, 400)],
    'A3': [(0, 400), (80, 480)], 'B3': [(80, 400), (160, 480)], 'C3': [(160, 400), (240, 480)], 'D3': [(240, 400), (320, 480)],
    'E3': [(320, 400), (400, 480)], 'F3': [(400, 400), (480, 480)], 'G3': [(480, 400), (560, 480)], 'H3': [(560, 400), (640, 480)],
    'A2': [(0, 480), (80, 560)], 'B2': [(80, 480), (160, 560)], 'C2': [(160, 480), (240, 560)], 'D2': [(240, 480), (320, 560)],
    'E2': [(320, 480), (400, 560)], 'F2': [(400, 480), (480, 560)], 'G2': [(480, 480), (560, 560)], 'H2': [(560, 480), (640, 560)],
    'A1': [(0, 560), (80, 640)], 'B1': [(80, 560), (160, 640)], 'C1': [(160, 560), (240, 640)], 'D1': [(240, 560), (320, 640)],
    'E1': [(320, 560), (400, 640)], 'F1': [(400, 560), (480, 640)], 'G1': [(480, 560), (560, 640)], 'H1': [(560, 560), (640, 640)]
}

predefined_labels = ["b", "k", "n", "p", "q", "r", "B", "K", "N", "P", "Q", "R"]

def detect_pieces(model, image, confidence_threshold=0.5, iou_threshold=0.35):
    """_summary_

    Args:
        model (_type_): _description_
        image (_type_): _description_
        confidence_threshold (float, optional): _description_. Defaults to 0.7.
        iou_threshold (float, optional): _description_. Defaults to 0.35.
    """
    results = model.predict(image, conf=confidence_threshold, iou=iou_threshold)
    return results

def extract_boxes_labels(results):
    boxes = results[0].boxes.xywh.cpu().numpy()
    labels = results[0].boxes.cls.cpu().numpy()
    return boxes, labels

def xyhw_to_xyxy(box):
    """
    Somehow x and y in xywh are the center of the box (normally top left?)
    """
    x, y, w, h = box
    # Calculate top-left corner (x1, y1)
    x1 = x - w / 2
    y1 = y - h / 2
    # Calculate bottom-right corner (x2, y2)
    x2 = x + w / 2
    y2 = y + h / 2
    return [x1, y1, x2, y2] 

def sample_points_from_bbox(bbox, num_points=10, threshold=0.2):
    x1, y1, x2, y2 = bbox
    sample_points = []
    # y coordinate lowest 'threshold' % of bbox
    y_min = y2 - (y2 - y1) * threshold
    
    for _ in range(num_points):
        x = random.uniform(x1, x2)
        y = random.uniform(y_min, y2)
        sample_points.append((x, y))
    
    return sample_points

def get_sampled_points(boxes, labels, num_points=10):
    sampled_points_labels = []
    
    for box, label in zip(boxes, labels):
        bbox = xyhw_to_xyxy(box)
        points = sample_points_from_bbox(bbox, num_points)
        points = [(float(x), float(y)) for x, y in points]
        label = predefined_labels[int(label)]
        sampled_points_labels.append([points, label]) 

    return sampled_points_labels

def transform_coordinates(points, M):
    transformed_points = []
    
    for (x, y) in points:
        src = np.array([x, y, 1]).reshape((3, 1))
        dst = np.dot(M, src)
        dst = dst / dst[2]  # normalize
        transformed_points.append((dst[0][0], dst[1][0]))  # flatten
    
    return transformed_points

def map_points_to_grid(points, grid=grid_coords):
    square_counts = {square: 0 for square in grid.keys()}
    
    for point in points:
        x, y = point
        for square, ((x1, y1), (x2, y2)) in grid.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                square_counts[square] += 1
                break
    
    # Find square with most points
    max_square = max(square_counts, key=square_counts.get)
    return max_square if square_counts[max_square] > 0 else None

def get_mapped_pieces(sampled_points_labels, M):
    mapped_pieces = []
    
    for points, label in sampled_points_labels:
        transformed_points = transform_coordinates(points, M)
        mapped_square = map_points_to_grid(transformed_points)
        if mapped_square:
            mapped_pieces.append((mapped_square, label))
    
    return mapped_pieces

def create_FEN_notation(mapped_pieces):
    # Define valid rows and columns
    rows = "87654321"
    cols = "ABCDEFGH"

    # Create an 8x8 matrix initialized with empty spaces
    board = [[" " for _ in range(8)] for _ in range(8)]

    # Place each piece on the board
    for pos, piece in mapped_pieces:
        #print(f"Position: {pos}, Piece: {piece}")  # Debug output
        if len(pos) != 2 or pos[0] not in cols or pos[1] not in rows:
            raise ValueError(f"Invalid board position: {pos}")

        col = cols.index(pos[0])
        row = rows.index(pos[1])
        board[row][col] = piece

    # Convert the board to FEN notation row by row
    fen_rows = []
    for row in board:
        empty_count = 0
        fen_row = ""
        for cell in row:
            if cell == " ":
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += cell
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)

    # Join the rows into the final FEN string
    fen_string = "/".join(fen_rows)
    return fen_string

def get_center_bottom_bb(transformation, boundingboxes):
    dimension = 640
    labels = ["b", "k", "n", "p", "q", "r", "B", "K", "N", "P", "Q", "R"]


    middles = []

    for bbox in boundingboxes:
        x, y, w, h, probs = bbox
        bottom_middle = np.array([[(x + w/2), y + h]], dtype=np.float32) 
        print(bottom_middle) 
        transformed_middle = cv2.perspectiveTransform(bottom_middle.reshape(-1, 1, 2), transformation)
        max_prob_index = np.argmax(probs)
        label = labels[max_prob_index]
        entry = [tuple(np.squeeze(transformed_middle[0])), label] 
        middles.append(entry)


    return middles