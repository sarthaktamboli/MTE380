import os
import sys
import time
import argparse
from os import listdir, path

import cv2

import warnings
warnings.filterwarnings('ignore')

import io
import glob
import scipy.misc
import numpy as np
from six import BytesIO
from PIL import Image, ImageDraw, ImageFont

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    # Suppress TensorFlow logging
import tensorflow as tf
tf.get_logger().setLevel('ERROR')           # Suppress TensorFlow logging (2)

from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder


class HumanLocalizer():
	MODULE_DIR = path.dirname(path.abspath(__file__))

	def __init__(self, model_name, models_dir=None, label_map_path=None, score_thres=0.45):
		# models_dir arg validation
		if models_dir is None:
			models_dir = path.join(HumanLocalizer.MODULE_DIR, "NNs")
		if not path.exists(models_dir) or not path.isdir(models_dir):
			raise ValueError("The specified models_dir: {} does not exist, or is not a directory".format(models_dir))

		self.models_dir = models_dir

		# model_name arg validation
		models = [d for d in listdir(self.models_dir) if path.isdir(path.join(self.models_dir, d))]
		if model_name not in models:
			raise ValueError("The requested model {} does not exist! Please download to the specified models_dir".format(model_name))

		self.model_name = model_name

		# label_map_path arg validation
		if label_map_path is None:
			label_map_path = path.join(self.models_dir, 'mscoco_label_map.pbtxt')
		if not path.exists(label_map_path) or not path.isfile(label_map_path):
			raise ValueError("The specified label_map_path: {} does not exist, or is not a file".format(label_map_path))
		self.label_map_path = label_map_path


		path_to_ckpt = os.path.join(self.models_dir, self.model_name, "checkpoint", "ckpt-0")
		path_to_cfg = os.path.join(self.models_dir, self.model_name, "pipeline.config")

		#recover saved model
		self.configs = config_util.get_configs_from_pipeline_file(path_to_cfg)
		model_config = self.configs['model']
		self.detection_model = model_builder.build(model_config=model_config, is_training=False)

		# Restore checkpoint
		self.ckpt = tf.compat.v2.train.Checkpoint(model=self.detection_model)
		self.ckpt.restore(path_to_ckpt)

		# load map labels for inference decoding
		label_map = label_map_util.load_labelmap(self.label_map_path)
		categories = label_map_util.convert_label_map_to_categories(
			label_map,
			max_num_classes=label_map_util.get_max_label_map_index(label_map),
			use_display_name=True)
		self.category_index = label_map_util.create_category_index(categories)

		for k, v in self.category_index.items():
			if v['name'] == 'person':
				self.person_category_index = v['id']
		self.label_id_offset = 1

		self.detect_fn = self.get_model_detection_function(self.detection_model)

		self.score_thres = score_thres

	def __del__(self):
		cv2.destroyAllWindows()

	@staticmethod
	def get_model_detection_function(model):
		"""Get a tf.function for detection."""

		@tf.function
		def detect_fn(image):
			"""Detect objects in image."""

			image, shapes = model.preprocess(image)
			prediction_dict = model.predict(image, shapes)
			detections = model.postprocess(prediction_dict, shapes)

			return detections, prediction_dict, tf.reshape(shapes, [-1])

		return detect_fn

	def _get_np_image(self):
		raise NotImplementedError("Subclass should implement this")

	def _cv_waitkey(self):
		cv2.waitKey()
		return True

	def infer(self, visualize=False):
		start_time = time.time()

		image_np = self._get_np_image()
		print("1, Time: {}".format(time.time()-start_time))

		if image_np is None:
			return None

		# very fast operation
		input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)

		# slow on first inference
		detections, prediction_dict, shape = self.detect_fn(input_tensor)

		print("2, Time: {}".format(time.time()-start_time)) 

		boxes = []
		detection_boxes = detections['detection_boxes'][0].numpy()
		detection_scores = detections['detection_scores'][0].numpy()
		detection_classes = detections['detection_classes'][0].numpy()

		for i in range(detections['detection_boxes'].shape[1]):
			if detection_scores[i] > self.score_thres:
				if detection_classes[i] == self.person_category_index - self.label_id_offset:
					boxes.append(detection_boxes[i])

		print("3, Time: {}".format(time.time()-start_time))

		if visualize:
			image_np_with_detections = image_np.copy()
			
			viz_utils.visualize_boxes_and_labels_on_image_array(
				image_np_with_detections,
				detections['detection_boxes'][0].numpy(),
				(detections['detection_classes'][0].numpy() + self.label_id_offset).astype(int),
				detections['detection_scores'][0].numpy(),
				self.category_index,
				use_normalized_coordinates=True,
				max_boxes_to_draw=20,
				min_score_thresh=.30,
				agnostic_mode=False)

			cv2.imshow('object detection', cv2.resize(image_np_with_detections, (450, 300)))

			print("4, Time: {}".format(time.time()-start_time))

			if not self._cv_waitkey():
				return None

		# list of bounding boxes, each element is a np array with 4 elements: ymin, xmin, ymax, xmax
		# the values are normalized to the image:
		# (left, right, top, bottom) = (xmin * im_width, xmax * im_width, 
		#                               ymin * im_height, ymax * im_height)
		return boxes

	def stream(self):
		while True:
			ret = self.infer(visualize=True)
			if ret is None:
				break


