#
# Fetch weather data from data.go.kr
#
import os
import sys
import json
from datetime import datetime, timedelta, timezone
import logging

import requests
from requests.exceptions import HTTPError

logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

URL = 'http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList'

def parse(rows):
    results = list()
    for row in rows:
        result = {'name': 'weather'}
        for k, v in row.items():
            if k == 'tm':
                dt = datetime.strptime(v, '%Y-%m-%d %H:%M')
                dt = dt.replace(tzinfo=timezone(timedelta(hours=9)))
                result['time'] = dt.isoformat()
            elif k == 'rnum': # 목록순서
                continue
            elif v == '':
                result[k] = None
            elif k in (      
                       'stnId',     # 지점번호
                       'dc10Tca',   # 전운량(10분위)
                       'dc10LmcsCa',# 중하층운량(10분위)
                       'lcsCh',     # 최저운고(100m)
                       'vs'         # 시정(10m)
                       ):
                result[k] = int(v)
            elif k in (
                       'ta',     # 기온
                       'rn',     # 강수량(mm)
                       'ws',     # 풍속(m/s)
                       'hm',     # 습도(%)
                       'pv',     # 중기압(hPa)
                       'td',     # 이슬점온도
                       'pa',     # 현지기압
                       'ps',     # 해면기압
                       'ss',     # 일조(hr)
                       'icsr',   # 일사(MH/m^2)
                       'dsnw',   # 적설(cm)
                       'hr3Fhsc',# 3시간 신적설(cm)
                       'ts',     # 지면온도
                       'm005Te', # 5cm 지중온도
                       'm01Te',  # 10cm 지중온도
                       'm02Te',  # 20cm 지중온도
                       'm03Te'   # 30cm 지중온도
                       ):
                result[k] = float(v)
        results.append(result)
    return results

def fetch(url, key, std_id, dt_str):
    payload = {
        'serviceKey': key,
        'dataType': 'JSON',
        'pageNo': 1,
        'numOfRows': 30,
        'dataCd': 'ASOS',
        'dateCd': 'HR',
        'stnIds': std_id,
        'startDt': dt_str,
        'startHh': '00',
        'endDt': dt_str,
        'endHh': '23',
    }
    r = requests.get(url, params=payload)
    r.raise_for_status()
    if r.ok:
        return r.json()
    else:
        return None

def main():
    service_key = os.environ.get('SERVICE_KEY')
    if service_key == None:
        print('SERVICE_KEY environment variable should be set')
        sys.exit(1)
    std_id = os.environ.get('STD_ID')
    if std_id == None:
        std_id = '217' # 강원도 정선군
    dt_str = os.environ.get('DATE')
    if dt_str == None:
        dt = datetime.now() - timedelta(days=1) # Yesterday
        dt_str = dt.strftime('%Y%m%d')

    # Ref: https://pynative.com/parse-json-response-using-python-requests-library/
    try:
        raw_data = fetch(URL, service_key, std_id, dt_str)
    except HTTPError as http_err:
        logging.exception(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logging.exception(f'Other error occurred: {err}')

    try:
        data = parse(raw_data['response']['body']['items']['item'])
    except Exception as err:
        logging.exception(f'Other error occurred: {err}')

    # Store weather data
    with open(f'./data/weather-{dt_str}.log', 'a') as fp:
        for line in data:
            fp.write(json.dumps(line)+'\n')

if __name__ == '__main__':
    main()
