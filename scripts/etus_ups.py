import os
import sys
import time
import json
import struct
import socket
import logging

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

from pysnmp.hlapi import *

ETUS_OIDS = {
  '1.3.6.1.2.1.33.1.2.1.0':
    {
    'name': 'Battery Status',
    'short_name': 'battery_status',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.2.3.0':
    {
    'name': 'Battery Remain',
    'short_name': 'battery_remain',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.2.4.0':
    {
    'name': 'Battery Charge',
    'short_name': 'battery_charge',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.3.3.1.3.1':
    {
    'name': 'Input Voltage 1',
    'short_name': 'input_vol1',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.3.3.1.3.2':
    {
    'name': 'Input Voltage 2',
    'short_name': 'input_vol2',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.3.3.1.3.3':
    {
    'name': 'Input Voltage 3',
    'short_name': 'input_vol3',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.4.1.0':
    {
    'name': 'Output Source',
    'short_name': 'output_source',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.4.4.1.2.1':
    {
    'name': 'Output Voltage 1',
    'short_name': 'output_vol1',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.4.4.1.2.2':
    {
    'name': 'Output Voltage 2',
    'short_name': 'output_vol2',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.4.4.1.2.3':
    {
    'name': 'Output Voltage 3',
    'short_name': 'output_vol3',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.4.4.1.5.1':
    {
    'name': 'Output Load 1',
    'short_name': 'output_load1',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.4.4.1.5.2':
    {
    'name': 'Output Load 2',
    'short_name': 'output_load2',
    'type': 'gauge',
    },
  '1.3.6.1.2.1.33.1.4.4.1.5.3':
    {
    'name': 'Output Load 3',
    'short_name': 'output_load3',
    'type': 'gauge',
    },
}

def fetch(host, port):
    ret = None
    objs = [ ObjectType(ObjectIdentity(ObjectIdentifier(oid))) for oid in ETUS_OIDS.keys() ]
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData('public', mpModel=0),
               UdpTransportTarget((host, port)),
               ContextData(),
               *objs
        )
    )
    if errorIndication:
        logging.error(errorIndication)
    elif errorStatus:
        logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        ret = dict()
        for varBind in varBinds:
            logging.info(' = '.join([x.prettyPrint() for x in varBind]))
            name, val = varBind
            ret[str(name.getOid())] = float(val)
    return ret

def main():
    ipaddr = os.getenv('DEVICE_IPADDR', None)
    port = os.getenv('DEVICE_PORT', None)
    tag = os.getenv('DEVICE_TAG', '')
    if len(tag) == 0:
        logging.error('No tag error! Stop program.')
        sys.exit(1)
    # Test device address
    logging.info('Test fetch data')
    fetch(ipaddr, port)

    logging.info('Start loop')
    while True:
        logging.info('Start monitoring')
        data = list()
        try:
            tstamp = int(time.time())
            ret = fetch(ipaddr, port)
            for k, v in ret.items():
                if v <= 0:
                    logging.warning("Unexpected value: {} is {}".format(k,v))
                    continue
                data.append({
                    "measurement": ETUS_OIDS[k]["short_name"],
                    "dev": tag,
                    "value": v,
                    "time": tstamp,
                })
            with open(f'./data/etus_ups_{tag}.log', 'a') as fp:
                fp.write(json.dumps(data)+'\n')
                fp.flush()
            logging.info('End monitoring')
            time.sleep(5)
        except KeyboardInterrupt:
            logging.info('Good bye')
            break
        except:
            logging.exception("Exception")
            time.sleep(5)

if __name__ == "__main__":
    main()
