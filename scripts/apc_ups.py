import os
import sys
import time
import logging

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

from pysnmp.hlapi import *
from influxdb import InfluxDBClient

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
    db = InfluxDBClient(
             host=os.getenv('INFLUXDB_HOST', None),
             port=int(os.getenv('INFLUXDB_PORT', None)),
             database=os.getenv('INFLUXDB_NAME', None),
             username=os.getenv('INFLUXDB_USER', None),
             password=os.getenv('INFLUXDB_PASS', None),
             ssl=True if os.getenv('INFLUXDB_VERIFYSSL', None) == 'True' else False,
             verify_ssl= True if os.getenv('INFLUXDB_VERIFYSSL', None) == 'True' else False,
         )
    # Test device address
    fetch(os.getenv('DEVICE_IPADDR', None), os.getenv('DEVICE_PORT', None))
    while True:
        data = list()
        try:
            tstamp = time.time()
            ret = fetch(os.getenv('DEVICE_IPADDR', None), int(os.getenv('DEVICE_PORT', None)))
            for k, v in ret.items():
                data.append({
                    "measurement": APC_OIDS[k]["short_name"],
                    "tags": { "dev": os.getenv('DEVICE_TAG', '') },
                    "fields": { "value": v },
                    "time": int(tstamp),
                })
            db.write_points(data, time_precision="s")
            time.sleep(5)
        except KeyboardInterrupt:
            logging.info('Good bye')
            break
        except:
            logging.exception("Exception")
            time.sleep(5)
        logging.info(data)

if __name__ == '__main__':
    main()
