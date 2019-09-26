import cv2
import numpy as np
import sys
import time


cap = cv2.VideoCapture(0)

while True:
	ret, frame = cap.read()

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (21, 21), 0)
	ret, thresh_img = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)

	contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	#print(contours)

	for c in contours:
		cv2.drawContours(thresh_img, [c], -1, (0, 0, 255), 3)


	cv2.imshow('Search', thresh_img)

	code = cv2.waitKey(10)
	if code == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()