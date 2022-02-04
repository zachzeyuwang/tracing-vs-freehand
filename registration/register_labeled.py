import cv2
import json
import os
import sys
import numpy as np
import SimpleITK as sitk
from ThinPlateSplineShapeTransformer import ThinPlateSplineShapeTransformer

def command_iteration(method) :
    # if (method.GetOptimizerIteration() == 0):
    #     print("\tLevel: {0}".format(method.GetCurrentLevel()))
    #     print("\tScales: {0}".format(method.GetOptimizerScales()))
    # print("#{0}".format(method.GetOptimizerIteration()))
    # print("\tMetric Value: {0:10.5f}".format( method.GetMetricValue()))
    # print("\tLearningRate: {0:10.5f}".format(method.GetOptimizerLearningRate()))
    # if (method.GetOptimizerConvergenceValue() != sys.float_info.max):
    #     print("\tConvergence Value: {0:.5e}".format(method.GetOptimizerConvergenceValue()))
    return

def command_multiresolution_iteration(method):
    # print("\tStop Condition: {0}".format(method.GetOptimizerStopConditionDescription()))
    # print("============= Resolution Change =============")
    return

def init_displacement_field_TPS(image, uid):
  with open("fiducials.json") as f:
    fiducials = json.load(f)
  src_db = fiducials[image][""]
  dst_db = fiducials[image][uid]
  src = []
  dst = []
  for xy_src, xy_dst in zip(src_db.split(","), dst_db.split(",")):
    if xy_dst != "":
      src.append(float(xy_src))
      dst.append(float(xy_dst))
  assert len(src) == len(dst)
  src = np.asarray(src).reshape(-1, 2).tolist()
  dst = np.asarray(dst).reshape(-1, 2).tolist()
  tps = ThinPlateSplineShapeTransformer(dst, src)   
  step_size = 4
  df = np.zeros((256 // step_size, 256 // step_size, 2), np.float64)
  pts = [[x * step_size / 255 * 799, y * step_size / 255 * 799] for y in range(256 // step_size) for x in range(256 // step_size)]
  # print("Sampling %s points from fiducial-based TPS..." % len(pts))
  pts_warped = tps.applyTransformation(pts)
  for y in range(256 // step_size):
    for x in range(256 // step_size):
      df[y][x][0] = pts_warped[y * 256 // step_size + x][0] / 799 * 255 - x * step_size
      df[y][x][1] = pts_warped[y * 256 // step_size + x][1] / 799 * 255 - y * step_size
  df = cv2.resize(df, (256, 256))
  return df

if len ( sys.argv ) != 3:
    print( "Usage: {0} <IMAGE_FILENAME.png> <PARTICIPANT_ID>".format(sys.argv[0]))
    sys.exit ( 1 )

image = sys.argv[1]
uid = sys.argv[2]
print("Registering with labeled fiducials: %s %s" % (image, uid))


kernel = np.ones((3, 3), np.uint8)
fixed_0_np = cv2.imread("../data/png/drawings/%s&%s.png" % (image[:-4], uid), cv2.IMREAD_GRAYSCALE)
_, fixed_0_np = cv2.threshold(fixed_0_np, 127, 255, cv2.THRESH_BINARY_INV)
fixed_0_np = cv2.dilate(fixed_0_np, kernel, iterations=2)
fixed_0_np = cv2.resize(fixed_0_np, (256, 256))
cv2.imwrite("./visual_labeled/%s_%s_input1.png" % (image[:-4], uid), 255 - fixed_0_np)
fixed_0 = sitk.GetImageFromArray(fixed_0_np.astype(np.float32))

moving_0_np = 255 - cv2.imread("../data/density/density&%s&2.png" % image[:-4], cv2.IMREAD_GRAYSCALE)
moving_0_np = cv2.resize(moving_0_np, (256, 256))
cv2.imwrite("./visual_labeled/%s_%s_input2.png" % (image[:-4], uid), 255 - moving_0_np)
moving_0 = sitk.GetImageFromArray(moving_0_np.astype(np.float32))

# init with fiducials TPS

# displacement
displacement_field_np = init_displacement_field_TPS(image, uid)
displacement_field = sitk.GetImageFromArray(displacement_field_np, isVector=True)
displacement_field.CopyInformation(fixed_0)
tx = sitk.DisplacementFieldTransform(displacement_field)
tx.SetSmoothingGaussianOnUpdate()
del displacement_field

R = sitk.ImageRegistrationMethod()
R.SetMetricAsANTSNeighborhoodCorrelation(16)
R.SetOptimizerAsGradientDescent(learningRate=1,
                                numberOfIterations=300,
                                estimateLearningRate=R.EachIteration)
R.SetOptimizerScalesFromPhysicalShift()

R.SetInitialTransform(tx, inPlace=True)
R.SetInterpolator(sitk.sitkLinear)

R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R) )
outTx = R.Execute(fixed_0, moving_0)

sitk.WriteTransform(outTx, "./transform_labeled/transform_%s_%s.txt" % (image[:-4], uid))

if ( not "SITK_NOSHOW" in os.environ ):

    # sitk.Show(displacementTx.GetDisplacementField(), "Displacement Field")

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed_0)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(0)
    resampler.SetTransform(outTx)

    out_0 = resampler.Execute(moving_0)
    out_0_np = sitk.GetArrayFromImage(out_0)
    cv2.imwrite("./visual_labeled/%s_%s_output.png" % (image[:-4], uid), 255 - out_0_np)
