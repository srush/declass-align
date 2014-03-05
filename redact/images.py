"""
Code for converting images to layouts.
"""

from random import random
import cv2
from redact.image_utils import *
import math
import matplotlib.pyplot as plt
import numpy as np
import numpy.linalg
import scipy.ndimage as ndimage
import sys
from itertools import izip

PARAMS = {
  "feature_score": 5000
}

FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing

flann_params = dict(algorithm = FLANN_INDEX_KDTREE,
                    trees = 4)

def make_boxes(im1, im2):
    warp = align_images(im1, im2)
    im1 = clean_text_image(im1)
    im2 = clean_text_image(warp)
    return (find_lines(im1), find_lines(im2))

def clean_text_image(image):
    """
    Run a preprocessing pipeline on an image with text.
    
    Parameters. 
    """
    ret = remove_blobs(crop_image(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)))
    angle = estimate_skew(ret)
    return rotate_image(ret, angle)    

def align_images(im1, im2):
    """
    
    """

    pairs, key1, key2 = align_image_keypoints(im1, im2)
    points1 = np.array([key1[point].pt for point, _ in pairs])
    points2 = np.array([key2[point].pt for _, point in pairs])
    return warp_image_from_match(im1, im2, points1, points2)


def make_surf_detector():
    return cv2.SURF(500, 4, 2, False, True)

def compute_features(detector, img):
    """
    Compute image descriptors and key points from an image.

    Parameters
    ----------
    detector : Feature detector

    img : numpy matrix

    Returns
    ---------
    keypoints, descriptors 
    """
    return detector.detectAndCompute(img, None)


def get_nearest_neighbors(desc1, desc2):
    """
    Parameters
    ----------
    desc1, desc2 : lists of descriptors
        Feature descriptors.
    
    Returns
    --------
    points : list of list of pairs 
        For each descriptor in desc1, the n-best matches as an index and distance pair.
    """    

    flann = cv2.flann_Index(desc2, flann_params)
    idx2, dist = flann.knnSearch(desc1, 5, params = {}) 
    return [zip(matches, dists)
            for matches, dists in izip(idx2, dist)]

def align_features(key1, key2, matches, max_dist = 0.05):
    """
    Nearest neighbors matching of sets of features.
    
    Parameters
    ----------
    
    key1, key2 : Key points
    
    """
    final_matches = [-1] * len(key1)
    for id1, nbest in enumerate(matches): 
        best = 100
        for id2, dist in nbest:

            # Check1: Check if the descriptor distance is within threshold. 
            if dist > max_dist: continue
            
            # Check2: Keep the closest with keypoint distance is within threshold. 
            l2 = l2_distance(key1[id1].pt, key2[id2].pt)
            if l2 < best:
                best = l2 
                final_matches[id1] = id2
                break

    return [(i, m) for i, m in enumerate(final_matches) if m != -1] 


def align_image_keypoints(im1, im2):
    """
    Aligns the keypoints of two images.
    
    Parameters
    ---------
    im1, im2 : Images
    
    """
    detector = make_surf_detector()
    key1, des1 = compute_features(detector, im1)
    key2, des2 = compute_features(detector, im2)
    matches = get_nearest_neighbors(des1, des2)
    pairs = align_features(key1, key2, matches)
    return pairs, key1, key2



def estimate_skew(image):  
    """
    Estimates the skew angle of an image with text.

    Parameters
    ----------
    image : Numpy array

    Returns 
    --------
    skew : float
        The estimate skew in degrees.
    """
    uni_im = ndimage.uniform_filter(image, (1, 50))

    ret, uni_im = cv2.threshold(uni_im, 50, 255, cv2.THRESH_BINARY)
    lines = cv2.HoughLinesP(uni_im, 1, math.pi / 180.0, 100, None, 100, 20)
    cum_angle = 0
    for l in lines[0]:
        a = angle((l[0], l[1]), (l[2], l[3]))
        if abs(a) < 5:
            cum_angle += a
    rotate = cum_angle / len(lines[0])
    return rotate


def find_lines(image):
    """
    Compute the layout from the image
    """

    draw_image = numpy.array(image)
    tmp_im = numpy.array(image)
    ret, thres_im = cv2.threshold(tmp_im, 4, 255, cv2.THRESH_BINARY)

    thres_im = ndimage.uniform_filter(thres_im, (1, 50))

    ret, thres_im = cv2.threshold(thres_im, 50, 255, cv2.THRESH_BINARY)


    lines = cv2.HoughLinesP(thres_im, 1, math.pi / 4.0, 100, None, 100, 10)
    tmp_mask = np.zeros(thres_im.shape, np.uint8)
    for l in lines[0]:
        a = angle((l[0], l[1]), (l[2], l[3]))
        if abs(a) < 1.0: 
            cv2.line(tmp_mask, (l[0], l[1]), (l[2], l[3]), 255, 1)
        
    contours, hier = cv2.findContours(tmp_mask, cv2.RETR_EXTERNAL, 
                                      cv2.CHAIN_APPROX_TC89_L1)  

    boxes = []
    mask = np.zeros(image.shape, np.uint8)
    draw_image = cv2.cvtColor(draw_image, cv2.COLOR_GRAY2BGR)
    for cnt in contours:
        box  = cv2.boundingRect(cnt)
        x, y, width, height = box
        if width > 20 and height > 2 and height < 40:
            boxes.append((x, y, width, height))
    return boxes

def draw_matches(im1, im2, pairs, key1, key2):
    """
    
    """

    h1, w1 = im1.shape[:2]
    h2, w2 = im2.shape[:2]
    hdif = (h1-h2)/2
    newimg = make_side_by_side(im1, im2)
    for p1, p2 in pairs:
        x1, y1 = key1[p1].pt
        x2, y2 = key2[p2].pt
        pt_a = (int(x1), int(y1+hdif))
        pt_b = (int(x2 + w1), int(y2))
        cv2.rectangle(newimg, (pt_a[0] + 5, pt_a[1] + 5), 
                      (pt_a[0] - 5, pt_a[1] - 5), (255,0,0))
        cv2.rectangle(newimg, (pt_b[0] + 5, pt_b[1] + 5), 
                      (pt_b[0] - 5, pt_b[1] - 5), (255,0,0))
        cv2.line(newimg, (pt_a[0] + 5, pt_a[1] + 5), (pt_b[0] + 5, pt_b[1] + 5), 
                 255, 1)
    return newimg

def draw_box(im, box):
    x, y, width, height = box
    cv2.rectangle(im, (x, y ), (x + width , y + height ), (250, 0, 0), 3)
            # cv2.rectangle(draw_image, (x + 5, y - 5), 
            #               (x + width + 10, y + height + 10), (250, 0, 0), 3)
