import os
import sys
import time
import logging
import json

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

import serial

def main():
    dev = os.getenv('DEVICE', None)
    tag = os.getenv('DEVICE_TAG', '')
    if len(tag) == 0:
        logging.error('No tag error! Stop program.')
        sys.exit(1)

    # Read serial number
    logging.info('Fetch serial number')
    with serial.Serial(dev, 19200) as ser:
        ser.write(b'ATCMODEL\r\n')
        res = ser.readline().strip() # response example: b'ATCMODEL 19060001'
        sn = res.decode('utf-8').split()[1]

    # Read oxygen level and temperture
    logging.info('Start loop')
    while True:
        try:
            logging.info('Start monitoring')
            tstamp = int(time.time())
            with serial.Serial(dev, 19200) as ser:
                ser.write(b'ATCD\r\n')
                res = ser.readline() # reponse example: b'ATCD 20.40,25.2'
                values = res.decode('utf-8').split()[1]
                o2, temp = values.split(',')
                data = {
                    'name': 'o2',
                    'pos': tag,
                    'vender': 'dekist',
                    'model': 'UA-52',
                    'sn': sn,
                    'o2': float(o2),
                    'temp': float(temp),
                    'time': tstamp,
                }
            with open(f'./data/radionode-UA52-{tag}.log','a') as fp:
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
