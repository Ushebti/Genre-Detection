import json, os, os.path


class OperationHandler(object):
	def __init__(self, movie_directory, project_directory):
		self.movdir = movie_directory
		self.prodir = project_directory
		self.tempdict = {}

	def update_projects(self):
		added_movs = []
		for mov in os.listdir(self.movdir):
			if mov not in os.listdir(self.prodir) and mov != "FilmData":
				added_movs.append(mov)
				newdir = os.path.join(self.prodir, mov)
				os.mkdir(newdir)
				movfolder = os.path.join(self.movdir, mov)
				self.tempdict["path"] = os.path.join(movfolder, os.listdir(movfolder)[0])

				with open (os.path.join(newdir, "project.json"), "w") as file:
					json.dump(self.tempdict, file, sort_keys=True, indent=4)

		return added_movs

	def open_project(self, projectname):
		with open(os.path.join(self.prodir, projectname, "project.json"), "r") as file:
			data = json.load(file)
			cmovfile = data["path"]
			cprodir = os.path.join(self.prodir, projectname)

			return cmovfile, cprodir, data





if __name__ == "__main__":
	oh = OperationHandler()
	oh.update_projects()

