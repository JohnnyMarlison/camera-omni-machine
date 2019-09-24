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
        cv2.polylines(image, [pts], True, (0, 0, 255), 3)

    for bc in barcodes:
        cv2.putText(frame, bc.data.decode("utf-8") + " - " + bc.type, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    bgr, 2)

        return "Barcode: {} - Type: {}".format(bc.data.decode("utf-8"), bc.type)


print("Start Program")

pts = 0
value = True
bgr = (0, 255, 0)
frame_rate = 30
camera = PiCamera()
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size = (640, 480))
time.sleep(0.1)

ser = serial.Serial('/dev/ttyUSB0', 115200)

L_x1 = 300
L_y1 = 0
L_y2 = 480

R_x1 = 385
R_y1 = 0
R_y2 = 480

x1 = int(np.take(pts,([0])))
x2 = int(np.take(pts,([0])))

for frame1 in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):   
	frame = frame1.array

	prev = 0

	time_elapsed = time.time() - prev
	image = frame1.array

	if time_elapsed > 1./frame_rate:
		prev = time.time()

	line1 = cv2.line(image, (L_x1, L_y1), (L_x1, L_y2), (0, 255, 0), 3)
	line2 = cv2.line(image, (R_x1, L_y1), (R_x1, R_y2), (0, 255, 0), 3)

	barcode = barcodeReader(frame, bgr)
	print(barcode)


	while value:
		ser.write(b'R 1 \n')
		time.sleep(0.25)
		ser.write(b'R 0 \n')
		time.sleep(0.25)

		print("Step_0")
		ser.write(b'L 0 0 \n')
		time.sleep(1)
		ser.write(b'L 255 0 \n')
		time.sleep(1)
		ser.write(b'L 0 255 \n')
		time.sleep(1)

	#print((np.take(pts,([[0]]))))
	#print((np.take(pts,([[4]]))))

	#print(x1)
	#print(x2)


	if barcode == "Barcode: Step_1 - Type: QRCODE":
		ser.write(b'L 0 0 \n')
		#time.sleep(1)
		ser.write(b'L 0 255 \n')
		time.sleep(1)

		print("Step_1_0")
		#value = 0


	if (x1 < L_x1 and x2 < R_x1 and barcode == "Barcode: Step_1 - Type: QRCODE"):
		print("Step_1_1")

		ser.write(b'L 0 0 \n')
		time.sleep(1)
		#value = 1
		ser.write(b'L 0 255 \n')
		time.sleep(1)

	if barcode == "Barcode: Step_2 - Type: QRCODE":
   		print("Step_2_0")

   		ser.write(b'R 1 \n')
   		time.sleep(1)

	if barcode == "Barcode: Step_3 - Type: QRCODE":
		print("PING PING PING")

	#cv2.imshow('Barcode reader', frame)
	rawCapture.truncate(0)


	code = cv2.waitKey(10)
	if code == ord('q'):
		break

camera.close()
cv2.destroyAllWindows()
ser.close()
