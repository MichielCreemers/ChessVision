import numpy as np
import cv2

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