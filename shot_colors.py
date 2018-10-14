# -*- coding: utf-8 -*-
import cv2 as cv
import numpy
import scipy.cluster
import os.path
import math
import functools
import os
from lib import hls_sort2


def shot_colors(mov, op):
	NUM_CLUSTERS = 5
	PIXELS_PER_COLOR = 20
	EVERY_NTH_FRAME = 5

	projectlist = os.listdir(op.prodir)
	answer = mov
	if answer in projectlist:
		cmovfile, cprodir, jsondict = op.open_project(answer)
		jsondict["shot_colors"] = os.path.join(cprodir, "shot_colors")
		os.mkdir(jsondict["shot_colors"])

		cap = cv.VideoCapture()
		cap.open(cmovfile)

		if not cap.isOpened():
			print(f"Fatal error - could not parse video {answer}")

		width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
		height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
		new_width = int(width / 4)
		new_height = int(height / 4)
		px_count = new_width * new_height

	# skip frames in the beginning, if neccessary
	start_frame = int(jsondict["start_frame"])
	cap.set(cv.CAP_PROP_POS_FRAMES, start_frame) #start_frame

	with open(os.path.join(cprodir, "snapshots/shots.txt"), "r") as f:
		scene_durations = [int(values[2]) for values in [line.split("\t") for line in f if line]]

	for scene_nr, duration in enumerate(scene_durations):
		h = int(math.ceil(float(duration) / EVERY_NTH_FRAME))
		OUT_IMG = numpy.empty((h, PIXELS_PER_COLOR * NUM_CLUSTERS, 3), numpy.uint8)
		frame_counter = 0

		for i in range(duration):

			(rv, img_orig) = cap.read()

			if not rv:
				break

			if i % EVERY_NTH_FRAME != 0:
				continue

			img = cv.resize(img_orig, (0, 0), fx=0.25, fy=0.25, interpolation=cv.INTER_AREA)

			img = cv.cvtColor(img, cv.COLOR_BGR2HLS)

			img = img.reshape(img.shape[0] * img.shape[1], img.shape[2])  # make it 1-dimensional

			# set initial centroids
			init_cluster = []
			for y in [int(new_height / 4.0), int(new_height * 3 / 4.0)]:
				for x in [int(new_width * f) for f in [0.25, 0.75]]:
					init_cluster.append(img[y * new_width + x])
			init_cluster.insert(2, img[int(new_height / 2.0) * new_width + int(new_width / 2.0)])
			img = img.astype(float)

			init_cluster = numpy.asarray(init_cluster)

			centroids, labels = scipy.cluster.vq.kmeans2(img, init_cluster)

			vecs, dist = scipy.cluster.vq.vq(img, centroids)  # assign codes
			counts, bins = scipy.histogram(vecs, len(centroids))  # count occurrences
			centroid_count = []
			for i, count in enumerate(counts):
				if count > 0:
					centroid_count.append((centroids[i].tolist(), count))

			centroid_count.sort(key=functools.cmp_to_key(hls_sort2))

			x = 0
			for item in centroid_count:
				count = item[1] * (PIXELS_PER_COLOR * NUM_CLUSTERS)
				count = int(math.ceil(count / float(px_count)))
				centroid = item[0]
				for l in range(count):
					xl = x + l
					if x + l >= PIXELS_PER_COLOR * NUM_CLUSTERS:
						break
					OUT_IMG[frame_counter, xl, 0], OUT_IMG[frame_counter, xl, 1], OUT_IMG[frame_counter, xl, 2] = centroid[0], centroid[1], centroid[2]
				x += count

			frame_counter += 1

			cv.imwrite(os.path.join(jsondict["shot_colors"], f"preconv_{scene_nr}.png"), OUT_IMG)
			img_conv = cv.imread(os.path.join(jsondict["shot_colors"], f"preconv_{scene_nr}.png"), cv.IMREAD_COLOR)
			img_conv = cv.cvtColor(img_conv, cv.COLOR_HLS2BGR)
			cv.imwrite(os.path.join(jsondict["shot_colors"], f"shot_colors_{scene_nr}.png"), img_conv)

	print(f"processing shot colors for {mov} has finished.")

	return
