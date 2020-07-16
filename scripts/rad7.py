import sys
import time
import re
import logging
import json

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)

import serial

DEV='/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AI03B0BV-if00-port0'
BUFSIZE=1024000

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

def parse_runnum(data):
    runnum = None
    for line in data.split('\r\n'):
        m = re.search('^([0-9]+)', line)
        if m is not None:
            runnum = int(m.group(1).strip()[:2])
    return runnum

def parse_data(data):
    dlst = list()
    for line in data.split('\r\n'):
        d = [ l.strip() for l in line.split(',') ]
        if d[0].isdigit():
            dlst.append(d)
    ret = list()
    for d in dlst:
        try:
            t = time.strptime(' '.join(d[1:6]), '%y %m %d %H %M')
            tstamp = int(time.mktime(t))
            output = {
                'name': 'rad7',
                'dev': '4331',
                'time': tstamp,

                'recnum': int(d[0]),
                'totc': float(d[6]),
                'livet': float(d[7]),
                'totcA': float(d[8]),
                'totcB': float(d[9]),
                'totcC': float(d[10]),
                'totcD': float(d[11]),
                'hvlvl': float(d[12]),
                'hvcycle': float(d[13]),
                'temp': float(d[14]),
                'hum': float(d[15]),
                'leaki': float(d[16]),
                'batv': float(d[17]),
                'pumpi': float(d[18]),
                'flag': int(d[19]),
                'radon': float(d[20]),
                'radon_uncert': float(d[21]),
                'unit': int(d[22]),
            }
            ret.append(output)
        except IndexError:
            logging.exception('Line parsing failed')
            continue
        except ValueError:
            logging.exception('Value parsing failed')
            continue
    return ret

def fetch():
    with serial.Serial(DEV, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10) as ser:
        logging.info('Send ETX')
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)

        logging.info('Send Special Status')
        ser.write(b'Special Status\r\n')
        res = read_until_prompt(ser)
        runnum = parse_runnum(res)

        logging.info(f'Send Data Com {runnum:02d}')
        ser.write(f'Data Com {runnum:2d}\r\n'.encode('ascii'))
        res = read_until_prompt(ser)
        logging.info('Parse data')
        ret = parse_data(res)
        
        return ret

def main():
    while True:
        try:
            with open('./data/rad7.dat', 'w') as fp:
                data = fetch()
                fp.write(json.dumps(data)+'\n')
                fp.flush()
            time.sleep(600)
        except KeyboardInterrupt:
            logging.info('Good bye')
        except:
            logging.exception('Exception: ')
            time.sleep(600)

if __name__ == '__main__':
    main()
