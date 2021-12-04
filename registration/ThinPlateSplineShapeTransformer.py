# self-implemented thin plate spline: https://profs.etsmtl.ca/hlombaert/thinplates/
import cv2
import numpy as np
from scipy import linalg

class ThinPlateSplineShapeTransformer:
  def __init__(self, src_pts, dst_pts):
    assert len(src_pts) == len(dst_pts)
    self.num_pts = len(src_pts)
    self.src_pts = src_pts
    self.dst_pts = dst_pts
    self.params_x_dst2src = None
    self.params_y_dst2src = None
    self.params_x_src2dst = None
    self.params_y_src2dst = None

  def __mapping_dst2src(self):
    # mapping dst_pts to src_pts
    dx = [self.src_pts[i][0] - self.dst_pts[i][0] for i in range(self.num_pts)]
    dy = [self.src_pts[i][1] - self.dst_pts[i][1] for i in range(self.num_pts)]
    Vx = np.concatenate((np.asarray(dx, np.float32), np.zeros(3, np.float32)), axis=0)
    Vy = np.concatenate((np.asarray(dy, np.float32), np.zeros(3, np.float32)), axis=0)
    K = np.asarray([[self.__tps(self.dst_pts[i], self.dst_pts[j]) for j in range(self.num_pts)] for i in range(self.num_pts)], dtype=np.float32)
    P = np.concatenate((np.ones((self.num_pts, 1), np.float32), np.asarray(self.dst_pts, dtype=np.float32)), axis=1)
    L_upper = np.concatenate((K, P), axis=1)
    L_lower = np.concatenate((P.T, np.zeros((3, 3), np.float32)), axis=1)
    L = np.concatenate((L_upper, L_lower), axis=0)
    # L is symmetric, so eigen decomposition gives L = V E inv(V)
    # E is eigenvalues, diagonal
    # V is eigenvectors, orthogonal, i.e. V.T = inv(V)
    # inv(L) = inv(V) inv(E) V = V.T 1/E V
    E, V = np.linalg.eigh(L)
    L_inv = np.dot(V, np.dot(np.diag(1 / E), V.T))
    self.params_x_dst2src = np.dot(L_inv, Vx)
    self.params_y_dst2src = np.dot(L_inv, Vy)

  def __mapping_src2dst(self):
    # mapping src_pts to dst_pts
    dx = [self.dst_pts[i][0] - self.src_pts[i][0] for i in range(self.num_pts)]
    dy = [self.dst_pts[i][1] - self.src_pts[i][1] for i in range(self.num_pts)]
    Vx = np.concatenate((np.asarray(dx, np.float32), np.zeros(3, np.float32)), axis=0)
    Vy = np.concatenate((np.asarray(dy, np.float32), np.zeros(3, np.float32)), axis=0)
    K = np.asarray([[self.__tps(self.src_pts[i], self.src_pts[j]) for j in range(self.num_pts)] for i in range(self.num_pts)], dtype=np.float32)
    P = np.concatenate((np.ones((self.num_pts, 1), np.float32), np.asarray(self.src_pts, dtype=np.float32)), axis=1)
    L_upper = np.concatenate((K, P), axis=1)
    L_lower = np.concatenate((P.T, np.zeros((3, 3), np.float32)), axis=1)
    L = np.concatenate((L_upper, L_lower), axis=0)
    # L is symmetric, so eigen decomposition gives L = V E inv(V)
    # E is eigenvalues, diagonal
    # V is eigenvectors, orthogonal, i.e. V.T = inv(V)
    # inv(L) = inv(V) inv(E) V = V.T 1/E V
    E, V = np.linalg.eigh(L)
    L_inv = np.dot(V, np.dot(np.diag(1 / E), V.T))
    self.params_x_src2dst = np.dot(L_inv, Vx)
    self.params_y_src2dst = np.dot(L_inv, Vy)

  def __tps(self, pt1, pt2):
    pt1 = np.asarray(pt1)
    pt2 = np.asarray(pt2)
    pt1_2 = pt2 - pt1
    sqr_norm = np.dot(pt1_2, pt1_2.T)
    if np.isclose(sqr_norm, 0):
      return 0
    return sqr_norm * np.log(sqr_norm) / 2

  def __evaluate(self, pt, params, src_pts):
    assert len(params) - 3 == len(src_pts)
    value = 0
    for i in range(len(params) - 3):
      value += params[i] * self.__tps(src_pts[i], pt)
    value += params[-3] + params[-2] * pt[0] + params[-1] * pt[1]
    return value

  def __get_mapped_pt(self, pt, params_x, params_y, src_pts):
    dx_recon = self.__evaluate(pt, params_x, src_pts)
    dy_recon = self.__evaluate(pt, params_y, src_pts)
    return [pt[0] + dx_recon, pt[1] + dy_recon]

  # TODO acceleration
  def warpImage(self, img_src):
    if self.params_x_dst2src is None or self.params_y_dst2src is None:
      self.__mapping_dst2src()
    img_dst = np.zeros(img_src.shape, np.uint8)
    for y in range(img_src.shape[0]):
      for x in range(img_src.shape[1]):
        pt_src = self.__get_mapped_pt([x, y], self.params_x_dst2src, self.params_y_dst2src, self.dst_pts)
        # bilinear interpolation to get the image
        x1 = int(np.floor(pt_src[0]))
        x2 = int(np.ceil(pt_src[0]))
        rx = pt_src[0] - x1
        y1 = int(np.floor(pt_src[1]))
        y2 = int(np.ceil(pt_src[1]))
        ry = pt_src[1] - y1
        tl = img_src[y1][x1] if x1 >= 0 and x1 <= img_src.shape[1] - 1 and y1 >= 0 and y1 <= img_src.shape[0] - 1 else np.asarray([0, 0, 0])
        tr = img_src[y1][x2] if x2 >= 0 and x2 <= img_src.shape[1] - 1 and y1 >= 0 and y1 <= img_src.shape[0] - 1 else np.asarray([0, 0, 0])
        bl = img_src[y2][x1] if x1 >= 0 and x1 <= img_src.shape[1] - 1 and y2 >= 0 and y2 <= img_src.shape[0] - 1 else np.asarray([0, 0, 0])
        br = img_src[y2][x2] if x2 >= 0 and x2 <= img_src.shape[1] - 1 and y2 >= 0 and y2 <= img_src.shape[0] - 1 else np.asarray([0, 0, 0])
        img_dst[y][x] = np.round((1-ry) * (1-rx) * tl + (1-ry) * rx * tr + ry * (1-rx) * bl + ry * rx * br)
    return img_dst
  
  def applyTransformation(self, src_pts):
    if self.params_x_src2dst is None or self.params_y_src2dst is None:
      self.__mapping_src2dst()
    dst_pts = []
    for i in range(len(src_pts)):
      # print(i, end=" ")
      dst_pts.append(self.__get_mapped_pt(src_pts[i], self.params_x_src2dst, self.params_y_src2dst, self.src_pts))
    return dst_pts
