# TODO: It is unfinished code
#
import os
import sys
import time
import re
import logging
import json
import socket

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)

BUFSIZE = 1024

def read_until_prompt(sock):
    data = bytearray(BUFSIZE)
    for i in range(BUFSIZE):
        b = sock.recv(BUFSIZE)
        if len(b) > 0:
            data[i] = b[0]
            if i >= 2:
                if data[i-2:i+1] == b'\r\n>':
                    logging.debug('Prompt line founded')
                    break
        else:
            logging.debug('Read timeout or no data')
            break
    return data.decode('ascii')

def parse_runnum(data):
    runnum = None
    for line in data.split('\r\n'):
        m = re.search('^([0-9]+)', line)
        if m is not None:
            runnum = int(m.group(1).strip()[:2])
    return runnum

def parse_data(data):
    dlst = list()
    for line in data.split('\r\n'):
        d = [ l.strip() for l in line.split(',') ]
        if d[0].isdigit():
            dlst.append(d)
    ret = list()
    for d in dlst:
        try:
            t = time.strptime(' '.join(d[1:6]), '%y %m %d %H %M')
            tstamp = int(time.mktime(t))
            output = {
                'time': tstamp,
                'recnum': int(d[0]),
                'totc': float(d[6]),
                'livet': float(d[7]),
                'totcA': float(d[8]),
                'totcB': float(d[9]),
                'totcC': float(d[10]),
                'totcD': float(d[11]),
                'hvlvl': float(d[12]),
                'hvcycle': float(d[13]),
                'temp': float(d[14]),
                'hum': float(d[15]),
                'leaki': float(d[16]),
                'batv': float(d[17]),
                'pumpi': float(d[18]),
                'flag': int(d[19]),
                'radon': float(d[20]),
                'radon_uncert': float(d[21]),
                'unit': int(d[22]),
            }
            ret.append(output)
        except IndexError:
            logging.exception('Line parsing failed')
            continue
        except ValueError:
            logging.exception('Value parsing failed')
            continue
    return ret

def fetch(ipaddr, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ipaddr, port))
        logging.info('Send ETX')
        s.sendall(b'\x03\r\n')
        res = read_until_prompt(s)
        s.sendall(b'\x03\r\n')
        res = read_until_prompt(s)
        logging.info('Send Special Status')
        s.sendall(b'Special Status\r\n')
        res = read_until_prompt(s)
        runnum = parse_runnum(res)
        logging.info(f'Send Data Com {runnum:02d}')
        s.sendall(f'Data Com {runnum:2d}\r\n'.encode('ascii'))
        res = read_until_prompt(s)
        logging.info('Parse data')
        ret = parse_data(res)
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
                logging.error(f'{ipaddr}:{port} connection failed.')
                break
            except ValueError:
                logging.exception('Parsing failed. Retry after 5 secs...')
                time.sleep(5)
                continue
            except KeyboardInterrupt:
                logging.info('Good bye')
                break
            except:
                logging.exception('Exception')
                time.sleep(60)
            break
        try:
            data = list()
            for tstamp, d in ret:
                data.append({
                    'name': 'rad7',
                    'dev': sn,
                    'pos': tag,
                    'time': tstamp,
                    **d,
                })
            with open(f'./data/rad7-socket_{tag}.log', 'w') as fp:
                fp.write(json.dumps(data)+'\n')
                fp.flush()
                time.sleep(600)
        except KeyboardInterrupt:
            logging.info('Good bye')
            break
        except:
            logging.exception('Exception: ')
            time.sleep(600)

if __name__ == '__main__':
    main()
