# Read streaming Lutron sensor data
# Example of data: 02:34:37:30:36:30:31:30:30:30:30:30:31:33:36:0d
# 0,1: header
# 2: code (1: humidity, 2: temperature, ...)
# 5: polarity
# 6: digits after decimal point
# 7-15: value
# 16: end of line
import os
import sys
import time
import json
import struct
import socket
import logging

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

def fetch(host, port, stype):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)
        s.connect((host, port))
        logging.debug("{}:{}".format(host, port))

        hum, temp, dewpoint, wetbulb, o2, o2_temp = None, None, None, None, None, None
        d = b''
        while len(d) < 256:
            tmp = s.recv(256)
            d += tmp

        logging.debug(":".join(["{:02x}".format(c) for c in d]))
        for line in d.split(b'\r'):
            if len(line) < 15:
                continue
            code = chr(line[2])
            polarity = 1.0 if chr(line[5]) == "0" else -1.0
            dp = int(chr(line[6]))
            value = polarity * float(str(line[7:15], "utf-8")) / (10.0**dp)
            if value > 100.0 or value < -100.0:
                logging.warning("Error value: code={}, value={}".format(code, value))
                continue
            if code == "1": # humidity
                hum = value if hum == None else hum
            elif code == "2": # temperature/humidity
                temp = value if temp == None else temp
            elif code == "3": # dewpoint
                dewpoint = value if dewpoint == None else dewpoint
            elif code == "4": # wet-bulb
                wetbulb = value if wetbulb == None else wetbulb
            elif code == "7": # oxygen
                o2 = value if o2 == None else o2
            elif code == "8": # temperature/oxygen
                o2_temp = value if o2_temp == None else o2_temp
            else:
                pass
    if stype == "o2th":
        ret = { "rh_t": temp, "rh": hum, "dew": dewpoint, "wb": wetbulb, "o2_t": o2_temp, "o2": o2 }
    else:
        ret = { "rh_t": temp, "rh": hum, "dew": dewpoint, "wb": wetbulb }
    return ret

def main():
    ipaddr = os.getenv('DEVICE_IPADDR', None)
    port = int(os.getenv('DEVICE_PORT', None))
    tag = os.getenv('DEVICE_TAG', '')
    stype = os.getenv('DEVICE_TYPE', '')
    if len(tag) == 0 or len(stype) == 0:
        logging.error('No tag or type error! Stop program.')
        sys.exit(1)
    logging.info('Start loop')
    while True:
        data = list()
        try:
            logging.info('Start monitoring')
            tstamp_start = int(time.time())
            fields = fetch(ipaddr, port, stype)
            tstamp_end = int(time.time())
            data.append({
                "name": "t_rh_o2",
                "pos": tag,
                "time": tstamp_start,
                **fields,
            })
            with open(f'./data/lutron_{stype}_{tag}.log','a') as fp:
                fp.write(json.dumps(data)+'\n')
                fp.flush()
            logging.info('End monitoring')
            time.sleep(60 - (tstamp_end - tstamp_start))
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

if __name__ == '__main__':
    main()
