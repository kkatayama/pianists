#!/usr/bin/env python3
import serial
import time
import threading
import sys
import argparse


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--src", help="the musicmxl file to parse")
    args = ap.parse_args()

    ser  = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

    """
    if sys.argv[1] == 't':
        ser.write('p\n'.encode('ascii'))

    if sys.argv[1] == '-c':

        code = ' '.join(sys.argv[2:]) + '\n'

        ser.write(code.encode('utf-8'))
    """

    if args.src:
        path = args.src

        with open(path, mode='r', encoding='utf-8') as f:
            stuff = f.read()

        ser.write(stuff.encode('utf-8'))
