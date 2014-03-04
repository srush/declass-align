"""
Some basic image processing helper functions.
"""

import cv2
import numpy as np
import numpy.linalg
import math
import difflib

def fuzzy_box_align(boxes1, boxes2):
    differ = difflib.SequenceMatcher(
        None,
        [FuzzyBox(t) for t in boxes1], 
        [FuzzyBox(t) for t in boxes2], 
        autojunk=None)
    return differ.get_opcodes()

class FuzzyBox:
    def __init__(self, box):
        (x, y, height, width) = box
        self.y = y
        
    def __eq__(self, o):
        return abs(self.y - o.y) < 10

    def __hash__(self):
        return hash(self.y)


def crop_image(image, border=100):
    return image[border:-border, border:-border]

def rotate_image(image, angle):
    """
    Rotate an image by an angle

    Parameters 
    ----------
    image : Numpy Matrix

    angle : float
        An angle in degrees.

    Returns 
    --------
    
    """
    image_center = tuple(np.array(image.shape) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle,1.0)
    result = cv2.warpAffine(image, rot_mat, 
                            (image.shape[1], image.shape[0]), 
                            flags=cv2.INTER_LINEAR)
    return result

def l2_distance(pt1, pt2):
    """
    Returns the l2 distance between two points.
    
    Parameters
    ------------
    pt1, pt2 : two opencv points.

    """
    diff = abs(np.array(pt1) - numpy.array(pt2))
    return numpy.linalg.norm(diff)

def angle(pt1, pt2):
    """
    Compute the angle frow two points.

    Parameters
    ------------
    pt1, pt2 : two opencv points.
    
    Returns
    ---------
    angle : 
        The angle in degrees.
    """
    xDiff = pt2[0] - pt1[0];
    yDiff = pt2[1] - pt1[1];
    return math.atan2(yDiff, xDiff) * (180 / math.pi)


def make_side_by_side(im1, im2):
    """
    Draws a new image with both images side by side.

    Parameters
    ---------
    im1, im2 : Images

    
    Return
    --------
    newimg
    """
    h1, w1 = im1.shape[:2]
    h2, w2 = im2.shape[:2]
    nWidth = w1+w2
    nHeight = max(h1, h2)
    hdif = (h1-h2)/2
    newimg = np.zeros((nHeight, nWidth, 3), np.uint8)
    newimg[:h1, :w1] = im1
    newimg[:h2, w1:w1+w2] = im2
    return newimg


def warp_image_from_match(im1, im2, points1, points2):
    """
    Warp the image based on RANSAC matching.

    Parameters
    ----------
    im1, im2: Two images
    
    points1, point2 : Keypoints
       Matched key points from im1 and im2.
    """
    
    val, trans = cv2.findHomography(points2, points1, cv2.RANSAC)
    return cv2.warpPerspective(im2, val, (im1.shape[1], im1.shape[0]))

def remove_blobs(image, max_area=1000, min_height=5):
    """
    Remove blobs with thresholed size from the image.

    Parameters
    ------------
    image : Numpy array

    max_area : float
        Area threshold

    min_height : float
        Height threshold

    Returns
    -------
    newimage : Numpy array
        The image with blobs removed

    """
    ret, img2 = cv2.threshold(image, 250, 255, 1)
    contours, hier = cv2.findContours(np.array(img2), 
                                      cv2.RETR_LIST, 
                                      cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros(img2.shape, np.uint8)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, width, height = cv2.boundingRect(cnt)
        if cv2.contourArea(cnt) > max_area or height < min_height:
            cv2.drawContours(mask,[cnt],0, 255, -1)
 
    return cv2.bitwise_and(img2, cv2.bitwise_not(mask))
