"""
Code for converting images to layouts.
"""

from random import random
import cv2
import math
import matplotlib.pyplot as plt
import numpy as np
import numpy.linalg
import scipy.ndimage as ndimage
import sys

FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing

PARAMS = {
  "feature_score": 5000
}

flann_params = dict(algorithm = FLANN_INDEX_KDTREE,
                    trees = 4)


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
    key, des = detector.detectAndCompute(img, None)
    return key, des


def get_nearest_neighbors(desc1, desc2):
    """
    Parameters
    ----------
    desc1, desc2 : Feature descriptors.
    
    Returns
    --------
    idx2 : 
        The index in desc2 that matches.

    dist : 
        The euclidean between the descriptors.
    """    

    flann = cv2.flann_Index(desc2, flann_params)
    idx2, dist = flann.knnSearch(desc1, 5, params = {}) 
    return idx2, dist


def align_features(key1, key2, idx2, dist, max_dist = 0.05):
    """
    Nearest neighbors matching of sets of features.
    
    Parameters
    ----------
    
    key1, key2 : Key points
    
    """
    matches = [-1] * len(key1)
    for id1, match2 in enumerate(idx2): 
        # id1 is the index of the original features.
        # match2 is the n-best matches
        best = 100
        for i, m in enumerate(match2):
            # m is the match. 

            # Check1: Check if the descriptor distance is within threshold. 
            if dist[id1][i] > max_dist: continue
            
            # Check2: Keep the closet  n keypoint distance is within threshold. 
            diff = abs(np.array(key1[id1].pt) - numpy.array(key2[m].pt))
            l2 = numpy.linalg.norm(diff)
            if l2 < best:
                best = l2 
                matches[id1] = m
                break

    return [(i,m) for i, m in enumerate(matches) if m != -1] 


def align_images(im1, im2):
    detector = make_surf_detector()
    key1, des1 = compute_features(detector, im1)
    key2, des2 = compute_features(detector, im2)
    idx2, dist = get_nearest_neighbors(des1, des2)
    pairs = align_features(key1, key2, idx2, dist)
    return pairs, key1, key2

    # show_pairs(img1, img2, pairs, key1, key2)


def make_side_by_side(im1, im2):
    # im1 = cv2.cvtColor(im1, cv2.COLOR_GRAY2BGR)
    # im2 = cv2.cvtColor(im2, cv2.COLOR_GRAY2BGR)
    h1, w1 = im1.shape[:2]
    h2, w2 = im2.shape[:2]
    nWidth = w1+w2
    nHeight = max(h1, h2)
    hdif = (h1-h2)/2
    newimg = np.zeros((nHeight, nWidth, 3), np.uint8)
    newimg[:h1, :w1] = im1
    newimg[:h2, w1:w1+w2] = im2
    return newimg

def draw_matches(im1, im2, pairs, key1, key2):
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


