from pyzbar.pyzbar import decode
from picamera import PiCamera
from picamera.array import PiRGBArray
from subprocess import Popen, PIPE
import cv2
import numpy as np
import time
import sys
import serial
import socket
import threading

TCP_PORT_SERIAL = 9000

def get_name_usb():
	dev = Popen("ls /dev/ttyU* 2>/dev/null", shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()
	if (not len(dev)):
		dev = Popen("ls /dev/ttyA* 2>/dev/null", shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()

	for i in range(0, len(dev)):
		dev[i] = dev[i].decode()
	return dev

def readall(sock):
	message = ''
	b = 0
	while 1:
		b = sock.recv(1).decode()
		if b == '\0':
			break
		message += b
	return message

def send_to_serial(sock, message):
	message += '\n\0'
	sock.send(message.encode())

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
	print('Video connected')
	while 1:
		ser.write(readall(conn))

def video_thread():
	time.sleep(2)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(('127.0.0.1', TCP_PORT_SERIAL))

	pts = 0
	value = True
	bgr = (0, 255, 0)
	frame_rate = 30
	camera = PiCamera()
	camera.resolution = (640, 480)
	rawCapture = PiRGBArray(camera, size = (640, 480))
	time.sleep(0.1)

	L_x1 = 300
	L_y1 = 0
	L_y2 = 480

	R_x1 = 385
	R_y1 = 0
	R_y2 = 480

	x1 = int(np.take(pts,([0])))
	x2 = int(np.take(pts,([4])))

	for frame1 in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):   
		frame = frame1.array
		image = frame1.array

		line1 = cv2.line(image, (L_x1, L_y1), (L_x1, L_y2), (0, 255, 0), 3)
		line2 = cv2.line(image, (R_x1, L_y1), (R_x1, R_y2), (0, 255, 0), 3)

		barcode = barcodeReader(frame, bgr)
		print(barcode)

		if value == -1:
			send_to_serial(sock, 'R 1')

		if barcode == "Barcode: Step_1 - Type: QRCODE":
			send_to_serial(sock, 'L 0 0')
			#time.sleep(1)
			send_to_serial(sock, 'L 0 255')
			time.sleep(1)

			print("Step_1_0")
			#value = 0


		if (x1 < L_x1 and x2 < R_x1 and barcode == "Barcode: Step_1 - Type: QRCODE"):
			print("Step_1_1")

			send_to_serial(sock, 'L 0 0')
			time.sleep(1)
			#value = 1
			send_to_serial(sock, 'L 0 255')
			time.sleep(1)

		if barcode == "Barcode: Step_2 - Type: QRCODE":
	   		print("Step_2_0")

	   		send_to_serial(sock, 'R 1')
	   		time.sleep(1)

		if barcode == "Barcode: Step_3 - Type: QRCODE":
			print("PING PING PING")

		#cv2.imshow('Barcode reader', frame)
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