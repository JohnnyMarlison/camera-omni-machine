import sys
import cv2 as cv 
import numpy as np
import time
from picamera import PiCamera
from picamera.array import PiRGBArray
import serial

#ser = serial.Serial('/dev/ttyUSB0', 115200)
#ser.open()
cascade = cv.CascadeClassifier("lbpcascade_frontalface.xml") 

print("PING PROGRAM")

frame_rate = 15
camera = PiCamera()
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port=True):
	img = frame.array
	value = -1
	gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
	sf = min(640./img.shape[1], 480./img.shape[0])
	gray = cv.resize(gray, (0,0), None, sf, sf)
	rects = cascade.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors = 4, minSize = (40, 40), flags = cv.CASCADE_SCALE_IMAGE)
	gray = cv.GaussianBlur(gray, (3, 3), 1.1)
	edges = cv.Canny(gray, 5, 50)  
	out = cv.cvtColor(edges, cv.COLOR_GRAY2BGR)
	L_x1 = 160
	L_y1 = 0
	L_y2 = 480
	R_x1 = 480
	R_y1 = 0
	R_y2 = 480
	cv.line(out, (L_x1, L_y1), (L_x1, L_y2), (0, 255, 0), 3)
	cv.line(out, (R_x1, R_y1), (R_x1, R_y2), (0, 255, 0), 3)
	for x, y, w, h in rects: 
		cv.rectangle(out, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
		if (L_x1 > x) and (L_y1 < y):
			print("LEFT")
			#ser.open()
			#ser.write(b'L -2 0 \n')
			#ser.close()
#			time.sleep(0.5)
			continue
        
		if (R_x1 < x + w) and (R_y1 < y + h):
			print("RIGHT")
			#ser.write(b'L 2 0 \n')

			continue
        
		if (L_x1 < x) and (R_x1 > x + w):
			print("GO FRONT")
			#ser.open()
			#ser.write(b'L 0 3 \n')
			#ser.close()
#			time.sleep(0.5)
			continue
        
		if (x < L_x1) and (x + w > R_x1):
			print("BACK BACK BACK")
			#ser.write(b'L 0 -3 \n')
			continue
   

	cv.imshow("Face Detect", out)
	rawCapture.truncate(0)
	if cv.waitKey(1) & 0xFF == ord('q'): 
		break

camera.close()
cv.destroyAllWindows()   
#ser.close() 
    
