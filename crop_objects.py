import os
import time
import argparse
import multiprocessing
import numpy as np
import tensorflow as tf
import cv2

# from utils.app_utils import FPS, WebcamVideoStream
from multiprocessing import Queue, Pool
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
import numpy as np
from PIL import Image

CWD_PATH = os.getcwd()

# Path to frozen detection graph. This is the actual model that is used for the object detection.
MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
PATH_TO_CKPT = os.path.join(CWD_PATH, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(CWD_PATH, 'object_detection', 'data', 'mscoco_label_map.pbtxt')

IMAGE_SIZE = (12, 8)
NUM_CLASSES = 90
OUTPUT_PATH = './output/'

# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
			use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def load_image_into_numpy_array(image):
	im_width, im_height = image.size
	return np.array(image.getdata()).reshape(
		(im_height, im_width, 3)).astype(np.uint8)

def crop_rectangle(img_path, save_path, idx, x_min, x_max, y_min, y_max):
	# check if img_path is valid file
	if not os.path.exists(img_path):
		print('Invalid image path specified')
		sys.exit(1)
	# check if save_path is valid directory
	if not os.path.isdir(save_path):
		print('Invalid save path specified')
		sys.exit(1)
	img = cv2.imread(img_path)
	crop_img = img[y_min:y_max, x_min:x_max]
	b_idx = img_path.rfind('/')
	base_name = ''
	if b_idx == -1:
		base_name = img_path[:-4]
	else:
		base_name = img_path[b_idx+1:-4]
	crop_name = str(idx) + '.jpg'
	cv2.imwrite(os.path.join(save_path, crop_name), crop_img)

def crop_objects(image_path):
	detection_graph = tf.Graph()
	with detection_graph.as_default():
		od_graph_def = tf.GraphDef()
		with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
			serialized_graph = fid.read()
			od_graph_def.ParseFromString(serialized_graph)
			tf.import_graph_def(od_graph_def, name='')

		sess = tf.Session(graph=detection_graph)
	image = Image.open(image_path)
	width, height = image.size
	image_np = load_image_into_numpy_array(image)
	# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
	image_np_expanded = np.expand_dims(image_np, axis=0)
	image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

	# Each box represents a part of the image where a particular object was detected.
	boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

	# Each score represent how level of confidence for each of the objects.
	# Score is shown on the result image, together with the class label.
	scores = detection_graph.get_tensor_by_name('detection_scores:0')
	classes = detection_graph.get_tensor_by_name('detection_classes:0')
	num_detections = detection_graph.get_tensor_by_name('num_detections:0')

	# Actual detection.
	(boxes, scores, classes, num_detections) = sess.run(
		[boxes, scores, classes, num_detections],
		feed_dict={image_tensor: image_np_expanded})

	# vis_util.visualize_boxes_and_labels_on_image_array(
	# 	image_np,
	# 	np.squeeze(boxes),
	# 	np.squeeze(classes).astype(np.int32),
	# 	np.squeeze(scores),
	# 	category_index,
	# 	use_normalized_coordinates=True,
	# 	line_thickness=8)
	idx = 0
	for root, dirs, files in os.walk(OUTPUT_PATH):
		for name in files:
			os.remove(os.path.join(root, name))
	with open("input.txt", "a") as f:
		f.truncate(0)
		first = True
		for index,value in enumerate(classes[0]):
			if scores[0,index] > 0.05 and category_index.get(value)['name'] == 'book':
				
				# Book object
				ymin = int(boxes[0][index][0] * height)
				xmin = int(boxes[0][index][1] * width)
				ymax = int(boxes[0][index][2] * height)
				xmax = int(boxes[0][index][3] * width)
				print([ymin, ymax, xmin, xmax])
				if (ymax-ymin) >= 2.25 * (xmax - xmin) or (ymax-ymin) <= (xmax - xmin):
					continue
				crop_rectangle(image_path, OUTPUT_PATH , idx, xmin, xmax, ymin, ymax)
				if first:
					f.write("output/{}.jpg 0".format(idx))
					first = False
				else: 
					f.write("\noutput/{}.jpg 0".format(idx))
				idx += 1
	tf.reset_default_graph()


