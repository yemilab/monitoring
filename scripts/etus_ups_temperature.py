import os
import sys
import time
import json
import struct
import socket
import logging

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

MESSAGE = b"\x66\x11\x44\x55\x97\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xE8\x03\x00\x00"

def fetch(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(5.0)
        s.sendto(MESSAGE, (host, port))
        rawdata = s.recv(1024)
    d = struct.unpack("95i", rawdata)
    igbt1 = d[86] / 10.0
    igbt2 = d[87] / 10.0
    return igbt1, igbt2

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
        logging.debug('Start monitoring')
        data = list()
        try:
            tstamp = int(time.time())
            igbt1, igbt2 = fetch(ipaddr, port)
            data = json.dumps([{
                "name": "invert_temp",
                "dev": tag,
                "fields": { "IGBT1": igbt1, "IGBT2": igbt2 },
                "time": tstamp
            }])
            with open(f'./data/etus_ups_temp_{tag}.log', 'a') as fp:
                fp.write(json.dumps(data)+'\n')
                fp.flush()
            logging.debug('End monitoring')
            time.sleep(5)
        except KeyboardInterrupt:
            logging.info('Good bye')
            break
        except:
            logging.exception("Exception")
            time.sleep(5)
        logging.debug(data)

if __name__ == "__main__":
    main()
