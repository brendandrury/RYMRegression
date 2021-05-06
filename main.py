import subprocess
import os
import pandas

database = open("database.json", 'w')
database.write("[]")
database.close()
files_to_scan = os.listdir('files_to_scan')
for file in files_to_scan:
  if file == ".DS_Store":
    continue
  path = "files_to_scan/" + file
  if os.path.isdir(path):
    continue
  subprocess.run(["python3", "scan_file.py", path])
