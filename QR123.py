from pyzbar.pyzbar import decode
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import numpy as np
import time
import sys
import serial


def barcodeReader(image, bgr):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray_img)

    for decodedObject in barcodes:
        points = decodedObject.polygon
        global pts

        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        print(np.take(pts,([0, 0])))
        print(np.take(pts,([4, 4])))
        cv2.polylines(image, [pts], True, (0, 0, 255), 3)

    for bc in barcodes:
        cv2.putText(frame, bc.data.decode("utf-8") + " - " + bc.type, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    bgr, 2)

        return "Barcode: {} - Type: {}".format(bc.data.decode("utf-8"), bc.type)


print("Start Program")

pts = 0
value = -1

bgr = (0, 255, 0)
frame_rae = 30
camera = PiCamera()
camera.resloution(640, 480)
rawCapture = PiRGBArray(camera, size = (640, 480))
time.sleep(0.1)

#ser = serial.Serial('/dev/ttyUSB0', 115200)


for frame1 in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):   
    frame = frame1.array

    frame_rate = 10
    prev = 0

    time_elapsed = time.time() - prev
    image = frame1.array

    if time_elapsed > 1./frame_rate:
       	prev = time.time()

    if barcode == "Barcode: Step_1 - Type: QRCODE":
    	#ser.write("","")
    	print("PING")

    if barcode == "Barcode: Step_2 - Type: QRCODE":
   		print("PING PING")

    if barcode == "Barcode: Step_3 - Type: QRCODE":
    	print("PING PING PING")

    barcode = barcodeReader(frame, bgr)
    print(barcode)
    cv2.imshow('Barcode reader', frame)
    rawCapture.truncate(0)


    code = cv2.waitKey(10)
    if code == ord('q'):
        break

camera.close()
cv2.destroyAllWindows()
