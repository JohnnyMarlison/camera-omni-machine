import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray

if __name__ == '__main__':
    def callback(*arg):
        print (arg)

camera = PiCamera()
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size = (640, 480))
bgr = (0, 255, 0)

hsv_min = np.array((0, 0, 0), np.uint8)
hsv_max = np.array((255, 100, 30), np.uint8)

color_yellow = (0,255,255)

for frame1 in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):
	img = frame1.array
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	thresh = cv2.inRange(hsv, hsv_min, hsv_max)

	moments = cv2.moments(thresh, 1)
	dM01 = moments['m01']
	dM10 = moments['m10']
	dArea = moments['m00']

	if dArea > 100:
		x = int(dM10 / dArea)
		y = int(dM01 / dArea)
		cv2.circle(img, (x, y), 5, color_yellow, 2)
		cv2.putText(img, "%d-%d" % (x,y), (x+10,y-10), 
		cv2.FONT_HERSHEY_SIMPLEX, 1, color_yellow, 2)

	cv2.imshow('result', img)
	rawCapture.truncate(0)
 
	ch = cv2.waitKey(5)
	if ch == 27:
		break

cv2.destroyAllWindows()
