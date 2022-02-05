# Visualize progression of tracing and freehand drawing
import cv2
import glob
import json
import numpy as np
import sys

if len(sys.argv) != 1 and len(sys.argv) != 3:
  print("Usage 1: python visualize_progression.py")
  print("Usage 2: python visualize_progression.py tracings|drawings_registered IMAGE_FILENAME.png")
  sys.exit(1)

def accumulate(group, image, uids):
  print("Accumulating %s: %s" % (group, image))
  for uid in uids:
    acc = 255 - np.zeros((800, 800), np.uint8)
    for i in range(5):
      subset = cv2.imread("subsets/%s&%s&%s&%s.png" % (group, image[:-4], uid, i), cv2.IMREAD_GRAYSCALE)
      _, subset = cv2.threshold(subset, 127, 255, cv2.THRESH_BINARY)
      acc = cv2.bitwise_and(acc, subset)
      cv2.imwrite("progression/acc&%s&%s&%s&%s.png" % (group, image[:-4], uid, i), acc)

def superimpose(group, image, uids):
  print("Superimposing %s: %s" % (group, image))
  for i in range(5):
    composite = np.zeros((800, 800), np.float32)
    for uid in uids:
      acc = cv2.imread("progression/acc&%s&%s&%s&%s.png" % (group, image[:-4], uid, i), cv2.IMREAD_GRAYSCALE)
      acc = (255 - acc) // 255
      composite += acc
    grayscale = 255 - np.round(composite / len(uids) * 255).astype(np.uint8)
    cv2.imwrite("progression/%s&%s&%s.png" % (group, image[:-4], i), grayscale)

    h = np.zeros((800, 800), np.uint8)
    s = np.zeros((800, 800), np.uint8)
    v = 255 - np.zeros((800, 800), np.uint8)
    a = np.zeros((800, 800), np.uint8)
    for r in range(composite.shape[0]):
      for c in range(composite.shape[1]):
        if composite[r][c] == 0: # white
          s[r][c] = 0
        elif composite[r][c] <= 0.25 * len(uids): # blue
          h[r][c] = 109
          s[r][c] = 255 - grayscale[r][c]
          a[r][c] = 255
        else: # orange
          h[r][c] = 12
          s[r][c] = 255 - grayscale[r][c]
          a[r][c] = 255
    hsv = cv2.merge((h, s, v))
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    b, g, r = cv2.split(bgr)
    bgra = cv2.merge((b, g, r, a))
    cv2.imwrite("progression/color&%s&%s&%s.png" % (group, image[:-4], i), bgra)

if len(sys.argv) == 1:
  for group in ["tracings", "drawings_registered"]:
    with open("../data/%s.json" % group) as f:
      json_data = json.load(f)
    for image in json_data.keys():
      accumulate(group, image, json_data[image].keys())
      superimpose(group, image, json_data[image].keys())
      
elif len(sys.argv) == 3:
  group = sys.argv[1]
  image = sys.argv[2]
  with open("../data/%s.json" % group) as f:
    json_data = json.load(f)
  accumulate(group, image, json_data[image].keys())
  superimpose(group, image, json_data[image].keys())
