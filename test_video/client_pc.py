import cv2
import time
import numpy
import socket
import os

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: 
        	return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def video_thread():
	TCP_IP = os.argv[1]
	TCP_PORT_VIDEO = 9000

	sock_video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock_video.connect((TCP_IP, TCP_PORT_VIDEO))

	time.sleep(5)

	print('Video start')
	while 1:
		length = recvall(sock_video, 5)
		stringData = recvall(sock_video, int(length))
		data = numpy.fromstring(stringData, dtype='uint8')
		image = cv2.imdecode(data, 1)

		cv2.imshow('Original', image)

		cv2.waitKey(1)

video_thread()