import os
import sys
import time
import json
import logging

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

import serial

def fetch(dev):
    with serial.Serial(dev, 19200) as ser:
        ser.write(b'ATCD\r\n')
        res = ser.readline()
        line = res.decode('utf-8').strip()
        logging.info(f'Res: {line}')
        ch1, _ = line.split(' ')[1].split(',')
        o2 = 1.5625 * (float(ch1) - 4.0)
    return o2

def main():
    dev = os.getenv('DEVICE', None)
    tag = os.getenv('DEVICE_TAG', '')
    sn = os.getenv('DEVICE_SN', '')
    if len(tag) == 0 or len(sn) == 0:
        logging.error('No tag error! Stop program.')
        sys.exit(1)
    # Test device address
    logging.info('Test fetch data')
    fetch(dev)

    logging.info('Start loop')
    while True:
        logging.info('Start monitoring')
        data = list()
        try:
            tstamp = int(time.time())
            o2 = fetch(dev)
            data.append({
                'name': 'o2',
                'vendor': 'pureaire',
                'model': 'TX-1100-DRA',
                'sn': sn,
                'pos': tag,
                'o2': o2,
                'time': tstamp,
            })
            with open(f'./data/pureaire_o2_{tag}.log','a') as fp:
                fp.write(json.dumps(data)+'\n')
                fp.flush()
            logging.info('End monitoring')
            time.sleep(60)
        except KeyboardInterrupt:
            logging.info('Good bye')
            break
        except:
            logging.exception("Exception")
            time.sleep(60)

if __name__ == '__main__':
    main()
