import os
import sys
import time
import json
import logging
import datetime

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

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
            with ModbusClient(ipaddr, port=port, framer=ModbusRtuFramer, timeout=5) as client:
                rr = client.read_holding_registers(0, 2, unit=0x0)
                sensor1 = rr.registers[0]
                tstamp = int(time.time())
                with open(f'./data/leak_{tag}.log','a') as fp:
                    fp.write(f'LeakMon,loc={tag} sensor01={sensor1}i {tstamp*(10**9)}\n')
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
