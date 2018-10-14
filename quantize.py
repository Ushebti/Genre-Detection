import os.path
import numpy
import cv2 as cv
from modules.os_handler import OperationHandler
import csv


def quantize(mov, op):

    projectlist = os.listdir(op.prodir)
    answer = mov
    if answer in projectlist:
        cmovfile, cprodir, jsondict = op.open_project(answer)
        jsondict["shot_colors"] = os.path.join(cprodir, "shot_colors")
        jsondict["motion"] = os.path.join(cprodir, "motion")

    movie_colors = cv.imread(os.path.join(jsondict["shot_colors"], "_RESULT.png"))
    motion_spectrum = cv.imread(os.path.join(jsondict["motion"], "result_sorted.png"))

    colors = movie_colors[1,:,:]
    motion = numpy.mean(motion_spectrum[:,1,0])
    unique_colors = []
    quantized_data = [mov]
    prev_color = movie_colors[1,1,:]
    width = None

    #find unique colors
    for nr, color in enumerate(colors):
        if not numpy.array_equal(color, prev_color):
            unique_colors.append((prev_color, nr))
        elif nr == len(colors) - 1:
            unique_colors.append((color, nr))
        prev_color = color

    #transform them to a single unique value and append to list
    for index, color in enumerate(unique_colors):
        blue = color[0][0]
        green = color[0][1]
        red = color[0][2]
        if width is None:
            width = color[1]
        else:
            width = color[1] - unique_colors[index - 1][1] + 1
        quantized_data.append(f"{blue}, {green}, {red}, {width}")

    if len(quantized_data) != 11:
        for miss in range(11 - len(quantized_data)):
            quantized_data.append("missing")

    #find average of motion spectrum
    motion = numpy.mean(motion_spectrum[:,1,0])
    quantized_data.append(motion)

    return quantized_data


if __name__ == "__main__":

    movie_directory = "D:/film"
    project_directory = os.path.join(movie_directory, "FilmData")
    op = OperationHandler(movie_directory, project_directory)
    quant_directory = os.path.join(op.prodir, "quantized")
    movlist = [mov for mov in os.listdir(movie_directory)]

    quant_header = ["Movie", "Color1", "Color2", "Color3", "Color4", "Color5", "Color6", "Color7", "Color8", "Color9", "Color10", "avg_motion"]
    quantized_csv = open(os.path.join(quant_directory, "quantized_data.csv"), "w", newline="")
    quant_writer = csv.writer(quantized_csv, delimiter=",", quotechar="'", quoting=csv.QUOTE_MINIMAL)

    quant_writer.writerow(quant_header)

    results = []

    for mov in movlist:
        try:
            results.append(quantize(mov, op))
        except UnboundLocalError:
            continue

    for row in results:
        quant_writer.writerow(row)

    quantized_csv.close()



















