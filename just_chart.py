import json
import sys
import numpy
import datetime
import copy

month_dict = {"January":1, "February":2, "March":3, "April":4, "May":5, "June":6, "July":7, "August":8, "September":9, "October":10, "November":11, "December":12}

sys.stdout = open('chart.txt', 'w')

regression_dict = json.loads(open('regression.json', 'r').read())

obscurity_penalty = numpy.array(regression_dict["Obscurity Penalty"])
obscurity_model = numpy.poly1d(obscurity_penalty)

genre_dict = {}
age_list = []

def get_age(album):
  album_release_date = album["Release date"].split(" ")
  if len(album_release_date) == 3:
    day = album_release_date[0]
    try:
      mon = month_dict[album_release_date[1]]
    except KeyError:
      return
    year = album_release_date[2]
  if len(album_release_date) == 2:
    day = 15
    try:
      mon = month_dict[album_release_date[0]]
    except KeyError:
      return
    year = album_release_date[1]
  if len(album_release_date) == 1:
    day = 15
    mon = 6
    year = album_release_date[0]
  try:
    release_date = datetime.date(int(year), int(mon), int(day))
  except ValueError:
    # broken album. removing this check will catch broken release dates
    return
  today = datetime.date(2020, 10, 27)
  age = today - release_date
  return age.days

def get_boost(age, boost_function):
  if not boost_function:
    return 0
  vertex = -1 * boost_function[1] / (2 * boost_function[0])
  if age >= vertex:
    return 0
  else:
    max = boost_function[2] - (boost_function[1] * boost_function[1] / (4 * boost_function[0]))
    return max - boost_function[0] * age * age - boost_function[1] * age - boost_function[2]

def sorting_function(album):
  penalty = 0
  if album["Ratings"] < 564:
    penalty = 3.7255 - obscurity_model(album["Ratings"])
  
  age = get_age(album)
  if not age:
    # could not determine age
    return album["Rating"] + penalty

  boost_function_1 = None
  
  boost_function_2 = None

  last_i = None
  boost = None
  for i in list(regression_dict["Recency Boost"].keys()):
    #print(i)
    if float(i) > album["Ratings"]:
      boost_function_1 = regression_dict["Recency Boost"][i]
      try:
        boost_function_2 = regression_dict["Recency Boost"][last_i]
      except KeyError:
        pass
      if not boost_function_1:
        boost_function_1 = regression_dict["Recency Boost"][list(regression_dict["Recency Boost"].keys())[len(list(regression_dict["Recency Boost"].keys()))-1]]
      boost_1 = get_boost(age, boost_function_1)
      boost_2 = get_boost(age, boost_function_2)
      if boost_1 == 0:
        boost = boost_2
        break
      if boost_2 == 0:
        boost = boost_1
        break
      #print(album["Name"], boost_1, boost_2)
      difference_2 = float(i) - album["Ratings"]
      difference_1 = album["Ratings"] - float(last_i)
      boost = (boost_1 * difference_1 + boost_2 * difference_2) / (difference_1 + difference_2)
      break
    last_i = i

  if boost is None:
    boost = get_boost(age, regression_dict["Recency Boost"][last_i])
  #print(album["Name"], penalty, boost, album["Rating"])
  return album["Rating"] + penalty + boost

def sorting_function_2(genre):
  return round(genre["average"], 2)

def sorting_function_3(genre):
  return round(genre["appearances"], 2)

json_database = open('database.json', 'r').read()
albums = json.loads(json_database)

albums.sort(key=sorting_function, reverse=True)

for album in albums:
  print(album["Artists"], "--", album["Name"], "(" + album["Release date"],"):", round(sorting_function(album),2))
  


