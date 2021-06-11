# TODO: Input device path via command line argument
#
import sys
import logging

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)

import serial

DEV=''
BUFSIZE=102400

def read_until_prompt(ser):
    data = bytearray(BUFSIZE)
    for i in range(BUFSIZE):
        b = ser.read()
        if len(b) > 0:
            data[i] = b[0]
            if i >= 2:
                if data[i-2:i+1] == b'\r\n>':
                    logging.debug('Prompt line founded')
                    break
        else:
            logging.debug('Read timeout or no data')
            break
    return data.decode('ascii')

def test_start():
    with serial.Serial(DEV, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10) as ser:
        logging.info('Send ETX')
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)

        logging.info('Send Test Start')
        ser.write(b'Test Start\r\n')
        buf = ser.read(BUFSIZE)
        if len(buf) > 0:
            logging.info(buf.decode('ascii'))
        else:
            logging.error('No data')

def test_status():
    with serial.Serial(DEV, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10) as ser:
        logging.info('Send ETX')
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)

        logging.info('Send Test Status')
        ser.write(b'Test Status\r\n')
        buf = ser.read(BUFSIZE)
        if len(buf) > 0:
            logging.info(buf.decode('ascii'))
        else:
            logging.error('No data')

def setup_recycle():
    with serial.Serial(DEV, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10) as ser:
        logging.info('Send ETX')
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)

        logging.info('Send Setup Recycle')
        ser.write(b'Setup Recycle\r\n')
        res = read_until_prompt(ser)
        logging.debug(res)
        ser.write(b'00\r\n')
        res = read_until_prompt(ser)
        logging.debug(res)

def test_stop():
    with serial.Serial(DEV, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10) as ser:
        logging.info('Send ETX')
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)

        logging.info('Send Test Stop')
        ser.write(b'Test Stop\r\n')
        buf = ser.read(BUFSIZE)
        if len(buf) > 0:
            logging.info(buf.decode('ascii'))
        else:
            logging.error('No data')

def test_purge():
    with serial.Serial(DEV, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10) as ser:
        logging.info('Send ETX')
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)

        logging.info('Send Test Purge')
        ser.write(b'Test Purge\r\n')
        buf = ser.read(BUFSIZE)
        if len(buf) > 0:
            logging.info(buf.decode('ascii'))
        else:
            logging.error('No data')

def main():
    #test_stop()
    #test_status()
    #test_purge()
    test_start()
    test_status()

if __name__ == '__main__':
    main()
