from picamera import PiCamera
from picamera.array import PiRGBArray
from enum import Enum
from QRscan import *
from mathlogic import *
from connection import *
import time
import socket
import threading

TCP_PORT_SERIAL = 9000
frame = 0

class State(Enum):
	SEARCH_QR = 1
	GO_TO_QR = 2
	SCAN_QR = 3
	SEARCH_NEW_QR = 4

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

		res, x, y = barcodeSearcher(image)

		if curr_state == State.SEARCH_QR:
			send_to_serial(sock, 'R 0')
			print('SEARCH')
			
			if res:
				send_to_serial(sock, 'L 0 0')
				time.sleep(2)
				curr_state = State.GO_TO_QR

		elif curr_state == State.GO_TO_QR:
			print('GO_TO_QR')
			if res:
				command = math_block(x, y)
				send_to_serial(sock, 'L ' + command)
				
				bcr = barcodeReader(image, bgr)
				print(bcr)
				if bcr != 'Nan':
					time.sleep(2)
					curr_state = State.SCAN_QR
		
		elif curr_state == State.SCAN_QR:
			print('SCAN')
			send_to_serial(sock, 'L 0 0')
			bc = barcodeReader(image, bgr)
			if bc != 'Nan':
				time.sleep(2)
				barcode_base.append(bc)
				curr_state = State.SEARCH_NEW_QR


		elif curr_state == State.SEARCH_NEW_QR:
			print('SERACH_NEW')
			send_to_serial(sock, 'R 0')
			if res:
				time.sleep(2)
				bc = barcodeReader(image, bgr)
				if not (bc in barcode_base):
					curr_state = State.GO_TO_QR

		#cv2.imshow('Barcode reader', image)
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
