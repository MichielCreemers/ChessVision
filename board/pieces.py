import numpy as np
import cv2

def get_center_bottom_bb(transformation, boundingboxes):
    dimension = 640



    middles = []

    for bbox in boundingboxes:
        x, y, w, h, probs = bbox
        bottom_middle = np.array([[(x + w) / 2, y + h]], dtype=np.float32) 
        print(bottom_middle) # Reshape for perspectiveTransform
        transformed_middle = cv2.perspectiveTransform(bottom_middle.reshape(-1, 1, 2), transformation)
        middles.append(transformed_middle)

    return middles