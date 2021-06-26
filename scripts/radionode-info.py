import os
import sys
import time
import logging
import json

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

import serial

DEV = ''

def main():
    with serial.Serial(DEV, 19200) as ser:
        ser.write(b'ATCMODEL\r\n')
        res = ser.readline().strip()
        logging.info(f'MODEL: {res.decode("utf-8")}')
        ser.write(b'ATCVER\r\n')
        res = ser.readline().strip()
        logging.info(f'VER: {res.decode("utf-8")}')
        ser.write(b'ATCD\r\n')
        res = ser.readline().strip()
        logging.info(f'DATA: {res.decode("utf-8")}')

if __name__ == '__main__':
    main()

