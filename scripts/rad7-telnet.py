import os
import sys
import time
import json
import logging
from telnetlib import Telnet
import re

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.DEBUG)

def fetch(host, port, fetch_all=False):
    with Telnet(host, port, 900) as tn:
        # Send ETX to initialize connection
        logging.info("Send ETX")
        tn.write(b'\x03\r\n')
        tn.read_until(b'\r\n>', timeout=60)
        tn.write(b'\x03\r\n')
        tn.read_until(b'\r\n>', timeout=60)
        if fetch_all:
            # Read every stored data
            logging.info("Send Special ComAll")
            tn.write(b'Special ComAll\r\n')
            ret = tn.read_until(b'\r\n>').decode('ascii')
        else:
            # Check last reading number
            logging.info("Fetch last reading number")
            datanum = None
            tn.write(b'Special Status\r\n')
            ret = tn.read_until(b'\r\n>', timeout=60).decode('ascii')
            for line in ret.split('\r\n'):
                logging.debug(line)
                m = re.search('^([0-9]+)', line)
                if m is not None:
                    datanum = str.encode(m.group(1).strip()[:2])
            if datanum == None:
                raise ValueError('datanum check failed')
            # Send Data Com <datanum>
            tn.write(b'Data Com ' + datanum + b'\r\n')
            ret = tn.read_until(b'\r\n>', timeout=600).decode('ascii')
        logging.debug(ret)
        # Fetch data
        logging.info("Fetch data")
        dlst = list()
        for line in ret.split('\r\n'):
            d = [ l.strip() for l in line.split(',') ]
            if d[0].isdigit():
                dlst.append(d)
        logging.debug(dlst)
        logging.info("Collect data")
        if not fetch_all and len(dlst) > 5: # Read last 5 data only
            dlst = dlst[-5:]
        ret = list()
        for d in dlst:
            try:
                t = time.strptime(' '.join(d[1:6]), '%y %m %d %H %M')
                tstamp = int(time.mktime(t))
                output = {
                    "recnum": int(d[0]),
                    "totc": float(d[6]),
                    "livet": float(d[7]),
                    "totcA": float(d[8]),
                    "totcB": float(d[9]),
                    "totcC": float(d[10]),
                    "totcD": float(d[11]),
                    "hvlvl": float(d[12]),
                    "hvcycle": float(d[13]),
                    "temp": float(d[14]),
                    "hum": float(d[15]),
                    "leaki": float(d[16]),
                    "batv": float(d[17]),
                    "pumpi": float(d[18]),
                    "flag": int(d[19]),
                    "radon": float(d[20]),
                    "radon_uncert": float(d[21]),
                    "unit": int(d[22]),
                }
                ret.append((tstamp, output))
                logging.debug((tstamp, output))
            except IndexError:
                    logging.exception("Line parsing failed")
                    continue
            except ValueError:
                    logging.exception("Value parsing failed")
                    continue
    return ret

def main():
    ipaddr = os.getenv('DEVICE_IPADDR', None)
    port = int(os.getenv('DEVICE_PORT', None))
    tag = os.getenv('DEVICE_TAG', '')
    sn = os.getenv('DEVICE_SN', '')
    if len(tag) == 0 or len(sn) == 0:
        logging.error('No tag or sn error! Stop program.')
        sys.exit(1)
    logging.info('Start loop')
    while True:
        ret = list()
        for _ in range(5): # try 5 times
            try:
                ret = fetch(ipaddr, port)
            except OSError:
                logging.warning(f"{ipaddr}:{port} connection failed.")
            except ValueError:
                logging.exception("Parsing failed. Retry after 5 secs...")
                time.sleep(5)
                continue
            except KeyboardInterrupt:
                logging.info('Good bye')
                break
            except:
                logging.exception("Exception")
                time.sleep(60)
            break
        data = list()
        for tstamp, d in ret:
            data.append({
                "name": "rad7",
                "dev": sn,
                "pos": tag,
                "time": tstamp,
                **d,
            })
        with open(f'./data/rad7-telnet_{tag}.log','w') as fp:
            fp.write(json.dumps(data)+'\n')
            fp.flush()
        logging.info('End monitoring')
        time.sleep(1800)

if __name__ == '__main__':
    main()
