import os
import sys
import time
import json
import struct
import socket
import logging
import re

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.DEBUG)

def fetch(host, port):
    line = None
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(60.0)
        s.connect((host, port))
        chunk = b""
        for _ in range(32):
            chunk += s.recv(16)
            logging.debug(chunk)
            m = re.search(">(.+)<", chunk.decode("utf-8", errors="ignore"))
            if m is not None:
                line = m.group(1)
                break
    if line == None:
        logging.error("Failed")
        return None
    else:
        raw = line.split(",")
    data = dict()
    Sinput, Scontrol = raw[0][2:].split("-")
    data["Sinput"] = int(Sinput)
    data["Scontrol"] = 1 if Scontrol == "ON" else 0
    for i in [1, 2, 3, 4, 5, 6, 8, 10, 11, 12]:
        k, v = raw[i].split("=")
        if k == "F":
            data[k] = float(v)/10.0
        else:
            data[k] = int(v)
    for i in [7, 9]:
        key, value = raw[i].split("=")
        for j, bit in enumerate(value):
            data["{}{}".format(key, j)] = int(bit)
    data["UnitType"] = raw[13]
    return data

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
            fields = fetch(ipaddr, port)
            if fields == None:
                time.sleep(5)
                continue
            with open(f'./data/n2gen_{tag}.log','a') as fp:
                lst_fields = list()
                for k, v in fields.items():
                    if isinstance(v, int):
                        lst_fields.append(f'{k}={v}i')
                    elif isinstance(v, float):
                        lst_fields.append(f'{k}={v}')
                    else:
                        lst_fields.append(f'{k}="{v}"')
                line_fields = ','.join(lst_fields)
                fp.write(f'n2gen,dev={tag} {line_fields} {tstamp*(10**9)}\n')
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
