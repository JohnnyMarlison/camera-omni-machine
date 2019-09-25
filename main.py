from pyzbar.pyzbar import decode
from picamera import PiCamera
from picamera.array import PiRGBArray
from subprocess import Popen, PIPE
from enum import Enum
import cv2
import numpy as np
import time
import sys
import serial
import socket
import threading

TCP_PORT_SERIAL = 9000
frame = 0

class State(Enum):
	SEARCH_QR = 1
	GO_TO_QR = 2
	SCAN_QR = 3
	SEARCH_NEW_QR = 4

def my_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def math_block(pts):
    mid_x = (np.take(pts, ([4])) - np.take(pts, ([0]))) // 2 + np.take(pts, ([0]))
    mid_y = (np.take(pts, ([5])) - np.take(pts, ([1]))) // 2 + np.take(pts, ([1]))
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
    
        cv2.polylines(image, [pts], True, (0, 0, 255), 3)

        return pts

def barcodeReader(image, bgr):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray_img)

    if len(barcodes) == 0:
    	return 'Nan'

    # for decodedObject in barcodes:
    #     cv2.polylines(image, [pts], True, (0, 0, 255), 3)
    
    for bc in barcodes:
        cv2.putText(frame, bc.data.decode("utf-8") + " - " + bc.type, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    bgr, 2)

        return "Barcode: {} - Type: {}".format(bc.data.decode("utf-8"), bc.type)

def get_name_usb():
	dev = Popen("ls /dev/ttyU* 2>/dev/null", shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()
	if (not len(dev)):
		dev = Popen("ls /dev/ttyA* 2>/dev/null", shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()

	for i in range(0, len(dev)):
		dev[i] = dev[i].decode()
	return dev

def readall(sock):
	message = ''
	b = -1
	while 1:
		b = sock.recv(1).decode()
		if b == 'E':
			break
		message += b
	return message

def send_to_serial(sock, message):
	message += ' \nE'
	sock.send(message.encode())
	print('Sending')

def serial_thread():
	while (not len(get_name_usb())):
		continue
	ser_name = get_name_usb()[0]
	ser = serial.Serial(ser_name, 9600)
	print('Device connected {}'.format(ser_name))

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('', TCP_PORT_SERIAL))
	sock.listen(1)
	conn, addr = sock.accept()
	print('Video connected {}'.format(addr))
	while 1:
		m = readall(conn)
		print('Current command to serial: {}'.format(m))
		ser.write(m.encode())

def video_thread():
	time.sleep(2)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(('127.0.0.1', TCP_PORT_SERIAL))

	# value = -1
	barcode_base = []
	curr_state = State.SEARCH_QR
	bgr = (0, 255, 0)
	frame_rate = 30
	camera = PiCamera()
	camera.resolution = (640, 480)
	rawCapture = PiRGBArray(camera, size = (640, 480))

	L_x1 = np.int32(300)
	L_y1 = np.int32(0)
	L_y2 = np.int32(480)

	R_x1 = np.int32(385)
	R_y1 = np.int32(0)
	R_y2 = np.int32(480)

	for frame1 in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):   
		global frame
		frame = frame1.array
		image = frame1.array

		#line1 = cv2.line(image, (L_x1, L_y1), (L_x1, L_y2), (0, 255, 0), 3)
		#line2 = cv2.line(image, (R_x1, L_y1), (R_x1, R_y2), (0, 255, 0), 3)

		pts = barcodeSearcher(image, bgr)

		if curr_state == State.SEARCH_QR:
			send_to_serial(sock, 'R 0')
			print('SEARCH')
			
			if len(pts):
				send_to_serial(sock, 'L 0 0')
				curr_state = State.GO_TO_QR

		elif curr_state == State.GO_TO_QR:
			print('GO_TO_QR')
			if len(pts):
				command = math_block(pts)
				send_to_serial(sock, 'L ' + command)
				
				bcr = barcodeReader(image, bgr)
				print(bcr)
				if bcr != 'Nan':
					curr_state = State.SCAN_QR
		
		elif curr_state == State.SCAN_QR:
			print('SCAN')
			send_to_serial(sock, 'L 0 0')
			bc = barcodeReader(image, bgr)
			if len(bc) != 0:
				barcode_base.append(bc)
				curr_state = State.SEARCH_NEW_QR


		elif curr_state == State.SEARCH_NEW_QR:
			print('SERACH_NEW')
			send_to_serial(sock, 'R 0')
			if len(pts) != 0:
				bc = barcodeReader(image, bgr)
				if not (bc in barcode_base):
					curr_state = State.GO_TO_QR

		# if value == -1:
		# 	send_to_serial(sock, 'R 0')
		# 	print("Step_0")


		# if len(pts):
		# 	# x1 = np.take(pts,([0]))
		# 	# x2 = np.take(pts,([4]))

			

		# 	if barcode == "Barcode: Step_1 - Type: QRCODE":
		# 		print("PING PING PING")
		# 		send_to_serial(sock, 'L 0 0')
		# 		send_to_serial(sock, 'L 0 255')
		# 		print("Step_1_0")
		# 		value = 0

		# 	if (x1 < L_x1 and x2 > R_x1 and barcode == "Barcode: Step_1 - Type: QRCODE"):
		# 		send_to_serial(sock, 'L 0 0')
		# 		send_to_serial(sock, 'L 0 255')
		# 		print("Step_1_1")
		# 		value = 1
	
		# 	if barcode == "Barcode: Step_2 - Type: QRCODE":
		# 		send_to_serial(sock, 'R 1')
		# 		print("Step_2_0")
	
		# 	if barcode == "Barcode: Step_3 - Type: QRCODE":
		# 		print("PING PING PING")

		cv2.imshow('Barcode reader', image)
		rawCapture.truncate(0)


		code = cv2.waitKey(10)
		if code == ord('q'):
			break


thread1 = threading.Thread(target=serial_thread, args=())
thread2 = threading.Thread(target=video_thread, args=())

thread1.daemon = True
thread2.daemon = True

thread1.start()
thread2.start()
thread1.join()
thread2.join()
