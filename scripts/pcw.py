# TOW PCW
#
# Request bytes:
#   | STX | -  | -  | R  | - | - | - |   ETX    |  BCC  |
#   |-----| ADDRESS |TYPE| REQ CODE  | END CODE | CHECK |
#
# Response bytes:
#   | STX | -  | -  | ACK | - | - | - | - | - | - | - | - |   ETX    |  BCC  |
#   |-----| ADDRESS |-----|    CODE   |        DATA       | END CODE | CHECK |
#
# TOW TTM ASCII CODE
# | STX | 0x02 |
# | ETX | 0x03 |
# | ACK | 0x06 |
# | NAK | 0x15 |
#
# Defalut address: '01' => ['0','1']
#
# REQUEST Temperature:
#   | STX | 0 | 1 | R | P | V | 1 | ETX | BCC | ==> ADDRESS: 01, TYPE: Request, CODE: PV1
#
# RESPONSE:
#   | STX | 0 | 1 | ACK | P | V | 1 | 0 | 0 | 0 | 0 | 0 | ETX | BCC |
#      ==> ADDRESS: 01, TYPE: Response, CODE: PV1, DATA: 00000
import os
import sys
import time
import json
import struct
import socket
import logging

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)


def fetch(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10.0)
        s.connect((host, port))
        req = bytearray(b'\x0201RPV1\x03')
        bcc = req[0]
        for r in req[1:]:
            bcc = bcc ^ r
        req.append(bcc)
        res = s.send(req)
        logging.debug(f'RESPONSE: {res}')
        chunk = s.recv(32)
        logging.debug(f'RESPONSE: {chunk}')
        value = float(chunk[7:12]) / 10.0
    return value

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
            value = fetch(ipaddr, port)
            data = {
                "name": "pcw",
                "dev": tag,
                "value": value,
                "time": tstamp,
            }
            with open(f'./data/pcw_{tag}.log','a') as fp:
                fp.write(json.dumps(data)+'\n')
                fp.flush()
            logging.info('End monitoring')
            time.sleep(60)
        except ConnectionRefusedError:
            logging.exception('Exception')
            time.sleep(5) # wait device
        except ValueError:
            logging.exception('Exception')
            time.sleep(5) # wait device
        except KeyboardInterrupt:
            logging.info('Good bye')
            break
        except:
            logging.exception("Exception")
            time.sleep(60)

if __name__ == "__main__":
    main()
