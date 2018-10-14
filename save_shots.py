# -*- coding: utf-8 -*-
import os
import os.path
import glob
import json


def save_shots(mov, op):
	projectlist = os.listdir(op.prodir)
	answer = mov
	if answer in projectlist:
		cmovfile, cprodir, jsondict = op.open_project(answer)
		jsondict["snapshotdir"] = os.path.join(cprodir, "snapshots")

	frames = [os.path.splitext(os.path.basename(file))[0] for file in glob.glob(jsondict["snapshotdir"] + "\\*.png")]
	frames = [int(float(frame)) for frame in frames]
	frames.sort(key=int)

	with open(os.path.join(cprodir, "project.json"), "w") as jsonfile:
		jsondict["frames"] = str(frames[-1] - frames[0])
		jsondict["start_frame"] = str(frames[0])
		jsondict["end_frame"] = str(frames[-1] - 1)
		json.dump(jsondict, jsonfile, sort_keys=True, indent=4)

	with open(os.path.join(jsondict["snapshotdir"], "shots.txt"), "w") as f:
		for i, frame in enumerate(frames):
			if i == len(frames) - 1:
				break

			f.write(str(frame) + "\t" + str(frames[i + 1] - 1) + "\t" + str(frames[i + 1] - frame) + "\n")

	print(f"saving shots for {mov} have finished.")
	return
