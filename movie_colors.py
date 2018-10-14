# -*- coding: utf-8 -*-
import cv2 as cv
import os
import os.path
import numpy
import math
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


def difference(a, b):  # HLS
	c1 = sRGBColor(a[0], a[1], a[2])
	c2 = sRGBColor(b[0], b[1], b[2])

	c1 = convert_color(c1, LabColor)
	c2 = convert_color(c2, LabColor)

	delta_e = delta_e_cie2000(c1, c2)

	return delta_e


def sort_by_distance(colors):
	# Find the darkest color in the list.
	root = colors[0]
	for color in colors[1:]:
		if color[1] < root[1]:  # length
			root = color

	# Remove the darkest color from the stack,
	# put it in the sorted list as starting element.
	stack = [color for color in colors]
	stack.remove(root)
	sortd = [root]

	# Now find the color in the stack closest to that color.
	# Take this color from the stack and add it to the sorted list.
	# Now find the color closest to that color, etc.
	while len(stack) > 1:
		closest, distance = stack[0], difference(stack[0], sortd[-1])
		for clr in stack[1:]:
			d = difference(clr, sortd[-1])
			if d < distance:
				closest, distance = clr, d
		stack.remove(closest)
		sortd.append(closest)
	sortd.append(stack[0])

	return sortd


def movie_colors(mov, op):
	WIDTH = 1000

	projectlist = os.listdir(op.prodir)
	answer = mov
	if answer in projectlist:
		cmovfile, cprodir, jsondict = op.open_project(answer)
		jsondict["shot_colors"] = os.path.join(cprodir, "shot_colors")

	os.system(f"magick identify -format \"%k\" {os.path.join(jsondict['shot_colors'], 'result.png')}")
	os.system(f"magick convert {os.path.join(jsondict['shot_colors'], 'result.png')} +dither -colors 10 {os.path.join(jsondict['shot_colors'], 'result_quant.png')}")

	img_orig = cv.imread(os.path.join(jsondict["shot_colors"], "result_quant.png"))
	height, width, channels = img_orig.shape
	output_img = numpy.empty((WIDTH, WIDTH, 3), numpy.uint8)

	pixels = img_orig
	d = {}

	for line in pixels:
		for px in line:
			if tuple(px) in d:
				d[tuple(px)] += 1
			else:
				d[tuple(px)] = 1

	colors = list(d.keys())

	colors = sort_by_distance(colors)

	px_count = width * height
	x_pos = 0

	for color in colors:
		length = d[color] / float(px_count)
		length = int(math.ceil(length * WIDTH))

		for x in range(length):
			if x_pos + x >= WIDTH:
					break
			for y in range(WIDTH):
				xx = x_pos + x
				output_img[y, xx, 0], output_img[y, xx, 1], output_img[y, xx, 2] = int(color[0]), int(color[1]), int(color[2])
		x_pos += length

	cv.imwrite(os.path.join(jsondict["shot_colors"], "_RESULT.png"), output_img)

	print(f"processing movie colors for {mov} has finished")

	return
