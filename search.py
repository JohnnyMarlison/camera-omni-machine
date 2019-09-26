from pyzbar.pyzbar import decode
import cv2
import numpy as np
import sys
import time


def barcodeReader(image, bgr):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray_img)
    pts = np.array([])
  #  global pts
    if len(barcodes) == 0:
        return "NAN", pts

    for decodedObject in barcodes:
        points = decodedObject.polygon

        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
    
        return cv2.polylines(image, [pts], True, (0, 0, 255), 3)

cap = cv2.VideoCapture(0)
bgr = (0, 255, 0)

while True:
    _, frame = cap.read()
    #image = cap.read()
    barcode = barcodeReader(frame, bgr)
    print(barcode)

    cv2.imshow('Barcode reader', frame)

    code = cv2.waitKey(10)
    if code == ord('q'):
        break