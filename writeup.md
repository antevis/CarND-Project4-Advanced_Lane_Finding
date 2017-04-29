##Writeup

---

**Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[image1]: ./writeup_support_imgs/originalChecker.png "Original checker image"
[image2]: ./writeup_support_imgs/undistortedChecker.png "Undistorted checker image"
[image3]: ./writeup_support_imgs/originalRoad.png "Original Road"
[image4]: ./writeup_support_imgs/undistortedRoad.png "Sample with corrected distortion"
[image5]: ./writeup_support_imgs/undistortionEffect.png "Effect of undistortion"
[image6]: ./writeup_support_imgs/comboBinary.png "Combined binary"
[image7]: ./writeup_support_imgs/straight1_perspectiveCoords.png "Straight lane 1"
[image8]: ./writeup_support_imgs/straight2_perspectiveCoords.png "Straight lane 2"
[image9]: ./writeup_support_imgs/comboBinaryWarpedStd.png "Standard warped image"
[image10]: ./writeup_support_imgs/comboBinaryWide.png "Binary augmented with margins"
[image11]: ./writeup_support_imgs/comboBinaryWarpedWide.png "Augmented warped image"
[image12]: ./writeup_support_imgs/unsufficientMargin.png "Straight lane 2"
[image13]: ./writeup_support_imgs/undistLaneCurvatureOffset.png "Resulting image"

[video1]: ./project_video_out.mp4 "Video"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points
###Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
###Camera Calibration

Camera calibration has been implemented in ```calibrateCam.py```. It assumes that there's a folder ```camera_cal```,
containing calibration files ```calibration*.jpg```. Camera Calibration may be invoked directly from the Terminal as follows:
```python calibrateCam.py```.
It will prompt for number of corners both horizontally and vertically. The numbers are
```9``` and ```5``` respectively, as each image appears to contain at least that number of valid corners.
Here is the output:
```
Please specify number of corners horizontally: 9
Please specify number of corners vertically:   5
100%|███████████████████████████████████████████| 20/20 [00:41<00:00,  2.51s/it]
Calibration succeeded.
calibration data saved to file calibration_data.p
```
As can be seen above, the resulting calibration data saved to ```calibration_data.p```. The file contains a pickled
(serialized) dictionary with the following keys:

```cameraMatrix```, ```distCoeffs```, ```rvecs```, ```tvecs```

Internally, my implementation of camera calibration process replicates the one introduced at the lesson and utilizes 
OpenCV built-in functionality. It contains the following steps:

1. Generate a grid of ```objectPoints``` (lines ```40```, ```41``` in ```calibrateCam.py```, 
function ```getObjectImagePoints(...)```). Next is an explanation provided in the template which leaves little to add: 
"These are the ```(x, y, z)``` coordinates of the chessboard corners in the world. It is assumed that the chessboard is 
fixed on the ```(x, y)``` plane at ```z=0```, such that the object points are the same for each calibration image. 
Thus, ```objp``` is just a replicated array of coordinates, and objpoints will be appended with a copy of it with each 
successful detection of all chessboard corners in a given image. ```imgpoints``` will be appended with the ```(x, y)```
pixel position of each of the corners in the image plane with each successful chessboard detection."
2. Extract corners from all provided calibration files using OpenCV ```findChessboardCorners(...)``` function
3. Using corners extracted in previous step, obtain calibration data using OpenCV ```cv2.calibrateCamera(...)``` function
4. If data has been successfully obtained, store it in above mentioned pickle for future use.

Class ```Processing``` of ```imageProcessing.py``` module loads calibration data from disk and contains wrapper for
```cv2.undistort()``` that can be invoked to apply distortion correction with the available calibration data.
Here are the results:

![alt text][image1] ![alt text][image2]

###Pipeline demo on single image

####1. Distortion correction

#####Original image:

![alt text][image3]

#####Undistorted image:

![alt text][image4]

To emphasize the difference between the original and undistorted, here are two images combined:

![alt text][image5]

####2. Getting threshold binary

After numerous trials, I picked the following formula to obtain a final binary thresholded image:

```combined[((r == 1) & (s == 1) | abs == 1)] = 1```,

where ```r``` is a binary of ```red``` plane within an ```RGB``` color space with thresholds of ```(200, 255)```, 
```s``` is a binary of ```saturation``` plane within a ```HLS``` color space with thresholds of ```(90, 255)```, and
```abs``` is an absolute value of ```Sobel``` operator applied in ```x``` direction with thresholds of ```(20, 255)```.

The corresponding algorithm is implemented in the ```combiThreshold``` function of the ```Thresholding``` class 
within the ```imageProcessing.py``` module (lines 130-152).