class StreamHumanLocalizer(HumanLocalizer):
	def __init__(self, *args, video_stream=None, **kwargs):

		super().__init__(*args, **kwargs)

		if video_stream is None:
			video_stream = cv2.VideoCapture(0)

		self.video_stream = video_stream

	def __del__(self):
		self.video_stream.release()

	def _get_np_image(self):
		ret, image_np = self.video_stream.read()
		return image_np

	def _cv_waitkey(self):
		if cv2.waitKey(25) & 0xFF == ord('q'):
			return False


class ImageHumanLocalizer(HumanLocalizer):
	def __init__(self, *args, images_dir=None, **kwargs):

		super().__init__(*args, **kwargs)

		# models_dir arg validation
		if images_dir is None:
			images_dir = path.join(HumanLocalizer.MODULE_DIR, "images")
		if not path.exists(images_dir) or not path.isdir(images_dir):
			raise ValueError("The specified images_dir: {} does not exist, or is not a directory".format(images_dir))
		
		self.images = [path.join(images_dir, f) for f in listdir(images_dir) if path.join(images_dir, f).lower().endswith(('.png', '.jpg', '.jpeg'))]

		self.curr_image_idx = 0

	def _get_np_image(self):
		# Load an image from file into a numpy array.
		# Puts image into numpy array to feed into tensorflow graph.
		# Note that by convention we put it into a numpy array with shape
		# (height, width, channels), where channels=3 for RGB.

		if self.curr_image_idx >= len(self.images):
			return None

		image_path = self.images[self.curr_image_idx]
		self.curr_image_idx += 1

		img_data = tf.io.gfile.GFile(image_path, 'rb').read()
		image = Image.open(BytesIO(img_data))
		(im_width, im_height) = image.size

		# uint8 numpy array with shape (img_height, img_width, 3)
		return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


def main(args):
	model_name = args.model_name
	
	shl = ImageHumanLocalizer(model_name)
	shl.stream()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--models_dir", help="Directory where NN models are stored", 
		type=str, default="NNs")
	parser.add_argument("--image_dir", help="Directory where images to be prpcessed are stored", 
		type=str, default="images")
	LABEL_FILENAME = 'mscoco_label_map.pbtxt'
	#parser.add_argument("--label_map", help="Path to the label map file", 
	#	type=str, default=path.join("models", "research", "object_detection", "data", LABEL_FILENAME))
	parser.add_argument("--label_map", help="Path to the label map file", 
		type=str, default=path.join("NNs", LABEL_FILENAME))
	
	parser.add_argument("--model_name", help="Name of NN model to use", 
		type=str, default="ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8") # centernet_resnet50_v1_fpn_512x512_coco17_tpu-8
	args = parser.parse_args()

	main(args)
