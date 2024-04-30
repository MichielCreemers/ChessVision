from ultralytics import YOLO
import numpy as np
import math

def predict_corners(model, image_path, confidence_threshold=0.1, iou_threshold=0.2):
    """The function predicts the corners of the board in the image.

    Args:
        model (_type_): YOLO model trained to detect the corners of the board.
        image_path (str): Path to the image.
        confidence_threshold (float): Confidence threshold for the model.
        iou_threshold (float): Intersection over union threshold for the model.
    """
    results = model.predict(image_path, conf=confidence_threshold, iou=iou_threshold)
    
    # boxes = results[0].boxes
    # all_boxes = boxes.xywh
    # # all_boxes = all_boxes.cpu().numpy()

    return results

def box_coordinates(corners):
    """Returns the coordinates for each corner bounding box as:
    top-left x, top-left y, width, height

    Args:
        corners: Output object after prediction
    """
    boxes = corners[0].boxes
    all_boxes = boxes.xywh
    
    return all_boxes.cpu().numpy()

def get_sorted_corner_coordinates(corners, offsetx=0, offsety=0):
    """_summary_

    Args:
        corners (_type_): _description_
        offsetx (int, optional): _description_. Defaults to 0.
        offsety (int, optional): _description_. Defaults to 0.
    """
    all_boxes = box_coordinates(corners)
    corner_coordinates = []
    for box in all_boxes:
        x, y, w, h = box
        top_left = (x, y)
        top_right = (x + w, y)
        bottom_left = (x, y - h)
        bottom_right = (x + w, y - h)
        center = (x + w/2, y - h/2)
        corner_coordinates.append((top_left, top_right, bottom_left, bottom_right, center))
    
    def add_ofset(corners):
        corners[0] = (corners[0][0] - offsetx, corners[0][1] - offsety)
        corners[1] = (corners[1][0] + offsetx, corners[1][1] - offsety)
        corners[2] = (corners[2][0] + offsetx, corners[2][1] + offsety)
        corners[3] = (corners[3][0] - offsetx, corners[3][1] + offsety)
        return corners
    
    def leftmost_point(points):
        leftmost_point = points[0]
        for point in points[1:]:
            if point[0][0] < leftmost_point[0][0]:
                leftmost_point = point
        return leftmost_point
    
    def calculate_angle(start, point):
        return math.atan2(point[0][1] - start[0][1], point[0][0] - start[0][0])
    
    def get_polygon_order(leftmost_point, points):
        points_with_angle = []
        for point in points:
            angle = calculate_angle(leftmost_point, point)
            if angle != 0:
                angle = angle + math.pi/2
            points_with_angle.append((point, angle))
            
        sorted_points_with_angle = sorted(points_with_angle, key=lambda x: x[1])
        sorted_points = []
        i = 0
        for point in sorted_points_with_angle:
            sorted_points.append(point[0][i])
            i += 1
        
        return sorted_points
    
    leftmost = leftmost_point(corner_coordinates)
    sorted_corners = get_polygon_order(leftmost, corner_coordinates)
    
    # Add offset
    #sorted_corners = add_ofset(sorted_corners)
    
    return sorted_corners