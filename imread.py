import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from pyzbar.pyzbar import decode
import serial

def my_map(x, in_min, in_max, out_min, out_max)
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def math_block(pts):
    mid_x = (np.take(pts, ([4])) - np.take(pts, ([0]))) // 2 + np.take(pts, ([0]))
    mid_y = (np.take(pts, ([5])) - np.take(pts, ([1]))) // 2 + np.take(pts, ([1]))
    vec_a = 320 - mid_x 
    vec_b = 480 - mid_y
    my_map(vec_a, -320, 320, -255, 255)
    my_map(vec_b, -240, 240, -255, 255)
    return '{} {}'.format(vec_a, vec_b)

def barcodeReader(image, bgr):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray_img)

    for decodedObject in barcodes:
        points = decodedObject.polygon

        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))

        mid_qr_x = (np.take(pts, ([4])) - np.take(pts, ([0]))) // 2 + np.take(pts, ([0]))
        mid_qr_y = (np.take(pts, ([5])) - np.take(pts, ([1]))) // 2 + np.take(pts, ([1]))
        print("{} {}".format(mid_qr_x, mid_qr_y))
        cv2.polylines(image, [pts], True, (0, 0, 255), 3)

    for bc in barcodes:
        return "Barcode: {} - Type: {}".format(bc.data.decode("utf-8"), bc.type)

img = cv2.imread('/home/user/Documents/qrcodePy/test.png')

bgr = (0, 255, 0)
barcode = barcodeReader(img, bgr)
print(barcode)
cv2.imshow("Frame", img)

while 1:
    key = cv2.waitKey(1)