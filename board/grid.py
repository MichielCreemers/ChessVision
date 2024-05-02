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
    
    leftmost = tuple(contour_points[contour_points[:, 0].argmin()])
    rightmost = tuple(contour_points[contour_points[:, 0].argmax()])
    topmost = tuple(contour_points[contour_points[:, 1].argmin()])
    bottommost = tuple(contour_points[contour_points[:, 1].argmax()])
    
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