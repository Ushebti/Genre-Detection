from modules.os_handler import OperationHandler 
import os

if __name__ == "__main__":
	oh = OperationHandler()
	templist = []
	for mov in os.listdir("D:/film"):
		templist.append(mov)

	print("These are the movies in D:/film currently:")
	print(templist)
	print("")
	answer = input("Would you like to update the project directory with these movies? (y/n):")
	if answer == "y":
		movs = oh.update_projects()
		if len(movs) > 0: 
			print("These movies has been added")
			print(movs)
		else: 
			print("All movies already added")
	else:
		print("Alright fine...")
