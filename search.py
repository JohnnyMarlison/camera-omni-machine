from pyzbar.pyzbar import decode
import cv2
import numpy as np
import sys
import time

def my_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def get_pts_value(pts, ind):
    return np.take(pts, ([ind])).item()

def math_block(pts):
    mid_x = (get_pts_value(pts, 4) - get_pts_value(pts, 0)) // 2 + get_pts_value(pts, 0)
    mid_y = (get_pts_value(pts, 5) - get_pts_value(pts, 1)) // 2 + get_pts_value(pts, 1)
    vec_a = 320 - mid_x 
    vec_b = 480 - mid_y
    my_map(vec_a, -320, 320, -255, 255)
    my_map(vec_b, -240, 240, -255, 255)
    return '{} {}'.format(str(vec_a), str(vec_b))


def barcodeSearcher(image, bgr):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray_img)
    pts = np.array([])

    if len(barcodes) == 0:
        return pts

    for decodedObject in barcodes:
        points = decodedObject.polygon

        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))

        return pts

cap = cv2.VideoCapture(0)
bgr = (0, 255, 0)

while True:
    _, frame = cap.read()
    #image = cap.read()
    pts = barcodeSearcher(frame, bgr)
    if len(pts) != 0:
        print('L ' + math_block(pts))
    else:
        print('nan')

    cv2.imshow('Barcode reader', frame)

    code = cv2.waitKey(10)
    if code == ord('q'):
        break