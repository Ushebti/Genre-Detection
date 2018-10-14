# -*- coding: utf-8 -*-
import cv2 as cv
import os
import os.path
import numpy


def sort_motion_spectrum(mov, op):
	projectlist = os.listdir(op.prodir)
	answer = mov
	if answer in projectlist:
		cmovfile, cprodir, jsondict = op.open_project(answer)
		jsondict["motion"] = os.path.join(cprodir, "motion")
		jsondict["downsampled"] = os.path.join(cprodir, "downsampled")
		try:
			os.mkdir(jsondict["downsampled"])
		except OSError:
			print("downsampled folder already exists!")

	os.system(f"magick convert {os.path.join(jsondict['motion'], 'motion_*.png')} -adaptive-resize 500x500! " + jsondict["downsampled"] + "\\motion_%01d.png")
	#might not work
	os.system(f"magick convert {os.path.join(jsondict['downsampled'], 'motion_*.png')} -append {os.path.join(jsondict['downsampled'], 'result.png')}")

	img = cv.imread(os.path.join(jsondict['downsampled'], "result.png"))
	values = []

	rows, cols, depth = img.shape

	for y in range(rows):
		value = img[y, 0][0]
		values.append(value)

	values.sort(reverse=True)

	output_img = numpy.empty((rows, cols, 3), numpy.uint8)
	for y in range(rows):
		for x in range(cols):
			output_img[y, x, 0], output_img[y, x, 1], output_img[y, x, 2] = values[y], values[y], values[y]

	sorted_result = os.path.join(jsondict["motion"], "result_sorted.png")
	cv.imwrite(sorted_result, output_img)

	print(f"Sorting motion spectrum for {mov} has finished")
	return
