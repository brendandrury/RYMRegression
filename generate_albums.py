import math
import random

# randomly selects releases from adjusted chart

EXPONENTIAL_RATE = 4
NUM_ALBUMS = 5
album_list = []
weight_list = []

album_file = open("chart.txt")
album_string = album_file.read()
for line in album_string.splitlines():
  divided = line.split(":")
  score = divided[-1]
  album_list.append(line)
  weight_list.append(math.pow(EXPONENTIAL_RATE, 10 * float(score) - 36))

selected_list = random.choices(album_list, weights=weight_list, k=NUM_ALBUMS)

for element in selected_list:
  print(element)
