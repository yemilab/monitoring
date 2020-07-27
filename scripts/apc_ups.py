import os
import sys
import time
import logging
import json

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

from pysnmp.hlapi import *

APC_OIDS = {
  '1.3.6.1.4.1.318.1.1.1.2.1.1.0':
    {
    'name': 'Battery Status',
    'short_name': 'battery_status',
    'type': 'gauge',
    },
  '1.3.6.1.4.1.318.1.1.1.2.2.1.0':
    {
    'name': 'Battery Charge',
    'short_name': 'battery_charge',
    'type': 'gauge',
    },
  '1.3.6.1.4.1.318.1.1.1.3.2.1.0':
    {
    'name': 'Input Voltage',
    'short_name': 'input_vol',
    'type': 'gauge',
    },
  '1.3.6.1.4.1.318.1.1.1.4.1.1.0':
    {
    'name': 'Output Status',
    'short_name': 'status',
    'type': 'code',
    'code':
       {
       1: 'unknown',
       2: 'onLine',
       3: 'onBattery',
       4: 'onSmartBoost',
       5: 'timedSleeping',
       6: 'softwareBypass',
       7: 'off',
       8: 'rebooting',
       9: 'switchedBypass',
       10: 'hardwareFailureBypass',
       11: 'sleepingUntilPowerReturn',
       12: 'onSmartTrim',
       },
    },
  '1.3.6.1.4.1.318.1.1.1.4.2.1.0':
    {
    'name': 'Output Voltage',
    'short_name': 'output_vol',
    'type': 'gauge',
    },
  '1.3.6.1.4.1.318.1.1.1.4.2.3.0':
    {
    'name': 'Current Load',
    'short_name': 'load',
    'type': 'gauge',
    },
}

def fetch(host, port):
    ret = None
    objs = [ ObjectType(ObjectIdentity(ObjectIdentifier(oid))) for oid in APC_OIDS.keys() ]
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
            logging.debug(' = '.join([x.prettyPrint() for x in varBind]))
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
            tstamp = time.time()
            ret = fetch(ipaddr, port)
            for k, v in ret.items():
                data.append({
                    "name": APC_OIDS[k]["short_name"],
                    "dev": tag,
                    "value": v,
                    "time": int(tstamp),
                })
            with open(f'./data/apc_ups_{tag}.log', 'a') as fp:
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

if __name__ == '__main__':
    main()
