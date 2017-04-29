import cv2
import numpy as np
import matplotlib.pyplot as plt


# Prompt for limited number of options
def promptForInputCategorical(message, options):
    """
    Prompts for user input with limited number of options (not used in this project)
    :param message: Message displayed to the user
    :param options: limited number of options. 
    Prompt will repeat until one of provided options typed correctly
    :return: user response
    """
    response = ''

    options_list = ', '.join(options)

    while response not in options:
        response = input('{} ({}): '.format(message, options_list))

    return response


def promptForInt(message):
    """
    Prompting for Integer input
    :param message: Informative message when prompting for integer input
    :return: integer input
    """
    result = None

    while result is None:
        try:
            result = int(input(message))
        except ValueError:
            pass
    return result


def promptForFloat(message):
    """
    Prompting for Float
    :param message: Informative message when prompting for float input
    :return: integer input
    """
    result = None

    while result is None:
        try:
            result = float(input(message))
        except ValueError:
            pass
    return result


def putThrs(img, low, high):
    """
    Was used at the stage when determining thresholds for binarization
    """
    cv2.putText(img=img,
                text='low threshold: {}, high threshold: {})'.format(low, high),
                org=(100, 100),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1,
                color=(255, 0, 0),
                thickness=3)


def putText(img, text, origin=(100, 100), scale=1.0, color=(255, 0, 0), thickness=2):
    """
    Wrapper for OpenCV putText()
    :param img: 
    :param text: 
    :param origin: 
    :param scale: 
    :param color: 
    :param thickness: 
    :return: 
    """
    cv2.putText(img=img,
                text=text,
                org=origin,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=scale,
                color=color,
                thickness=thickness)


def drawRect(img, lx, ly, rx, ry, color=(0, 255, 0), thickness=2):
    """
    Wrapper for OpenCV rectangle
    :param img: 
    :param lx: 
    :param ly: 
    :param rx: 
    :param ry: 
    :param color: 
    :param thickness: 
    :return: 
    """
    cv2.rectangle(img=img, pt1=(lx, ly), pt2=(rx, ry), color=color, thickness=thickness)


def funcSpace(argSpace, fitParams):
    """
    Creates a space of quadratic function f(y) = ay^2 + by + c values given a space of variables
    :param argSpace: space of variables, may be a single value
    :param fitParams: 
    :return: space of function values
    """
    a = fitParams[0]
    b = fitParams[1]
    c = fitParams[2]

    return a * (argSpace ** 2) + b * argSpace + c


def curvature(fitParams, variable, scale=1):
    """
    :param fitParams: 2nd order polynomial params (a, b, c in f(y) = ay^2 + by + c). Passing just a tuple of
    'a' and 'b' is enough
    :param variable: the point where curvature being evaluated (passing 'linspace' should return an array of curvatures
    for a given linspace.
    :param scale: number of units per pixel
    :return: value of curvature in units
    """
    a = fitParams[0]
    b = fitParams[1]

    return ((1 + (2 * a * variable * scale + b) ** 2) ** 1.5) / np.absolute(2 * a)


def plot(img, figsize=(12, 12), title=None, axis='off', cmap=None):
    """
    Wrapper for matplotlib.pyplot imshow. Used for jupyter notebook
    :param img: 
    :param figsize: 
    :param title: 
    :param axis: 
    :param cmap: 
    :return: 
    """
    plt.figure(figsize=figsize)
    if title is not None:
        plt.title(title)
    plt.axis(axis)
    if cmap is not None:
        plt.imshow(img, cmap=cmap)
    else:
        plt.imshow(img)
