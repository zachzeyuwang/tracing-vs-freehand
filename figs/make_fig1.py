import cv2
import numpy as np

def get_freq_bar():
  h = np.zeros((51, 256), np.uint8)
  s = np.zeros((51, 256), np.uint8)
  v = 255 - np.zeros((51, 256), np.uint8)
  for r in range(h.shape[0]):
    for c in range(h.shape[1]):
      if c == 0: # white
        s[r][c] = 0
      elif c <= 0.25 * 255:
        h[r][c] = 109
        s[r][c] = c
      else: # orange
        h[r][c] = 12
        s[r][c] = c
  hsv = cv2.merge((h, s, v))
  return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

freq_bar = get_freq_bar()
image = "REN_SketchFab_fossil2_000_RGBND.png"
image_prompt = cv2.imread("../data/images/" + image)
apparent_ridges = cv2.imread("../data/npr_thresh/%s&_AR.png" % image[:-4])
kernel = np.ones((3, 3), np.uint8)
apparent_ridges = cv2.erode(apparent_ridges, kernel, iterations=1)

tracing_progression = []
for i in range(5):
  t = cv2.imread("../utils/progression/color&tracings&%s&%s.png" % (image[:-4], i))
  tracing_progression.append(t)
drawing_progression = []
for i in range(5):
  d = cv2.imread("../utils/progression/color&drawings_registered&%s&%s.png" % (image[:-4], i))
  drawing_progression.append(d)
row1 = np.hstack([image_prompt] + tracing_progression)
row2 = np.hstack([apparent_ridges] + drawing_progression)
row3 = np.ones((102, row1.shape[1], 3), np.uint8) * 255
row3[51:, -512:-256] = freq_bar
fig = np.vstack([row1, row2, row3])
cv2.imwrite("fig1.jpg", fig)
