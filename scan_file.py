import json
import sys
import copy
from html.parser import HTMLParser

default_album = {"Artists": [], "Artist links": [], "Primary genres": [], "Secondary genres": [], "Live": False}
albums = json.loads(open("database.json").read())

class MyHTMLParser(HTMLParser):
  def handle_starttag(self, tag, attrs):
    global albums
    global current_album
    global last_class
    global default_album
    if tag == "div" or tag == "class" or tag == "span":
      for name, value in attrs:
        if name == "class" and value.strip():
          last_class = value
        if last_class == "topcharts_itembox chart_item_release" and current_album != default_album:
          if "Source page" not in current_album:
            current_album["Source page"] = str(sys.argv[1])
          albums.append(current_album)
          current_album = copy.deepcopy(default_album)
          current_album["Source page"] = str(sys.argv[1])
    if tag == "a":
      last_name = None
      for name, value in attrs:
        if not value or value.strip() == "&" or value.strip() == "/":
          continue
        if name == "href":
          if last_class == "topcharts_album_title":
            current_album["Album link"] = value.strip()
          if last_class == "topcharts_item_artist_newmusicpage topcharts_item_artist":
            current_album["Artist links"].append(value.strip())
          if last_name == "ui_stream_link_btn ui_stream_link_btn_applemusic":
            current_album["Apple Music"] = value.strip()
          if last_name == "ui_stream_link_btn ui_stream_link_btn_spotify":
            current_album["Spotify"] = value.strip()
          if last_name == "ui_stream_link_btn ui_stream_link_btn_soundcloud":
            current_album["Soundcloud"] = value.strip()
          if last_name == "ui_stream_link_btn ui_stream_link_btn_bandcamp":
            current_album["Bandcamp"] = value.strip()
      if name:
        last_name = name
    #input(tag)

  def handle_endtag(self, tag):
    pass

  def handle_data(self, data):
    global albums
    global current_album
    global last_class
    if not data.strip() or data.strip() == "," or data.strip() == "&" or data.strip() == "/":
      return
    if last_class == "topcharts_item_title":
      current_album["Name"] = data.strip()
    if last_class == "topcharts_item_artist_newmusicpage topcharts_item_artist" or last_class == "credited_list_inner" and data.strip():
      current_album["Artists"].append(data.strip())
    if last_class == "chart_release_type":
      current_album["Type"] = data.strip()
    if last_class == "chart_is_live":
      current_album["Live"] = True
    if last_class == "topcharts_item_releasedate":
      current_album["Release date"] = data.strip()
    if last_class == "topcharts_stat topcharts_avg_rating_stat":
      current_album["Rating"] = float(data.strip())
    if last_class == "topcharts_stat topcharts_ratings_stat":
      current_album["Ratings"] = int(data.strip().replace(",",""))
    if last_class == "topcharts_item_genres_container":
      current_album["Primary genres"].append(data.strip())
    if last_class == "topcharts_item_secondarygenres_container":
      current_album["Secondary genres"].append(data.strip())

file_to_scan = open(str(sys.argv[1]))
music_page_string = file_to_scan.read()
parser_instance = MyHTMLParser()
current_album = copy.deepcopy(default_album)
last_class = ""
parser_instance.feed(music_page_string)
if current_album != default_album:
  albums.append(current_album)
file_to_write = open("database.json", "w")
file_to_write.write(json.dumps(albums))


