import serial
import time
import json

DEV = '/dev/serial/by-id/usb-Dekist_Co.__Ltd._UA_SERIES__19060001-if00'

with serial.Serial(DEV,19200) as ser:
    # Read serial number
    number = ser.write(b'ATCMODEL\r\n')
    res = ser.readline().strip() #Sensor response example: b'ATCMODEL 19060001'
    sn = res.decode('utf-8').split()[1]

    #Read oxygen level and temperture
    while True:
        try:
            result = ser.write(b'ATCD\r\n')
            res = ser.readline()                      #Sensor reponse example :b'ATCD20.40,25.2'
            values = res.decode('utf-8').split()[1]   #Decoded value example : 20.40,25.2
            o2, temp = values.split(',')
            data = {
                'name': 'o2',
                'pos': 'a5hpge',
                'vender': 'dekist',
                'model': 'UA-52',
                'sn': sn,
                'o2': float(o2),
                'temp': float(temp),
                'time': int(time.time()),
            }

            with open('data.log','a') as fp:
                fp.write(json.dumps(data)+'\n')
            time.sleep(60)

        except KeyboardInterrupt:
            break
