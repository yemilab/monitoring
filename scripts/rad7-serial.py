import os
import sys
import time
import re
import logging
import json

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)

import serial

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
    logging.debug(data)
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
            ret.append((tstamp, output))
            logging.debug((tstamp, output))
        except IndexError:
            logging.exception('Line parsing failed')
            continue
    return ret

def fetch(dev):
    mode = 'latest'

    with serial.Serial(dev, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10) as ser:
        logging.info('Send ETX')
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)
        ser.write(b'\x03\r\n')
        res = read_until_prompt(ser)

        if mode == 'latest':
            logging.info('Send Special Status')
            ser.write(b'Special Status\r\n')
            res = read_until_prompt(ser)
            runnum = parse_runnum(res)
            logging.debug(f'Run number is {runnum}')
            logging.info(f'Send Data Com {runnum:02d}')
            ser.write(f'Data Com {runnum:2d}\r\n'.encode('ascii'))
            res = read_until_prompt(ser)
            logging.info('Parse data')
            ret = parse_data(res)
        elif mode == 'all':
            logging.info(f'Special ComAll')
            ser.write(f'Special ComAll\r\n'.encode('ascii'))
            res = read_until_prompt(ser)
            logging.info('Parse data')
            ret = parse_data(res)
        else:
            logging.error('Unknown mode')
            sys.exit(1)

        return ret

def main():
    dev = os.getenv('DEVICE', None)
    tag = os.getenv('DEVICE_TAG', '')
    sn = os.getenv('DEVICE_SN', '')
    if len(tag) == 0 or len(sn) == 0:
        logging.error('No tag or sn error! Stop program.')
        sys.exit(1)
    logging.info('Start loop')
    while True:
        try:
            ret = fetch(dev)
            data = list()
            for tstamp, d in ret:
                data.append({
                    'name': 'rad7',
                    'dev': sn,
                    'pos': tag,
                    'time': tstamp,
                    **d,
                })
            with open(f'./data/rad7-serial_{tag}.log', 'w') as fp:
                fp.write(json.dumps(data)+'\n')
                fp.flush()
            time.sleep(600)
        except ValueError:
            logging.exception('Parsing failed. Retry after 5 secs...')
            time.sleep(5)
        except KeyboardInterrupt:
            logging.info('Good bye')
            break
        except:
            logging.exception('Exception: ')
            time.sleep(600)

if __name__ == '__main__':
    main()
