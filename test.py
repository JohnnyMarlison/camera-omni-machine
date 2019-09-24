import socket
import threading
import time

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
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('', 9000))
	sock.listen(1)
	conn, addr = sock.accept()
	print('Video connected')
	while 1:
		print(readall(conn))

def video_thread():
	time.sleep(2)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(('127.0.0.1', 9000))
	while 1:
		m = 'ping'
		send_to_serial(sock, m)


thread1 = threading.Thread(target=serial_thread, args=())
thread2 = threading.Thread(target=video_thread, args=())

thread1.daemon = True
thread2.daemon = True

thread1.start()
thread2.start()
thread1.join()
thread2.join()