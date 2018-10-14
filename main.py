from shot_detection import shot_detection
from save_shots import save_shots
from shot_colors import shot_colors
from shot_colors_avg import shot_colors_avg
from movie_colors import movie_colors
from motion import motion
from quantize import quantize
from sort_motion_spectrum import sort_motion_spectrum
from modules.os_handler import OperationHandler
from threading import Thread, activeCount
import os
import os.path
import time
import csv


def start_process():
    movie_directory = input("Write absolute path to movie folder: ")

    movlist = [mov for mov in os.listdir(movie_directory)]
    if len(movlist) == 0:
        print(f"{movie_directory} doesn't exist, or is empty.")
        return

    print(f"These are the movies in {movie_directory}:")
    print(movlist)
    print("")
    try:
        project_directory = os.path.join(movie_directory, "FilmData")
        os.mkdir(project_directory)
    except OSError:
        print("project folder already exists!")

    op = OperationHandler(movie_directory, project_directory)

    answer = input("Would you like to update the project directory with these movies? (y/n):")
    if answer == "y":
        movs = op.update_projects()
        if len(movs) > 0:
            print("These movies has been added")
            print(movs)
        else:
            print("All movies already added")
    else:
        print("Alright fine...")

    return movlist, op


def process_movie(mov, op, index, results):
    print(f"performing shot detection for {mov}")
    shot_detection(mov, op)

    print(f"Saving shots for {mov}")
    save_shots(mov, op)

    print(f"procesing shot colors for {mov}")
    shot_colors(mov, op)

    print(f"processing shot colors average for {mov}")
    shot_colors_avg(mov, op)

    print(f"processing movie colors for {mov}")
    movie_colors(mov, op)

    print(f"Calculating motion for {mov}")
    motion(mov, op)

    print(f"Sorting motion spectrum for {mov}")
    sort_motion_spectrum(mov, op)

    results[index] = quantize(mov, op)

    return


def main():
    movlist, op = start_process()
    start_overall = time.time()
    quant_directory = os.path.join(op.prodir, "quantized")
    os.mkdir(quant_directory)

    results = [None] * len(movlist)
    thread_dict = {}
    thread_index = 0

    quant_header = ["Movie", "Color1", "Color2", "Color3", "Color4", "Color5", "Color6", "Color7", "Color8", "Color9", "Color10", "avg_motion"]
    quantized_csv = open(os.path.join(quant_directory, "quantized_data.csv"), "w", newline="")
    quant_writer = csv.writer(quantized_csv, delimiter=",", quotechar="'", quoting=csv.QUOTE_MINIMAL)

    quant_writer.writerow(quant_header)

    for index, mov in enumerate(movlist):
        thread_dict[index] = Thread(target=process_movie, args=(mov, op, index, results))

    while None in results:
        if activeCount() == 6:
            time.sleep(30)
        elif thread_index == len(movlist) - 1:  # last movie to be added
            thread_dict[thread_index].start()
            thread_dict[thread_index].join()
            break
        else:
            thread_dict[thread_index].start()
            thread_index += 1

    while None in results:
        time.sleep(30)

    for row in results:
        quant_writer.writerow(row)

    quantized_csv.close()
    print(f"All {len(movlist)} movie(s) have been processed. it took {(time.time() - start_overall) / 60} minutes")


if __name__ == "__main__":
    main()
