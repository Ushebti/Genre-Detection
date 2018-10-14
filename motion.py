# -*- coding: utf-8 -*-
import cv2 as cv
import os
import numpy


def motion(mov, op):
	MAX_FRAMES = 5000
	WIDTH = 500

	projectlist = os.listdir(op.prodir)
	answer = mov
	if answer in projectlist:
		cmovfile, cprodir, jsondict = op.open_project(answer)
		jsondict["motion"] = os.path.join(cprodir, "motion")
		try:
			os.mkdir(jsondict["motion"])
		except:
			print("motion folder already exists!")

		cap = cv.VideoCapture()
		cap.open(cmovfile)

		if not cap.isOpened():
			print(f"Fatal error - could not parse video {answer}")

	prev_img = None

	global_frame_counter = 0
	file_counter = 0

	width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

	output_img = numpy.empty((MAX_FRAMES, WIDTH, 3), numpy.uint8)

	shottxt_dir = os.path.join(cprodir, "snapshots/shots.txt")
	with open(shottxt_dir, "r") as f:
		lines = [line for line in f if line]  # (start_frame, end_frame, duration)

	f_frm = open(os.path.join(jsondict["motion"], "motion.txt"), "w")
	f_avg = open(os.path.join(jsondict["motion"], "motion_shot-avg.txt"), "w")
	motion = []

	for nr, line in enumerate(lines):
		duration = int(line.split("\t")[2])

		for frame_counter in range(duration):
			(rv, img_orig) = cap.read()

			if not rv:
				break

			img = img_orig
			global_frame_counter += 1

			if nr == 0 and frame_counter == 0:  # first shot, first frame
				prev_img = numpy.empty((height, width, 3), numpy.uint8)

			diff = cv.absdiff(img, prev_img)
			diff = cv.threshold(diff, 10, 255, cv.THRESH_BINARY)
			d_color = 0
			for n in range(3):
				d_color += float(cv.countNonZero(diff[1][:,:,n])) / float(height * width)
			d_color = d_color / 3

			motion.append(d_color)
			prev_img = img

			# WRITE TEXT FILE
			f_frm.write("%f\n" % (d_color))
			if frame_counter == duration - 1:  # last frame of current shot
				motion_value = sum(motion) / len(motion)
				f_avg.write("%f\t%d\n" % (motion_value, duration))
				motion = []

			# WRITE IMAGE
			if frame_counter == 0:  # ignore each first frame -- the diff after a hard cut is meaningless
				global_frame_counter -= 1
				continue
			else:
				for i in range(WIDTH):
					value = d_color * 255
					remaining_frames = (global_frame_counter - 1) % MAX_FRAMES
					output_img[remaining_frames, i, 0], output_img[remaining_frames, i, 1], output_img[remaining_frames, i, 2] = value, value, value

			if global_frame_counter % MAX_FRAMES == 0:
				cv.imwrite(os.path.join(jsondict["motion"], f"motion_{file_counter}.png"), output_img)
				file_counter += 1

	if global_frame_counter % MAX_FRAMES != 0:
		remaining_frames = (global_frame_counter - 1) % MAX_FRAMES
		output_img = output_img[0:remaining_frames, :, :]
		cv.imwrite(os.path.join(jsondict["motion"], f"motion_{file_counter}.png"), output_img)

	f_frm.close()
	f_avg.close()

	print(f"Calculating motion for {mov} has finished")
	return
