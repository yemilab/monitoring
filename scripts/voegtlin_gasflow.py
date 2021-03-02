import os
import sys
import time
import json
import struct
import logging

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# Default Device Address: 247
# Address:
#   0: Gas flow
#
def main():
    dev = os.getenv('DEVICE', None)
    tag = os.getenv('DEVICE_TAG', '')
    devtype = os.getenv('DEVICE_TYPE', '')
    if len(tag) == 0 or len(devtype) == 0:
        logging.error('No tag error! Stop program.')
        sys.exit(1)

    logging.info('Start loop')
    while True:
        logging.info('Start monitoring')
        data = []
        try:
            tstamp = int(time.time())
            client = ModbusClient(method='rtu', port=dev, baudrate=9600, bytesize=8, parity='N', stopbit=2)
            client.connect()
            r = client.read_holding_registers(0, 2, unit=247)
            data = struct.pack('>HH', r.registers[0], r.registers[1])
            gasflow = struct.unpack('>f', data)[0]
            client.close()
            data = [{
                'name': 'gasflow',
                'id': devtype,
                'pos': tag,
                'gasflow': gasflow,
                'time': tstamp
            }]
            with open(f'./data/gasflow_{tag}.log', 'a') as fp:
                fp.write(json.dumps(data)+'\n')
                fp.flush()
            logging.info('End monitoring')
            time.sleep(60)
        except KeyboardInterrupt:
            logging.info('Good bye')
            break
        except:
            logging.exception('Exception')
            time.sleep(5)

if __name__ == '__main__':
    main()
