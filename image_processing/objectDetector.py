# import the necessary packages
import numpy as np
import argparse
import cv2
import time
import os
from imutils.video import VideoStream
from skimage.transform import ProjectiveTransform

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-i", "--input", type=str,
	help="path to optional input video file")
ap.add_argument("-o", "--output", type=str,
	help="path to optional output video file")
ap.add_argument("-c", "--confidence", type=float, default=0,
	help="minimum probability to filter weak detections")
ap.add_argument("-s", "--skip-frames", type=int, default=1,
	help="# of skip frames between detections")
ap.add_argument("-t", "--measure-times", action='store_true',
	help="flag for whether to measure processing time or not")
ap.add_argument("-g", "--draw-grids", action='store_true',
	help="flag for whether to draw grids, only works for second video currently")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

# if a video path was not supplied, grab a reference to the webcam
if not args.get("input", False):
	print("[INFO] starting video stream...")
	vs = VideoStream(src=0).start()
	time.sleep(2.0)
# otherwise, grab a reference to the video file
else:
	print("[INFO] opening video file...")
	vs = cv2.VideoCapture(args["input"])
# load our serialized model from disk

if args.get("draw_grids", False) and args.get("input", False):
	if os.path.abspath(args["input"]) != os.path.abspath(os.path.join("input_videos", "2.mp4")):
		sys.exit("Error, drawing grids only works for input_videos/2.mp4")


