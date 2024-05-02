import ultralytics
from ultralytics import YOLO
import os
import math
from PIL import Image
import cv2
from IPython.display import Video
import glob
import matplotlib.pyplot as plt
import numpy as np

import corners as corners

import warnings
warnings.filterwarnings("ignore")


def make_projection(img_dir, projections_dir):
    
    if not os.path.exists(projections_dir):
        os.makedirs(projections_dir)
    
    
    for filename in os.listdir(img_dir):
        if filename.endswith(".jpg"):
            image_path = os.path.join(img_dir, filename)
            save_path = os.path.join(projections_dir, filename)
            results = corners.predict_corners(corners_model, image_path, confidence_threshold=0.25, iou_threshold=0.1)

            sorted_corners = corners.get_sorted_corner_coordinates(results)
            print("Number of corners found: ", len(sorted_corners))
            if len(sorted_corners) != 4:
                print("Skipping image: ", image_path)
                continue
            labeled_corners, sorted_corners = corners.label_and_sort_corners(sorted_corners)
            sorted_corners = corners.add_offset(sorted_corners, offsetx=300, offsety=300)

            image = cv2.imread(image_path)
            corners1 = np.array(sorted_corners, dtype="float32")
            
            dimension = 640
            dst = np.array([
                [0, 0],
                [dimension - 1, 0],
                [dimension - 1, dimension - 1],
                [0, dimension - 1]
            ], dtype="float32")
            
            M = cv2.getPerspectiveTransform(corners1, dst)
            warped = cv2.warpPerspective(image, M, (dimension, dimension))
            
            cv2.imwrite(save_path, warped)
            
if __name__ == "__main__":
    corners_model = YOLO('models/corners.pt')
    img_dir = "images/dataset"
    projections_dir = "images/projections"
    make_projection(img_dir, projections_dir)