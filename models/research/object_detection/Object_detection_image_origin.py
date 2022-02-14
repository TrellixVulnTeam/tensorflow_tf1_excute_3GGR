######## Image Object Detection Using Tensorflow-trained Classifier #########
#
# Author: Evan Juras
# Date: 1/15/18
# Description: 
# This program uses a TensorFlow-trained neural network to perform object detection.
# It loads the classifier and uses it to perform object detection on an image.
# It draws boxes, scores, and labels around the objects of interest in the image.

## Some of the code is copied from Google's example at
## https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb

## and some is copied from Dat Tran's example at
## https://github.com/datitran/object_detector_app/blob/master/object_detection_app.py

## but I changed it to make it more understandable to me.

# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import sys
import time
import pathlib
import glob

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'inference_graph'
IMAGE_NAME = '1619166772997.5747.bmp'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'training','scratch_map.pbtxt')

# Path to image
PATH_TO_IMAGE = os.path.join(CWD_PATH,IMAGE_NAME)

# Number of classes the object detector can identify
NUM_CLASSES = 3

# Load the label map.
# Label maps map indices to category names, so that when our convolution
# network predicts `5`, we know that this corresponds to `king`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

# Define input and output tensors (i.e. data) for the object detection classifier

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Load image using OpenCV and
# expand image dimensions to have shape: [1, None, None, 3]
# i.e. a single-column array, where each item in the column has the pixel RGB value
# image = cv2.imread(PATH_TO_IMAGE)
# image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# PATH_TO_TEST_IMAGES_DIR = pathlib.Path('test_images')
TEST_IMAGE_PATHS = glob.glob("C:\\Users\\admin\\Desktop\\save_images\\*.bmp")
TEST_IMAGE_PATHS += glob.glob("C:\\Users\\admin\\Desktop\\save_images\\*.jpg")
TEST_IMAGE_PATHS += glob.glob("C:\\Users\\admin\\Desktop\\save_images\\*.png")
# TEST_IMAGE_PATHS = glob.glob("images/test/*.bmp")
# TEST_IMAGE_PATHS += glob.glob("images/test/*.jpg")
# TEST_IMAGE_PATHS += glob.glob("images/test/*.png")
# TEST_IMAGE_PATHS += glob.glob("images/train/*.png")
# TEST_IMAGE_PATHS += glob.glob("images/train/*.jpg")
# TEST_IMAGE_PATHS += glob.glob("images/train/*.bmp")
# TEST_IMAGE_PATHS += glob.glob("images/DDK_Station1_27052021/train/*.jpg")
# TEST_IMAGE_PATHS += glob.glob("images/DDK_Station1_27052021/train/*.png")

# TEST_IMAGE_PATHS = glob.glob("images/valid/*.png")
# TEST_IMAGE_PATHS += glob.glob("images/valid/*.jpg")
# TEST_IMAGE_PATHS += glob.glob("images/valid/*.bmp")

# TEST_IMAGE_PATHS = list(PATH_TO_TEST_IMAGES_DIR.glob("*.bmp"))
# TEST_IMAGE_PATHS += list(PATH_TO_TEST_IMAGES_DIR.glob("*.bmp"))
TEST_IMAGE_PATHS = sorted(TEST_IMAGE_PATHS)

def get_valid_boxes(boxes, scores,image, min_score_thresh=0.5):
    im_width = image.shape[1]
    im_height = image.shape[0]
    valid_boxes = []
    for i in range(boxes.shape[0]):
        if scores is None or scores[i] > min_score_thresh:
            ymin, xmin, ymax, xmax = tuple(boxes[i].tolist())

            valid_box = (int(xmin * im_width), int(ymin * im_height),
                                                int(xmax * im_width), int(ymax * im_height))

            valid_boxes.append(valid_box)

    return valid_boxes
while True:
    for image_path in TEST_IMAGE_PATHS:
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        _time = time.time()
        image_expanded = np.expand_dims(image_rgb, axis=0)
        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: image_expanded})

        # Draw the results of the detection (aka 'visulaize the results')
        valid_boxes = get_valid_boxes(np.squeeze(boxes), np.squeeze(scores), image, min_score_thresh=0.35)
        for (start_x, start_y, end_x, end_y) in valid_boxes:
            cv2.rectangle(image, pt1=(start_x, start_y), pt2=(end_x, end_y), color=(0, 255, 0), thickness=4,
                          lineType=cv2.LINE_AA)
        # vis_util.visualize_boxes_and_labels_on_image_array(
        #     image,
        #     np.squeeze(boxes),
        #     np.squeeze(classes).astype(np.int32),
        #     np.squeeze(scores),
        #     category_index,
        #     use_normalized_coordinates=True,
        #     line_thickness=20,
        #     min_score_thresh=0.5)
        print(f"time draw: {time.time() - _time}")
        # All the results have been drawn on image. Now display the image.
        image = cv2.resize(image, dsize=(800, 600))
        cv2.imshow('Object detector', image)

    # Press any key to close the image
        wk = cv2.waitKey(100)
        if wk & 0xFF == ord("q"):
            break
    if wk & 0xFF == ord("q"):
        break


# Clean up
cv2.destroyAllWindows()