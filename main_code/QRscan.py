from pyzbar.pyzbar import decode
import cv2
import numpy as np

def barcodeSearcher(frame):
	hsv_min = np.array((0, 0, 0), np.uint8)
	hsv_max = np.array((255, 100, 30), np.uint8)
	res = False

	x = 0
	y = 0   	

	color_yellow = (0,255,255)

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	thresh = cv2.inRange(hsv, hsv_min, hsv_max)

	moments = cv2.moments(thresh, 1)
	dM01 = moments['m01']
	dM10 = moments['m10']
	dArea = moments['m00']

	if dArea > 100:
		res = True
		x = int(dM10 / dArea)
		y = int(dM01 / dArea)
		#cv2.circle(frame, (x, y), 5, color_yellow, 2)
		#cv2.putText(frame, "%d-%d" % (x,y), (x+10,y-10), 
		#cv2.FONT_HERSHEY_SIMPLEX, 1, color_yellow, 2)
	
	return res, x, y

def barcodeReader(image, bgr):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray_img)

    if len(barcodes) == 0:
    	return 'Nan'

    # for decodedObject in barcodes:
    #     cv2.polylines(image, [pts], True, (0, 0, 255), 3)
    
    for bc in barcodes:
        #cv2.putText(frame, bc.data.decode("utf-8") + " - " + bc.type, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
        #           bgr, 2)

        return "Barcode: {} - Type: {}".format(bc.data.decode("utf-8"), bc.type)