print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video writer (we'll instantiate later if need be)
writer = None

src = np.array([[0, 0], [200, 0], [0, 200], [200, 200]])
dst = np.array([[53, 269], [225, 238], [190, 318], [365, 280]])
projectiveTransform = ProjectiveTransform()
projectiveTransform.estimate(src, dst)

times = []
cellBorders = None

totalFrames = 0
while True:
	frame = vs.read()
	frame = frame[1] if args.get("input", False) else frame

	# if we are viewing a video and we did not grab a frame then we have reached the end of the video
	if args["input"] is not None and frame is None:
		break

	(h, w) = frame.shape[:2]

	# if we are supposed to be writing a video to disk, initialize the writer
	if args["output"] is not None and writer is None:
		fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
		writer = cv2.VideoWriter(args["output"], fourcc, 30, (w, h), True)

	if totalFrames % args["skip_frames"] == 0:
		start1 = time.time()
		blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
		net.setInput(blob)
		start2 = time.time()
		detections = net.forward()
		if args["measure_times"]:
			print("[INFO] Forward Propragation: {:.4f}s".format(time.time() - start2))

		# loop over the detections
		for i in np.arange(detections.shape[2]):
			# extract the confidence (i.e., probability) associated with the prediction
			confidence = detections[0, 0, i, 2]

			# filter out weak detections by ensuring the `confidence` is
			# greater than the minimum confidence
			if confidence > args["confidence"]:
				# extract the index of the class label from the `detections`,
				# then compute the (x, y)-coordinates of the bounding box for
				# the object
				idx = int(detections[0, 0, i, 1])
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")

				if CLASSES[idx] != "person":
					continue

				# Projective Transform returns location relative to (5, 11) in layout
				relativeLoc = tuple(projectiveTransform.inverse(np.array([[(startX + endX) / 2, endY - 0.05 * (endY - startY)]]))[0])
				absoluteLoc =  (5 + int(relativeLoc[0] // 200), 11 + int(relativeLoc[1] // 200))
				label = "{}: {:.2f}%, at {}".format(CLASSES[idx], confidence * 100, absoluteLoc)
				print("[INFO] {}".format(label))
				cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
				y = startY - 15 if startY - 15 > 15 else startY + 15
				cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

		if args["measure_times"]:
			times.append(time.time() - start1)
			print("[INFO] Total detection time: {:.4f}s".format(times[0-1]))


		'''
		alpha = 0.25
		overlay = frame.copy()
		cv2.line(overlay, (0, 269), (w, 269), (0, 255, 0), 2)
		cv2.line(overlay, (53, 0),  (53, h),  (0, 255, 0), 2)
		cv2.line(overlay, (0, 238), (w, 238), (255, 0, 0), 2)
		cv2.line(overlay, (225, 0), (225, h), (255, 0, 0), 2)
		cv2.line(overlay, (0, 318), (w, 318), (0, 255, 255), 2)
		cv2.line(overlay, (190, 0), (190, h), (0, 255, 255), 2)
		cv2.line(overlay, (0, 280), (w, 280), (0, 0, 255), 2)
		cv2.line(overlay, (365, 0), (365, h), (0, 0, 255), 2)
		cv2.addWeighted(overlay, alpha, frame , 1 - alpha, 0, frame)
		'''

		'''
		cv2.line(frame, tuple(dst[0]), tuple(dst[1]), (0, 255, 0), 2)		# green
		cv2.line(frame, tuple(dst[0]), tuple(dst[2]), (255, 0, 0), 2)		# blue
		cv2.line(frame, tuple(dst[2]), tuple(dst[3]), (0, 0, 255), 2)		# red
		cv2.line(frame, tuple(dst[1]), tuple(dst[3]), (0, 255, 255), 2)		# yellow
		'''

		if args["draw_grids"]:
			if cellBorders is None:
				cellBorders = []

				grid = [[-1,  0,  1, -1, -1, -1, -1,  0,  0, -1, -1, -1, -1, -1, -1,  1, -1, -1, -1,  1],
						[-1,  0,  1,  1,  1, -1, -1, -1,  0,  2,  2,  2,  2,  2,  4,  4, -1, -1, -1,  1],
						[-1,  0,  0,  0,  1,  4,  2,  2,  4,  2,  3,  3,  3,  3,  4,  2,  2,  4,  1,  1],
						[-1, -1, -1,  0,  0,  4, -1, -1,  4,  3,  3, -1, -1, -1,  3,  3,  4,  4,  2, -1],
						[-1, -1, -1, -1, -1,  2, -1, -1,  3, -1, -1, -1, -1, -1, -1, -1,  3,  3,  2,  2],
						[-1, -1, -1, -1, -1,  4,  4,  3,  3, -1, -1, -1, -1, -1, -1, -1, -1,  3,  3,  2],
						[-1, -1, -1, -1, -1,  2,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
						[-1, -1, -1, -1,  2,  2,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
						[-1, -1, -1, -1,  2,  3,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  4,  4],
						[-1, -1, -1, -1,  2,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
						[-1, -1, -1, -1,  2,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
						[ 1,  1,  1,  1,  4,  4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
						[-1, -1,  0,  0,  4,  4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
						[ 0,  0,  0, -1,  2,  3,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
						[-1, -1, -1, -1,  2,  4,  4,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  3,  2],
						[-1, -1, -1, -1,  1,  4,  2,  3,  3, -1, -1, -1, -1, -1, -1, -1, -1,  3,  3,  2],
						[-1, -1, -1, -1,  1,  0,  2,  2,  4,  3,  3,  3,  4,  3, -1, -1,  3,  3,  2,  2],
						[-1, -1, -1,  1,  1,  0, -1,  4,  4,  2,  2,  2,  4,  3,  3,  4,  3,  2,  2, -1],
						[-1,  1,  1,  1,  0,  0, -1,  1, -1, -1, -1, -1,  2,  2,  2,  4,  2,  2, -1, -1],
						[-1,  1,  0,  0,  0, -1, -1,  1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1],
						[-1,  1,  0, -1, -1, -1, -1,  1, -1, -1, -1, -1, -1, -1, -1,  0, -1, -1, -1, -1]]

				floormap = np.array(grid).transpose(1,0)

				for i, j in np.ndindex(h, w):
					relativeLoc = tuple(projectiveTransform.inverse(np.array([[j, i]]))[0])
					nearestBorder = (200 * round(relativeLoc[0] / 200), 200 * round(relativeLoc[1] / 200))
					if abs(relativeLoc[0] - nearestBorder[0]) <= 5 or abs(relativeLoc[1] - nearestBorder[1]) <= 5:
						gridLoc = (5 + int(relativeLoc[0] // 200), 11 + int(relativeLoc[1] // 200))
						if floormap[gridLoc] != -1:
							cellBorders.append((i, j))
				# print(len(cellBorders))

			for cellBorder in cellBorders:
				frame[cellBorder] = (0, 255, 255)

		cv2.imshow("Frame", frame)

		# check to see if we should write the frame to disk
		if writer is not None:
			writer.write(frame)

	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		break

	totalFrames += 1

# if we are not using a video file, stop the camera video stream
if not args.get("input", False):
	vs.stop()
# otherwise, release the video file pointer
else:
	vs.release()

# check to see if we need to release the video writer pointer
if writer is not None:
	writer.release()

if args["measure_times"]:
	print("[INFO] Average total detection time: {}".format(np.average(times)))
	print("[INFO] Total detection time std. dev: {}".format(np.std(times)))

#0.026670806407928467, 0.005443000949946635 (1.mp4)
#0.02047379522134137, 0.003309995200970159 (2.mp4)
#0.020306305544452327, 0.003701451768991102 (3.mp4)
#0.01973256479601346, 0.0029976137421987466 (4.mp4)
# average: 0.021795867992433906, 0.0038630154155266604