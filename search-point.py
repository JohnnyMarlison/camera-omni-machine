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
		cv2.drawContours(frame, [c], -1, (0, 255, 0), 1)


	x = 0
	y = 0

	for i in range(2, frame.shape[0] - 2):
		for j in range(2, frame.shape[1] - 2):
			if (frame[i, j, 0] == 0 and frame[i, j, 1] == 255):
				x = i
				y = j
				break
			j += 6
		i += 6

	frame[x-10:x+10, y-10:y+10] = (0, 0, 255)

	print('{} {}'.format(x, y))

	# cv2.imshow('Search', thresh_img)
	cv2.imshow('Original', frame)

	code = cv2.waitKey(10)
	if code == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()