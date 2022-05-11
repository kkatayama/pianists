#!/user/bin/env python3
import serial
import time
import threading
import sys


ser  = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

if sys.argv[1] == 't':
    ser.write('p\n'.encode('ascii'))

if sys.argv[1] == '-c':

    code = ' '.join(sys.argv[2:]) + '\n'

    ser.write(code.encode('utf-8'))

if sys.argv[1] == '-s':

    path = '//home//pi//' + sys.argv[2]

    with open(path, mode='r', encoding='utf-8') as f:
        stuff = f.read()

    ser.write(stuff.encode('utf-8'))


