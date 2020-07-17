import sys
import logging

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

def fetch_snmp(self, host, port):
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
            logging.info(' = '.join([x.prettyPrint() for x in varBind]))
            name, val = varBind
            ret[str(name.getOid())] = float(val)
    return ret

def write(self):
    data = list()
    for host, dev in self.upslist:
        try:
            tstamp = time.time()
            ret = self.fetch_snmp(host, 161)
            for k, v in ret.items():
                data.append({
                    "measurement": APC_OIDS[k]["short_name"],
                    "tags": { "dev": dev },
                    "fields": { "value": v},
                    "time": int(tstamp),
                })
        except:
            logging.exception("Exception")
    logging.info(data)
    return json.dumps(data)
