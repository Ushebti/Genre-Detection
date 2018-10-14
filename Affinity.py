import csv

with open("movie.csv") as csvfile:
    data = csv.reader(csvfile, dialect="excel", delimiter=";")

    movdict = {}

    for index, row in enumerate(data):
        if index == 0:
            pass
        movdict[row[0]] = {"cluster_0": 0, "cluster_1": 0, "cluster_2": 0, "cluster_3": 0, "cluster_4": 0}
        for index, col in enumerate(row):
            if col == "cluster_0":
                movdict[row[0]]["cluster_0"] += 1 + (int(row[index - 1]) / 100)
            elif col == "cluster_1":
                movdict[row[0]]["cluster_1"] += 1 + (int(row[index - 1]) / 100)
            elif col == "cluster_2":
                movdict[row[0]]["cluster_2"] += 1 + (int(row[index - 1]) / 100)
            elif col == "cluster_3":
                movdict[row[0]]["cluster_3"] += 1 + (int(row[index - 1]) / 100)
            elif col == "cluster_4":
                movdict[row[0]]["cluster_4"] += 1 + (int(row[index - 1]) / 100)

outputfile = [["Movie", "cluster_0", "cluster_1", "cluster_2", "cluster_3", "cluster_4"]]

for row in movdict:
    templist = []
    templist.append(row)
    for x in range(1, 6):
        templist.append(movdict[row][outputfile[0][x]])
    outputfile.append(templist)

with open("cluster_affinity.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter=",", quotechar="'")
    for row in outputfile:
        writer.writerow(row)
