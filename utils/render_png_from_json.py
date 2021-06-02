# run in ubuntu bash
import json
import svgwrite
import os

for group in ["tracings", "drawings", "drawings_registered"]:
  print(group)

  with open("../data/%s.json" % group) as f:
    tracer_json = json.load(f)

  for image, uids in tracer_json.items():
    for uid, sketch in uids.items():
      if os.path.isfile("../data/png/%s/" % group + image[:-4] + "&" + uid + ".png"):
        print("Skipping", image, uid)
        continue
      print(image, uid)
      dwg = svgwrite.Drawing(filename="../data/svg/%s/" % group + image[:-4] + "&" + uid + ".svg", size=(800, 800))
      for sid in range(len(sketch)):
        txy = sketch[sid]["path"].split(",")
        if len(txy) <= 3:
          continue
        d = "M"
        for vid in range(len(txy) // 3):
          if vid >= 1:
            d = d + "L"
          d = d + txy[3*vid+1] + "," + txy[3*vid+2]
        # you can change stroke color and width by modifying the line below
        w = dwg.path(d=d, fill="none", stroke="#000000", style="-webkit-tap-highlight-color: rgba(0, 0, 0, 0); stroke-linecap: round; stroke-linejoin: round; stroke-opacity: %s; stroke-width: %s;" % ("1", "1"))
        dwg.add(w)
      dwg.save()
      os.system("rsvg-convert -b white " + "'../data/svg/%s/" % group + image[:-4] + "&" + uid + ".svg'" + " > " + "'../data/png/%s/" % group + image[:-4] + "&" + uid + ".png'")
