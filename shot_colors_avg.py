# -*- coding: utf-8 -*-
import cv2 as cv
import numpy
import scipy.cluster
import os.path
import os
import math
import functools
from lib import hls_sort2


def shot_colors_avg(mov, op):
	NUM_CLUSTERS = 5
	PIXELS_PER_COLOR = 40

	projectlist = os.listdir(op.prodir)
	answer = mov
	if answer in projectlist:
		cmovfile, cprodir, jsondict = op.open_project(answer)
		jsondict["shot_colors"] = os.path.join(cprodir, "shot_colors")
		print(jsondict["shot_colors"])

	for file in os.listdir(jsondict["shot_colors"]):
		if os.path.isdir(file):
			continue

		img_orig = cv.imread(os.path.join(jsondict["shot_colors"], file), cv.IMREAD_COLOR)
		w, h = img_orig.shape[1], img_orig.shape[0]

		img_hls = cv.cvtColor(img_orig, cv.COLOR_BGR2HLS)

		output_img = numpy.empty((h, PIXELS_PER_COLOR * NUM_CLUSTERS, 3), numpy.uint8)  # numpy.empty((height, width, depth), dtype)

		# make it 1-dimensional
		img = img_hls.reshape(img_hls.shape[0] * img_hls.shape[1], img_hls.shape[2])

		# set initial centroids
		init_cluster = []
		step = w / NUM_CLUSTERS
		for x, y in [(0*step, h*0.1), (1*step, h*0.3), (2*step, h*0.5), (3*step, h*0.7), (4*step, h*0.9)]:
			x = int(x)
			y = int(y)
			init_cluster.append(img[y * w + x])

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

		px_count = w * h
		x = 0
		for item in centroid_count:
			count = item[1] * (PIXELS_PER_COLOR * NUM_CLUSTERS)
			count = int(math.ceil(count / float(px_count)))
			centroid = item[0]
			for length in range(count):
				xl = x + length
				if x + length >= PIXELS_PER_COLOR * NUM_CLUSTERS:
					break
				for y in range(h):
					output_img[y, xl, 0], output_img[y, xl, 1], output_img[y, xl, 2] = centroid[0], centroid[1], centroid[2]
			x += count

		filename = file

		cv.imwrite(os.path.join(jsondict["shot_colors"], f"preconv_{filename}"), output_img)
		img_conv = cv.imread(os.path.join(jsondict["shot_colors"], f"preconv_{filename}"), cv.IMREAD_COLOR)
		img_conv = cv.cvtColor(img_conv, cv.COLOR_HLS2BGR)

		cv.imwrite(os.path.join(jsondict["shot_colors"], filename), img_conv)

	#this might not work
	print(f"processing shot colors average for {mov} has finished")
	os.system(f"magick convert {os.path.join(jsondict['shot_colors'], 'shot_colors_*.png')} -append {os.path.join(jsondict['shot_colors'], 'result.png')}")

	return
