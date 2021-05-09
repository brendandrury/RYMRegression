import json
import pandas
import numpy as np
import sys
import datetime
database = open("database.json", 'r')

DEBUG_CHARTS = False

# Load the JSON values into a DataFrame

df = pandas.read_json(database.read())

month_dict = {"January":1, "February":2, "March":3, "April":4, "May":5, "June":6, "July":7, "August":8, "September":9, "October":10, "November":11, "December":12}

# Obscurity regression: Adjust highly-rated releasess with few ratings downwards,
  # based on how much higher we expect them to be than an album with many ratings

df_low_ratings = df[df["Ratings"] < 200]
obscurity_fit = np.polyfit(df_low_ratings["Ratings"], df_low_ratings["Rating"], 4)

df_adjusted_obscurity = df.copy()

full = pandas.DataFrame(np.full(df_adjusted_obscurity["Ratings"].shape, 179))
vals_for_poly = pandas.concat((df_adjusted_obscurity["Ratings"], full), axis=1).min(axis=1)
polyvals = np.polyval(obscurity_fit, vals_for_poly)
adjustments = polyvals / np.polyval(obscurity_fit, 179)
df_adjusted_obscurity["Rating"] = df_adjusted_obscurity["Rating"] / (1 + 2 * (adjustments - 1))

df_adjusted_obscurity.sort_values("Rating", inplace=True, ascending=False)

if DEBUG_CHARTS:
  sys.stdout = open('chart_obscure.txt', 'w')
  for index, album in df_adjusted_obscurity.iterrows():
    print(album["Artists"], "--", album["Name"], "(", album["Release date"], "):", album["Rating"])

live_groups = df_adjusted_obscurity.groupby(df["Live"])
df_adjusted_live = df_adjusted_obscurity.copy()

for i in live_groups:
  if i[0] == True:
    lives = i[1]
  else:
    non_lives = i[1]

# Release type regression: Adjust live and bootleg albums based on average ratings for these types

df_adjusted_live.loc[df_adjusted_live["Live"] == True, "Rating"] /= np.mean(lives["Rating"]) / np.mean(non_lives["Rating"])

bootlegs = df_adjusted_live[df_adjusted_live["Type"] == "Bootleg / Unauthorized"]
non_bootlegs = df_adjusted_live[df_adjusted_live["Type"] != "Bootleg / Unauthorized"]

df_adjusted_live.loc[df_adjusted_live["Type"] == "Bootleg / Unauthorized", "Rating"] /= np.mean(bootlegs["Rating"]) / np.mean(non_bootlegs["Rating"])

live_groups = df_adjusted_live.groupby(df["Live"])
for i in live_groups:
  if i[0] == True:
    lives2 = i[1]
  else:
    non_lives2 = i[1]
bootlegs2 = df_adjusted_live[df_adjusted_live["Type"] == "Bootleg / Unauthorized"]
non_bootlegs2 = df_adjusted_live[df_adjusted_live["Type"] != "Bootleg / Unauthorized"]

live_bootlegs = bootlegs2[bootlegs2.isin(lives2)].dropna()
non_live_bootlegs = df_adjusted_live[~df_adjusted_live.isin(live_bootlegs)].dropna()

df_adjusted_live.sort_values("Rating", inplace=True, ascending=False)

if DEBUG_CHARTS:
  sys.stdout = open('chart_live.txt', 'w')
  for index, album in df_adjusted_live.iterrows():
    print(album["Artists"], "--", album["Name"], "(", album["Release date"], "):", album["Rating"])

# Adjust albums with only Month / Year or Year release dates to match the correct format

today = datetime.date.today()
Ages = []
df_adjusted_live['Age'] = 0
for i, row in df_adjusted_live.iterrows():
  release_date = row['Release date']
  ifor_val = ""
  if release_date.count(" ") == 0:
    ifor_val = "2 July " + release_date
    release_date = ifor_val
  elif release_date.count(" ") == 1:
    ifor_val = "15 " + release_date
    release_date = ifor_val
  if ifor_val:
    df_adjusted_live.at[i,'Release date'] = ifor_val
  Age = (today - datetime.date(int(release_date.split(" ")[2]), month_dict[release_date.split(" ")[1]], int(release_date.split(" ")[0]))).days
  df_adjusted_live.at[i, 'Age'] = Age

# Step 2: Add a new "Day" column

df_adjusted_recency = df_adjusted_live.copy()

# Step 3: Partition dataframes based on Ratings
ratings_groups = df_adjusted_recency.groupby(pandas.qcut(df_adjusted_recency.Ratings, 3, labels=False), as_index=False)

# Step 4: Run a Day vs Ratings regression within each partition
# RYM users rate older albums higher than newer ones; this regression allows us to adjust that
# However, albums with lots of ratings are affected much more, so separate regressions are needed

binned_adjustments = []
for group in ratings_groups:
  group_i = group[1][group[1]["Age"] < 20500]
  polyfit = np.polyfit(group_i["Age"], group_i["Rating"], 2)
  maximum = np.polyval(polyfit, polyfit[1] / (-2 * polyfit[0]))
  group_tuple = (np.min(group_i["Ratings"]), np.max(group_i["Ratings"]))
  polyfit_tuple = (maximum, polyfit)
  binned_adjustments.append((group_tuple, polyfit_tuple))
  
# Step 5: Adjust each partition based on the regression
# Since it's a quadratic fit, calculate max by finding vertex

page_dict = {}

for index, row in df_adjusted_recency.iterrows():
  if row["Live"] or row["Type"] == "Bootleg / Unauthorized":
    continue
  for binned_adjustment in binned_adjustments:
    if row["Ratings"] in range(*binned_adjustment[0]):
      maximum = binned_adjustment[1][0]
      polyfit = binned_adjustment[1][1]
      max_age = polyfit[1] / (-2 * polyfit[0])
  if row["Age"] > max_age:
    continue
  df_adjusted_recency.at[index, "Rating"] /= (np.polyval(polyfit, row["Age"])/maximum)


# Step 6: Concat the partitioned dataframes back into one
  
for index, row in df_adjusted_recency.iterrows():
  if row["Rating"] > 3.60:
    source = row["Source page"]
    if source not in page_dict:
      page_dict[source] = 1
    else:
      page_dict[source] += 1
  else:
    source = row["Source page"]
    if source not in page_dict:
      page_dict[source] = 0

# Step 7: Sort final product and print a chart

df_adjusted_recency.sort_values("Rating", inplace=True, ascending=False)

sys.stdout = open('chart.txt', 'w')

for index, album in df_adjusted_recency.iterrows():
  if album["Type"] == 'nan' or album["Type"] != album["Type"]:
    album["Type"] == "Single"
  print("{",album["Type"],"}", album["Artists"], "--", album["Name"], "(", album["Release date"], "):", album["Rating"])

# Alternate chart for only this decade

sys.stdout = open('2020s.txt', 'w')

for index, album in df_adjusted_recency.iterrows():
  if album["Type"] == 'nan' or album["Type"] != album["Type"]:
    album["Type"] == "Single"
  if album["Age"] > 400:
    continue
  print("{",album["Type"],"}", album["Artists"], "--", album["Name"], "(", album["Release date"], "):", album["Rating"])

sys.stdout = open('sources.txt', 'w')
keys_list = list(page_dict.keys())
keys_list.sort()
for key in keys_list:
  print(key, ":", page_dict[key])

# todo:
  # make repeated code into functions
  # extract constants, put at top
  # use 3D regression for recency bias instead of 
  # genre-based regression
  # GUI (HTML output?)
  # could take a user's RYM profile page and create chart based on their preferences
