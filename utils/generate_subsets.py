# Split each drawing into partial drawings based on temporal order, i.e., split 2 minutes into 5 segments
import glob
import json
import numpy as np
import os
import svgwrite
import sys

if len(sys.argv) != 1 and len(sys.argv) != 3:
  print("Usage 1: python generate_subsets.py")
  print("Usage 2: python generate_subsets.py tracings|drawings_registered IMAGE_FILENAME.png")
  sys.exit(1)

def generate_subsets(group, image, uid, sketch):
  if len(glob.glob("subsets/%s&%s&%s&*.svg" % (group, image[:-4], uid))) >= 5:
    print("Skipping %s: %s %s" % (group, image, uid))
    return
  print("Processing %s: %s %s" % (group, image, uid))
  start_time = int(sketch[0]["path"].split(",")[0])
  end_time = int(sketch[-1]["path"].split(",")[-3])
  delimiting_stroke_ids = []
  delimiting_vertex_ids = []
  bin_id = 0
  for stroke_id in range(len(sketch)):
    txy = sketch[stroke_id]["path"].split(",")
    for vertex_id in range(0, len(txy), 3):
      curr_bin_id = int((int(txy[vertex_id]) - start_time) / ((end_time - start_time) / 5))
      if curr_bin_id > bin_id:
        bin_id = curr_bin_id
        delimiting_stroke_ids.append(stroke_id)
        delimiting_vertex_ids.append(vertex_id // 3)
  while len(delimiting_stroke_ids) < 5:
    delimiting_stroke_ids.append(delimiting_stroke_ids[-1])
  while len(delimiting_vertex_ids) < 5:
    delimiting_vertex_ids.append(delimiting_vertex_ids[-1])
  delimiting_stroke_ids.insert(0, 0)
  delimiting_vertex_ids.insert(0, 0)
  for i in range(5):
    dwg = svgwrite.Drawing("subsets/%s&%s&%s&%s.svg" % (group, image[:-4], uid, i), size=(800, 800))
    for stroke_id in range(delimiting_stroke_ids[i], delimiting_stroke_ids[i+1]+1):
      txy = sketch[stroke_id]["path"].split(",")
      start_vertex_id = 0
      end_vertex_id = len(txy)
      if stroke_id == delimiting_stroke_ids[i]:
        start_vertex_id = 3 * delimiting_vertex_ids[i]
      if stroke_id == delimiting_stroke_ids[i+1]:
        end_vertex_id = 3 * delimiting_vertex_ids[i+1]
      if start_vertex_id >= end_vertex_id:
        continue
      d = "M"
      for vertex_id in range(start_vertex_id, end_vertex_id, 3):
        if vertex_id >= start_vertex_id + 3:
          d = d + "L"
        d = d + txy[vertex_id+1] + "," + txy[vertex_id+2]
      w = dwg.path(d=d, fill="none", stroke="#000000", style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); stroke-linecap: round; stroke-linejoin: round; stroke-opacity: %s; stroke-width: %s;" % ("1", "5"))
      dwg.add(w)
    dwg.save()
    os.system("rsvg-convert -b white 'subsets/%s&%s&%s&%s.svg' > 'subsets/%s&%s&%s&%s.png'" % (group, image[:-4], uid, i, group, image[:-4], uid, i))

if len(sys.argv) == 1:
  for group in ["tracings", "drawings_registered"]:
    with open("../data/%s.json" % group) as f:
      json_data = json.load(f)
    for image in json_data.keys():
      for uid in json_data[image].keys():
        sketch = json_data[image][uid]
        generate_subsets(group, image, uid, sketch)
elif len(sys.argv) == 3:
  group = sys.argv[1]
  image = sys.argv[2]
  with open("../data/%s.json" % group) as f:
    json_data = json.load(f)
  for uid in json_data[image].keys():
    sketch = json_data[image][uid]
    generate_subsets(group, image, uid, sketch)