Here's an example of my output for this step:

![alt text][image6]

####3. Perspective transformation

To obtain coordinates for proper perspective transformation, both files with straight lanes have been examined:

![alt text][image7]

![alt text][image8]

The vehicle in the project video is being driven in the leftmost lane, so the coordinates from the first image has been
picked for the perspective transformation:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 596, 450      | 204, 0        | 
| 204, 719      | 204, 719      |
| 1108, 719     | 1108, 719     |
| 684, 450      | 1108, 0       |

Perspective transformation is implemented in ```Warping``` class of ```imageProcessing.py``` module.
It contains an initializer with hard-coded coordinates for source and destination images, and 3 methods:
```warp()```, ```birdEye()``` and ```perspective()```. ```warp()``` function is actually a convenience wrapper for
```cv2.warpPerspective()```.

```birdEye()``` function transforms perspective view to bird-eye projection.

```perspective()``` function projects bird-eye view back to perspective.

Both ```birdEye()``` and ```perspective()``` functions use ```warp()``` wrapper under the hood, 
inversely switching source and destination coordinates.
 
When performing bird-eye projection, a lot of useful image data may be lost, especially in cases where the lane is curved:

![alt text][image9]

As can be seen, right line is almost completely clamped out of the image as a result of bird-eye transformation, 
which would severely aggravate the accuracy of subsequent line detection.

This can be addressed by introducing the external margins to the left and right side of the image:

![alt text][image10]

Binary image augmented with additional 'margins' of 320 px width each.
The graphical content of those margins doesn't matter, so we fill it with zeros.

Margin width passed to ```perspective()``` and ```birdEye()``` functions as a ```leftShift``` parameter, 
where it's being used to adjust source and destination coordinates along x axis for proper perspective transform.
As a result, bird-eye projection of the same image looks like this:

![alt text][image11]

Obviously this would allow to detect right line much higher precision. However, there may be situations when even such
margin augmentation would not be sufficient to fully accommodate the line, meaning that it would still intersect y axis
beyond the visible width of the image:

![alt text][image12]

Ignoring this situation will affect the final projected lane image, expressed in upper boundary to not being a straight
horizontal line. To address this, we can evaluate the ```C``` argument of the 2-nd order polynomial ```x = Ay^2 + By + C```
and further expand the left and/or right margin accordingly. This adjustment is implemented in ```addPolygon()``` function
within the ```Drawing``` class of ```imageProcessing.py``` module, lines 244-246.


####4. Lines detection

For more consistent and robust lane detection I've created a ```Line``` class which keeps track of detected lines and manages 
subsequent detections. It contains the following properties:

* **lineSpace**, which makes the line aware of whether it is LEFT or RIGHT
* **fits** - which is a list of previously detected lines
* **depth** - which is a number of lines to keep in **fits** list
* **margin** - the margin in pixels denoting the areas of search to the left and right from the center line
* **windowSplit** - denoting which part of the image to use for histogram evaluation. 
(2 means that lower half of the image will be used)
* **winCount** - number of windows to split the image height into for initial box search
* **searchPortion** - the vertical share of the image used for searching, from the bottom up.
with Bird-eye projection higher pixels contain less meaningful information for lane detection for obvious reasons.

The core function of the ```Line``` class is ```getFit()```. It accepts the binary bird-eye projection image and performs 
one of two types of line searching:
* **Box Search** - if no fits have been previously detected (or previous fits have been reset)
* **Look Ahead Search** - uses previously detected fits as a guidance for searching region of interest.

After obtaining new fit with one of the above mentioned methods, it is being added to the list of ```fits``` and a current
fit calculated as a weighted average of all previously found fits in ```currentFit()``` function. Worth mentioning that
standard ```numpy.average``` to obtain weighted average with weights performs really not as expected and can't be used here. 

Thus, I've implemented weighted average myself the way it is intended to work and provide meaningful results. The weights
themselves are calculated in ```getWeights()``` function and employ the following logic:

* Slope weights take steepness of curvature (A in polynomial coefficients) and give more weight to more vertical lines
* Vertex weights are the ```y``` coordinate where parabola turns. Considered that the lower it is, the higher the weight
should be
* Age weights - the younger the fit, the heavier its weight.

Then I compute cumulative weight as a product of all three and normalize it between 0 and 1



Both algorithms have been implemented in the ```LaneFinding.py``` module. They closely replicate those 
introduced it the corresponding lessons, but one aspect of **Look Ahead** search deserves a separate description.

