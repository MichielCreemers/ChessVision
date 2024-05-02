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
        print("gets here")
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
    
    return warped

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
    
    print("BL_L: ", bl_L)
    print("BL_b: ", bl_b)
    print("BR_L: ", br_L)
    print("BR_b: ", br_b)
    print("TL_L: ", tl_L)
    print("TL_b: ", tl_b)
    print("TR_L: ", tr_L)
    print("TR_b: ", tr_b)
    
    # Black and white condition checks
    correct = (bl_L < L_threshold or bl_b < b_threshold) and (br_L > L_threshold or br_b > b_threshold)

                
    
    if correct:
        return False  # No rotation needed
    else:
        return True   # Rotation needed