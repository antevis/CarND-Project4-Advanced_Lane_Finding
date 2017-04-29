import glob
import numpy as np
from tqdm import tqdm
import matplotlib.image as mpimg
import cv2
import pickle
import helper as aux


def saveToFile(mtx, dist, rvecs, tvecs, filename):
    """
    :param mtx: 3x3 floating-point camera matrix
    :param dist: Vector of distortion coefficients
    :param rvecs: Vector of rotation vectors
    :param tvecs: Vector of translation vectors estimated for each pattern view
    :param filename: File to save
    :return: void
    """
    data = {'cameraMatrix': mtx,
            'distCoeffs': dist,
            'rvecs': rvecs,
            'tvecs': tvecs}
    pickle.dump(data, open(filename, 'wb'))


def getObjectImagePoints(dx, dy, calibrationFolder='camera_cal'):
    """
    Getting object and image points for calibration
    :param calibrationFolder: folder with files for calibration
    :param dx: number of corners horizontally
    :param dy: number of corners vertically
    :return: objPoints, imgPoints, image shape
    """
    objpoints = []  # 3D points in real world space
    imgpoints = []  # 2D points in image plane

    fileMask = '{}/calibration*.jpg'.format(calibrationFolder)
    images = glob.glob(fileMask)

    objp = np.zeros((dy * dx, 3), np.float32)
    objp[:, :2] = np.mgrid[0:dx, 0:dy].T.reshape(-1, 2)

    cv_img_shape = None

    for fname in tqdm(images):

        img = mpimg.imread(fname)

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, (dx, dy), None)

        if ret:
            imgpoints.append(corners)
            objpoints.append(objp)

        if cv_img_shape is None:
            cv_img_shape = gray.shape[::-1]

    return objpoints, imgpoints, cv_img_shape


def main():
    dx = aux.promptForInt('Please specify number of corners horizontally: ')
    dy = aux.promptForInt('Please specify number of corners vertically:   ')

    objpoints, imgpoints, img_shape = getObjectImagePoints(dx=dx, dy=dy)

    try:

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints,
                                                           imgpoints,
                                                           img_shape,
                                                           None, None)
    except cv2.error:
        print('calibration failed. Most likely not all images contain {}x{} corners'.format(dx, dy))
        return 1

    if ret:
        print('Calibration succeeded.')
        calib_file_name = 'calibration_data.p'
        try:
            saveToFile(mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs, filename=calib_file_name)
            print('calibration data saved to file {}'.format(calib_file_name))
        except IOError:
            print('Saving calibration data might have failed.')
    else:
        print('Camera calibration failed.')


if __name__ == '__main__':
    main()
