from subprocess import Popen, PIPE
import sys
import serial

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