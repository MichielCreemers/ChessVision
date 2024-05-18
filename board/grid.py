from ultralytics import YOLO
import cv2
import numpy as np

def predict_grid_segmentation(model, image_path, conf=0.1, iou=0.2):
    
    results = model.predict(image_path, conf=conf, iou=iou)
    return results

def sort_corners(corners):
    # Sort based on their x-coordinates
    corners = sorted(corners, key=lambda x: x[0])
    
    # Separate them into leftmost and rightmost
    left_most = corners[:2]
    right_most = corners[2:]

    # Within each pair, sort them by y-coordinate to separate top from bottom
    left_most = sorted(left_most, key=lambda x: x[1])
    right_most = sorted(right_most, key=lambda x: x[1])

    # The coordinates are now sorted in the following order:
    # top-left, bottom-left, top-right, bottom-right
    sorted_corners = np.array([left_most[0], right_most[0], right_most[1], left_most[1]])

    return sorted_corners

def get_corners_from_grid_segmentation(prediction_result):
    
    # Access the segmentation mask from the prediction result
    masks = prediction_result[0].masks
    contour_points = masks.xy[0]
    contour_points = np.array(contour_points)
    
    # leftmost = tuple(contour_points[contour_points[:, 0].argmin()])
    # rightmost = tuple(contour_points[contour_points[:, 0].argmax()])
    # topmost = tuple(contour_points[contour_points[:, 1].argmin()])
    # bottommost = tuple(contour_points[contour_points[:, 1].argmax()])
    
    # Use OpenCV to approximate the contour to a polygon
    epsilon = 0.1 * cv2.arcLength(contour_points, True)
    approx_corners = cv2.approxPolyDP(contour_points, epsilon, True)
    
    if len(approx_corners) == 4:
        approx_corners = approx_corners.reshape((4, 2))
        # Sort the corners into the order you need for perspective transformation
        sorted_corners = sort_corners(approx_corners)
    else:
        raise Exception("Couldn't approximate a quadrilateral. Check the segmentation.")
    
    return sorted_corners

def make_perspective_transform(image, corners):
    
    corners = np.array(corners, dtype="float32")
    dimension = 640
    
    dst = np.array([
        [0, 0],
        [dimension - 1, 0],
        [dimension - 1, dimension - 1],
        [0, dimension - 1]
    ], dtype="float32")
    
    M = cv2.getPerspectiveTransform(corners, dst)
    warped = cv2.warpPerspective(image, M, (dimension, dimension))
    
    return warped, M

def correct_orientation(image):
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, w = img_hsv.shape[:2]

    sample_size = 20  # Adjusted for more targeted sampling
    num_samples = 5   # Reduced for efficiency

    def average_hue_saturation(image, x, y, size, num_samples):
        hues = []
        sats = []
        for _ in range(num_samples):
            sx = np.random.randint(x, x + size)
            sy = np.random.randint(y, y + size)
            hue = image[sy, sx, 0]
            sat = image[sy, sx, 1]
            hues.append(hue)
            sats.append(sat)
        return np.mean(hues), np.mean(sats)

    # Sample each corner
    bl_hue, bl_sat = average_hue_saturation(img_hsv, 0, h - sample_size, sample_size, num_samples)
    br_hue, br_sat = average_hue_saturation(img_hsv, w - sample_size, h - sample_size, sample_size, num_samples)
    tl_hue, tl_sat = average_hue_saturation(img_hsv, 0, 0, sample_size, num_samples)
    tr_hue, tr_sat = average_hue_saturation(img_hsv, w - sample_size, 0, sample_size, num_samples)

    # Define thresholds for black and white detection 
    black_threshold = (180, 255)  
    white_threshold = (0, 50)     

    # Black and white condition checks
    black_condition = lambda sat: sat <= black_threshold[1]
    white_condition = lambda sat: sat <= white_threshold[1]

    # Check if the orientation is correct based on corner color conditions
    if (black_condition(bl_sat) and white_condition(br_sat) and
        white_condition(tl_sat) and black_condition(tr_sat)):
        return False  # No rotation needed
    else:
        return True   # Rotation needed
    
