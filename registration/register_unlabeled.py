import cv2
import sys
import os
import numpy as np
import SimpleITK as sitk

# def command_iteration(method) :
    # if (method.GetOptimizerIteration() == 0):
    #     print("\tLevel: {0}".format(method.GetCurrentLevel()))
    #     print("\tScales: {0}".format(method.GetOptimizerScales()))
    # print("#{0}".format(method.GetOptimizerIteration()))
    # print("\tMetric Value: {0:10.5f}".format( method.GetMetricValue()))
    # print("\tLearningRate: {0:10.5f}".format(method.GetOptimizerLearningRate()))
    # if (method.GetOptimizerConvergenceValue() != sys.float_info.max):
    #     print("\tConvergence Value: {0:.5e}".format(method.GetOptimizerConvergenceValue()))

# def command_multiresolution_iteration(method):
#     print("\tStop Condition: {0}".format(method.GetOptimizerStopConditionDescription()))
#     print("============= Resolution Change =============")

if len ( sys.argv ) != 3:
    print( "Usage: {0} <IMAGE_FILENAME.png> <PARTICIPANT_ID>".format(sys.argv[0]))
    sys.exit ( 1 )

image = sys.argv[1]
uid = sys.argv[2]
print("Registering without labeled fiducials: %s %s" % (image, uid))


kernel = np.ones((3, 3), np.uint8)
fixed_0_np = cv2.imread("../data/png/drawings/%s&%s.png" % (image[:-4], uid), cv2.IMREAD_GRAYSCALE)
_, fixed_0_np = cv2.threshold(fixed_0_np, 127, 255, cv2.THRESH_BINARY_INV)
fixed_0_np = cv2.dilate(fixed_0_np, kernel, iterations=2)
fixed_0_np = cv2.resize(fixed_0_np, (256, 256))
cv2.imwrite("./visual_unlabeled/%s_%s_input1.png" % (image[:-4], uid), 255 - fixed_0_np)
fixed_0 = sitk.GetImageFromArray(fixed_0_np.astype(np.float32))

moving_0_np = 255 - cv2.imread("../data/density/density&%s&2.png" % image[:-4], cv2.IMREAD_GRAYSCALE)
# moving_0_np = 255 - cv2.imread("./imgprop/imgprop_%s.png" % image[:-4], cv2.IMREAD_GRAYSCALE)
moving_0_np = cv2.resize(moving_0_np, (256, 256))
cv2.imwrite("./visual_unlabeled/%s_%s_input2.png" % (image[:-4], uid), 255 - moving_0_np)
moving_0 = sitk.GetImageFromArray(moving_0_np.astype(np.float32))

fixed_0, moving_0 = moving_0, fixed_0 # for SIGGRAPH talk vis
mulres = 0

# affine
tx = sitk.CenteredTransformInitializer(fixed_0, moving_0, sitk.AffineTransform(fixed_0.GetDimension()))
R = sitk.ImageRegistrationMethod()

R.SetMetricAsCorrelation()
R.SetOptimizerAsGradientDescent(learningRate=1.0,
                                numberOfIterations=100,
                                estimateLearningRate = R.EachIteration)
R.SetOptimizerScalesFromPhysicalShift() # important!

R.SetInitialTransform(tx, inPlace=True)
R.SetInterpolator(sitk.sitkLinear)


def command_iteration(method, prefix) :
    
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed_0)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(0)

    if prefix == "b":        
        txx = sitk.CompositeTransform( [method.GetMovingInitialTransform(), method.GetInitialTransform()] )
        # txx = method.GetMovingInitialTransform()
        # txx.AddTransform(method.GetInitialTransform())
        resampler.SetTransform(txx)
    else:
        resampler.SetTransform(method.GetInitialTransform())

    out_0 = resampler.Execute(moving_0)
    out_0_np = sitk.GetArrayFromImage(out_0)
    # skip writing intermediate images
    # cv2.imwrite("./visual_unlabeled/%s_%d_%03d.png" % (prefix, mulres, method.GetOptimizerIteration()), 255 - out_0_np)
    

R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R, "a") )
outTx = R.Execute(fixed_0, moving_0)

# bspline
transformDomainMeshSize = [2] * moving_0.GetDimension()
tx = sitk.BSplineTransformInitializer(fixed_0, transformDomainMeshSize)

R = sitk.ImageRegistrationMethod()
R.SetMetricAsCorrelation()
R.SetOptimizerAsGradientDescentLineSearch(5.0,
                                          100,
                                          convergenceMinimumValue=1e-4,
                                          convergenceWindowSize=5)

R.SetMovingInitialTransform(outTx)
R.SetInitialTransformAsBSpline(tx, inPlace=True, scaleFactors=[1, 2, 4])
R.SetInterpolator(sitk.sitkLinear)

R.SetShrinkFactorsPerLevel([4, 2, 1])
R.SetSmoothingSigmasPerLevel([4, 2, 1])

def command_multiresolution_iteration(method):
    # print("\tStop Condition: {0}".format(method.GetOptimizerStopConditionDescription()))
    # print("============= Resolution Change =============")
    global mulres
    mulres += 1
    
R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R, "b") )
R.AddCommand( sitk.sitkMultiResolutionIterationEvent, lambda: command_multiresolution_iteration(R) )
outTx = sitk.CompositeTransform( [outTx, R.Execute(fixed_0, moving_0)] )
# outTx.AddTransform( R.Execute(fixed_0, moving_0) )

# displacement
displacement_field = sitk.TransformToDisplacementField(outTx,
                                                      sitk.sitkVectorFloat64,
                                                      fixed_0.GetSize(),
                                                      fixed_0.GetOrigin(),
                                                      fixed_0.GetSpacing(),
                                                      fixed_0.GetDirection())
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

R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R, "c") )
outTx = R.Execute(fixed_0, moving_0)

sitk.WriteTransform(outTx, "./transform_unlabeled/transform_%s_%s.txt" % (image[:-4], uid))

if ( not "SITK_NOSHOW" in os.environ ):

    # sitk.Show(displacementTx.GetDisplacementField(), "Displacement Field")

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed_0)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(0)
    resampler.SetTransform(outTx)

    out_0 = resampler.Execute(moving_0)
    out_0_np = sitk.GetArrayFromImage(out_0)
    cv2.imwrite("./visual_unlabeled/%s_%s_output.png" % (image[:-4], uid), 255 - out_0_np)