Instead of simply using search area with the given margin to the left and right of previously detected curve, 
I've introduced a concept of ```borderFit```, which offers a region of interest outstanding to a given margin from the 
center fit not horizontally but rather as a perpendicular to the tangent line at each point of the center fit. 
This helps to avoid narrowing the search area at the top of the image, where line curvature may be significant and simple
horizontal margins may not cover all width of curved line. The logic implemented in ```LaneFinding.borderFit()``` method of 
```LaneFinding.py``` module. Internally, it computes coordinates outstanding by a given margin perpendicularly 
to the tangent of center fit at each point and approximates new polynomials for those points.

The management of lines detection process has been implemented in ```LineDetector.py``` module with the core pipeline focused in 
```embedLane()``` function. It accepts the raw source image and returns undistorted image with the embedded lane
(if both lines have been detected and accepted as valid) and some telemetry data, such as estimated lane curvature and
vehicle's offset from the lane center. The process comprises the following steps:
1. Undistortion using ```undistort()``` function described earlier
2. Binarization and bird-eye projection. This two steps combined in ```preProcess()``` function which internally uses
```Thresholding``` and ```Warping``` classes
3. Getting fits with ```Line.getFits()``` function which internally decides how to search for a new fit.
4. Performing **Sanity Check**. The logic I've employed here includes checking for left and right curvatures similarity
and lane width to be within a given range.
5. If **Sanity Check** passes, we add Lane polygon to the undistorted image, otherwise we evaluate whether it may be feasible
to reject the last found fit and re-scan again with the **Box Search**, ignoring guidance of previously detected lines. 
At this stage we either re-scan with Box Search not deleting previous fits, or reset all previous fits and start a new 
Box Search from scratch.
After that we perform **Sanity Check** again and if it passes, add Lane polygon to the undistorted image.
Otherwise, we just don't add anything.
6. For visualization purposes, along with the fit itself, ```getFit``` returns an image of warped binary with the 
search results visualized. Here we use those images to add them to the result image as a semi-transparent Picture-in-picture.
7. Adding curvature and offset data using ```addCurvatureStamp()``` and ```addOffsetStamp()``` methods.

This is an example of how a particular resulting image looks like:

![alt text][image13]

---

###Pipeline (video)

Line detection in a video file may be invoked directly from the Terminal as follows:
```python LineDetector.py```. It will prompt for relevant parameters, perform detection in each frame and save the result
to a new video clip with '_out' postfix appended to the end of the source video clip.
The output might look something like this:

```bash
Enter video file name: project_video.mp4
Enter history depth in frames: 5
Enter Search Margin: 100
Enter filler width: 320
Enter Window Split: 2
Enter Window Count for Box Search: 18
Enter the Search portion (0.0 - 1.0): 1.
Enter Picture-in-picture alpha: (0.0 - 1.0): 0.8
Enter Picture-in-picture scale (0.0 - 1.0): .33
Total frames: 1260.0
1260it [04:02,  4.57it/s]
[MoviePy] >>>> Building video project_video_out.mp4
[MoviePy] Writing video project_video_out.mp4
100%|███████████████████████████████████████| 1260/1260 [00:44<00:00, 31.68it/s]
[MoviePy] Done.
[MoviePy] >>>> Video ready: project_video_out.mp4 
```

Here's a [link to my video result](./project_video_out.mp4)

---

###Discussion

I've tried to employ the convolutional approach, and there is a method ```convolutional_search``` in
```LaneFinding.py```, but found the result unsatisfactory.

I've invested A LOT of time (literally, weeks) trying to solve for the ```harder_challenge_video.mp4```, but the result
is still miserable and doesn't worth sharing. I should point out that the conditions in the ```harder_challenge_video.mp4```
footage are not quite realistic for the production environment, as the real camera used for line detection should be 
sealed in a hermetic compartment, eliminating those effects of sunlight reflection off dirty windshield glass.

A lot of time has been spent on deriving the thresholding combination (which is obviously not optimal), 
and it is sort of re-inventing the wheel, as the optimal parameters has already been figured out by someone before. 
IMO, solving for ```challenge_video.mp4``` is mostly a matter of finding optimal thresholding parameters.
 
**Sanity Check** logic may definitely be more sophisticated than my implementation, but for ```project_video.mp4``` 
it is OK. In fact, it seems that initial **Box Search** has been performed only once at the first frame and all 
subsequent searches employed **Look Ahead**, that is, the lines have never been lost through the rest of the clip.

When detecting lanes in a video, algorithm processes roughly 6 frames per second on MacBook Pro i7 mid 2014 machine.
Skipping visualization would yield a slight performance increase, but it still would not be even close to real time detection.