def correct_orientation_advanced(image):
    
    # Convert to Lab color space
    img_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    h, w = img_lab.shape[:2]
    outer_size = 640 // 8
    border_width = 10
    num_samples = 10
    
    def sample_border_lab_channels(img, x, y, outer_size, border_width, num_samples, channel_idx):
        values = []
        for _ in range(num_samples):
            # Randomly choose between horizontal and vertical border strips
            if np.random.rand() > 0.5:
                # Horizontal border strip (top or bottom)
                sx = np.random.randint(x, x + outer_size)
                sy = np.random.choice([np.random.randint(y, y + border_width), 
                                        np.random.randint(y + outer_size - border_width, y + outer_size)])
            else:
                # Vertical border strip (left or right)
                sx = np.random.choice([np.random.randint(x, x + border_width), 
                                        np.random.randint(x + outer_size - border_width, x + outer_size)])
                sy = np.random.randint(y, y + outer_size)
            values.append(img[sy, sx, channel_idx])
        return np.mean(values)

    # Sample L and b values in each corner
    # Bottom-left corner
    bl_L = sample_border_lab_channels(img_lab, 0, h - outer_size, outer_size, border_width, num_samples, 0)  # L channel
    bl_b = sample_border_lab_channels(img_lab, 0, h - outer_size, outer_size, border_width, num_samples, 2)  # b channel
    
    # Bottom-right corner
    br_L = sample_border_lab_channels(img_lab, w - outer_size, h - outer_size, outer_size, border_width, num_samples, 0)  # L channel
    br_b = sample_border_lab_channels(img_lab, w - outer_size, h - outer_size, outer_size, border_width, num_samples, 2)  # b channel
    
    # Top-left corner
    tl_L = sample_border_lab_channels(img_lab, 0, 0, outer_size, border_width, num_samples, 0)  # L channel
    tl_b = sample_border_lab_channels(img_lab, 0, 0, outer_size, border_width, num_samples, 2)  # b channel
    
    # Top-right corner
    tr_L = sample_border_lab_channels(img_lab, w - outer_size, 0, outer_size, border_width, num_samples, 0)  # L channel
    tr_b = sample_border_lab_channels(img_lab, w - outer_size, 0, outer_size, border_width, num_samples, 2)  # b channel
    
    # Define thresholds for black and white detection
    L_threshold = 100
    b_threshold = 140
    
    # print("BL_L: ", bl_L)
    # print("BL_b: ", bl_b)
    # print("BR_L: ", br_L)
    # print("BR_b: ", br_b)
    # print("TL_L: ", tl_L)
    # print("TL_b: ", tl_b)
    # print("TR_L: ", tr_L)
    # print("TR_b: ", tr_b)
    
    # Black and white condition checks
    correct = (bl_L < L_threshold or bl_b < b_threshold) and (br_L > L_threshold or br_b > b_threshold)

    # ...        
    
    if correct:
        return False  # No rotation needed
    else:
        return True   # Rotation needed
    
def map_grid_to_coordinates(image):
    
    h, w = image.shape[:2]
    grid_size = 8
    square_width = w // grid_size
    square_height = h // grid_size
    
    grid_coordinates = {}
    # labels --> [A8, B8, C8, D8, E8, F8, G8, H8, A7, B7, C7, D7, E7, F7, G7, H7, ...]
    labels = [f"{chr(65 + col)}{8 - row}" for row in range(grid_size) for col in range(grid_size)]  
    idx = 0
    
    for row in range(grid_size):
        for col in range(grid_size):
            x1 = col * square_width
            y1 = row * square_height
            x2 = x1 + square_width
            y2 = y1 + square_height
            grid_coordinates[labels[idx]] = [(x1, y1), (x2, y2)]
            idx += 1
    
    return grid_coordinates

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


def place_pieces_on_board(board, pieces, grid_coords=grid_coords):
    """
    Place each detected piece on the board based on their coordinates.

    :param board: 2D list representing the chessboard
    :param pieces: List of tuples containing piece center coordinates and piece type [(x, y), 'piece']
    :param grid_coords: Dictionary mapping square names to their coordinate ranges
    """
    
    def find_square(x, y, grid_coords):
        """
        Find the corresponding square for the given coordinates.

        :param x: X coordinate
        :param y: Y coordinate
        :param grid_coords: Dictionary mapping square names to their coordinate ranges
        :return: Square name (e.g., 'A8') if found, else None
        """
        for square, ((x1, y1), (x2, y2)) in grid_coords.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                return square
        return None
    
    for (x, y), piece in pieces:
        square = find_square(x, y, grid_coords)
        if square:
            row = 8 - int(square[1])  # Convert rank to row index (0-7)
            col = ord(square[0]) - ord('A')  # Convert file to column index (0-7)
            board[row][col] = piece
    
def generate_fen(board):
    fen = ''
    for row in board:
        empty_count = 0
        for cell in row:
            if cell == '':
                empty_count += 1
            else:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                fen += cell
        if empty_count > 0:
            fen += str(empty_count)
        fen += '/'
    return fen.rstrip('/')
    
    
    
