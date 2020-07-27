import os
import sys
import time
import json
import logging
import datetime

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

def fetch(host, port):
    ret = None
    with ModbusClient(host, port=port) as client:
        # Read V12, V23, V31, A1, A2, A3, W, pf, var, Hz, Wh_High, Wh_Low
        # varh_High, varh_Low, V1, V2, V3, W1, W2, W3, VA1, VA2, VA3, VA
        rr = client.read_input_registers(0x00, 31, unit=0xFF)
        decoder = BinaryPayloadDecoder.fromRegisters(rr.registers, byteorder=Endian.Big)
        i3v = [ float(decoder.decode_16bit_int())/10.0 for _ in range(3) ]
        i3i = [ float(decoder.decode_16bit_int())/1000.0 for _ in range(3) ]
        W = float(decoder.decode_16bit_int())
        pf = float(decoder.decode_16bit_int())
        var = float(decoder.decode_16bit_int())
        Hz = float(decoder.decode_16bit_int())/100.0
        Wh_High = float(decoder.decode_16bit_int())
        Wh_Low = float(decoder.decode_16bit_int())
        varh_High = float(decoder.decode_16bit_int())
        varh_Low = float(decoder.decode_16bit_int())
        i2v = [ float(decoder.decode_16bit_int())/10.0 for _ in range(3) ]
        An = float(decoder.decode_16bit_int())
        W123 = [ float(decoder.decode_16bit_int()) for _ in range(3) ]
        var123 = [ float(decoder.decode_16bit_int()) for _ in range(3) ]
        pf123 = [ float(decoder.decode_16bit_int()) for _ in range(3) ]
        VA123 = [ float(decoder.decode_16bit_int()) for _ in range(3) ]
        VA = float(decoder.decode_16bit_int())
        # Read maxV(R,S,T), maxVV(R,S,T), maxI(R,S,T), maxW, maxHz, temperatures
        rr = client.read_input_registers(0x27, 15, unit=0xFF)
        decoder = BinaryPayloadDecoder.fromRegisters(rr.registers, byteorder=Endian.Big)
        maxV = [ float(decoder.decode_16bit_int())/10.0 for _ in range(3) ]
        maxVV = [ float(decoder.decode_16bit_int())/10.0 for _ in range(3) ]
        maxI = [ float(decoder.decode_16bit_int())/1000.0 for _ in range(3) ]
        maxW = float(decoder.decode_16bit_int())
        maxHz = float(decoder.decode_16bit_int())
        max_temp = [ float(decoder.decode_16bit_int()) for _ in range(2) ]
        temp = [ float(decoder.decode_16bit_int()) for _ in range(2) ]
        ret = {
            "In3V1": i3v[0],
            "In3V2": i3v[1],
            "In3V3": i3v[2],
            "In3I1": i3i[0],
            "In3I2": i3i[1],
            "In3I3": i3i[2],
            "In2V1": i2v[0],
            "In2V2": i2v[1],
            "In2V3": i2v[2],
            "W": W,
            "Hz": Hz,
            "W1": W123[0],
            "W2": W123[1],
            "W3": W123[2],
            "VA1": VA123[0],
            "VA2": VA123[1],
            "VA3": VA123[2],
            "VA": VA,
            "maxV_R": maxV[0],
            "maxV_S": maxV[1],
            "maxV_T": maxV[2],
            "maxVV_R": maxVV[0],
            "maxVV_S": maxVV[1],
            "maxVV_T": maxVV[2],
            "maxI_R": maxI[0],
            "maxI_S": maxI[1],
            "maxI_T": maxI[2],
            "maxW": maxW,
            "maxHz": maxHz,
            "Temp1": temp[0],
            "Temp2": temp[1],
        }
    return ret

def main():
    ipaddr = os.getenv('DEVICE_IPADDR', None)
    port = int(os.getenv('DEVICE_PORT', None))
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
        data = []
        try:
            tstamp = int(time.time())
            fields = fetch(ipaddr, port)
            data = [{
                "name": "avr",
                "pos": tag,
                "time": tstamp,
                **fields
            }]
            with open(f'./data/avr_{tag}.log', 'a') as fp:
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
