import serial 
import time
from subprocess import Popen, PIPE

def get_name_usb():
	dev = Popen("ls /dev/ttyU* 2>/dev/null", shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()
	if (not len(dev)):
		dev = Popen("ls /dev/ttyA* 2>/dev/null", shell=True, stdin=PIPE, stdout=PIPE).stdout.read().split()

	for i in range(0, len(dev)):
		dev[i] = dev[i].decode()
	return dev

while (not len(get_name_usb())):
	continue

ser_name = get_name_usb()[0]
ser = serial.Serial(ser_name, 9600)

print('Connected {}'.format(ser_name))
print('Start comm-ping')

while (1):
	ser.write(b'R 1 \n')
	time.sleep(1)
	ser.write(b'R 0 \n')
	time.sleep(1)
	ser.write(b'L 0 0 \n')
	time.sleep(1)
	ser.write(b'L 255 0 \n')
	time.sleep(1)
	ser.write(b'L 0 255 \n')
	time.sleep(1)
	print('Loop comm-ping successfully completed')

