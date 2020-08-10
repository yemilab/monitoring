# Fire alarm
# Address Details
# 0       Dry contact (digital input)
# 1       Wet contact (digital output) => 24V fire alarm
import os
import sys
import time
import json
import logging
import datetime

from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)

def main():
    ipaddr = os.getenv('DEVICE_IPADDR', None)
    port = int(os.getenv('DEVICE_PORT', None))
    tag = os.getenv('DEVICE_TAG', '')
    if len(tag) == 0:
        logging.error('No tag error! Stop program.')
        sys.exit(1)
    logging.info('Start loop')
    while True:
        logging.info('Start monitoring')
        try:
            tstamp = int(time.time())
            with ModbusClient(ipaddr, port=port) as client:
                # Read fire alarm status
                rr = client.read_holding_registers(0, 1, unit=1)
                status = 0 if rr.registers[0] == 0 else 1
                with open(f'./data/fire_{tag}.log','a') as fp:
                    fp.write(f'fire,pos={tag} status={status}i {tstamp*(10**9)}\n')
                    fp.flush()
            logging.info('End monitoring')
            time.sleep(5)            
        except KeyboardInterrupt:
            logging.info('Good bye')
            break
        except:
            logging.exception("Exception")
            time.sleep(5)

if __name__ == '__main__':
    main()
