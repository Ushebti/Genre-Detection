# -*- coding: utf-8 -*-
import os.path
import cv2 as cv
import numpy as np


def shot_detection(mov, op):
	projectlist = os.listdir(op.prodir)
	answer = mov
	if answer in projectlist:
		cmovfile, cprodir, jsondict = op.open_project(answer)
		jsondict["snapshotdir"] = os.path.join(cprodir, "snapshots")
		try:
			os.mkdir(jsondict["snapshotdir"])
		except OSError:
			print("snapshot folder already exists!")

		cap = cv.VideoCapture()
		cap.open(cmovfile)

		if not cap.isOpened():
			print(f"Fatal error - could not parse video {answer}")

		width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
		height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)

		last_frame_black = False

		while True:
			(rv, img_orig) = cap.read()

			if not rv:
				cv.imwrite(os.path.join(jsondict["snapshotdir"], f"{current_frame}.png"), prev_img)
				jsondict["frame_count"] = current_frame
				break

			img = cv.resize(img_orig, (0, 0), fx=0.25, fy=0.25, interpolation=cv.INTER_AREA)

			current_frame = cap.get(cv.CAP_PROP_POS_FRAMES)
			if current_frame == 1:
				cv.imwrite(os.path.join(jsondict["snapshotdir"], f"{current_frame}.png"), img)
				prev_img = img
				continue

			img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

			#####################
			# METHOD #1: find the number of pixels that have (significantly) changed since the last frame
			diff = cv.absdiff(img_hsv, prev_img)
			diff = cv.threshold(diff, 10, 255, cv.THRESH_BINARY)

			d_color = 0
			for n in range(3):
				d_color += float(cv.countNonZero(diff[1][:,:,n])) / float(width * height)

			d_color = float(d_color / 3.0)  # 0..1

			# #####################
			# METHOD #2: calculate the amount of change in the histograms

			#numpy array indicing for the 3 channels of the hsv image. (Not entirely sure this is best solution, but it is more readable than before)
			#it is also definitely faster than cv2.split().
			planes = [img_hsv[:,:,0], img_hsv[:,:,1], img_hsv[:,:,2]]

			#Why does he do binsize 50? speed maybe.
			bin_size = [50, 50, 50]
			hist_range = [0, 360, 0, 250, 0, 255]
			channels = [0,1,2]

			hist = cv.calcHist(planes, channels, None, bin_size, hist_range)
			cv.normalize(hist, hist).flatten()

			if current_frame == 2:
				prev_hist = hist

			d_hist = cv.compareHist(prev_hist, hist, cv.HISTCMP_INTERSECT)
			prev_hist = hist

			# combine both methods to make a decision
			THRESHOLD = 0.48
			if (0.4 * d_color + 0.6 * (1 - d_hist)) >= THRESHOLD:
				cv.imwrite(os.path.join(jsondict["snapshotdir"], f"{current_frame}.png"), img)

			# #####################
			# METHOD #3: detect series of (almost) black frames as an indicator for "fade to black"
			#average of the value channel
			average = np.average(img_hsv[:,:,2])
			if average <= 0.6:
				if not last_frame_black:  # possible the start
					black_frame_start = current_frame
				last_frame_black = True
			else:
				if last_frame_black:  # end of a series of black frames
					cut_at = black_frame_start + int((current_frame - black_frame_start) / 2)

					cv.imwrite(os.path.join(jsondict["snapshotdir"], f"{cut_at}.png"), img)
				last_frame_black = False

			prev_img = img

		print(f"shot detection for {mov} finished")

		cap.release()

		return
