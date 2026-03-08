import urllib.request
import json
import urllib.error

data = json.dumps({'year': 1990, 'month': 1, 'day': 1, 'hour': 12, 'gender': '남', 'cal_type': '양력', 'unknown_time': False, 'is_leap_month': False}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/saju', data=data, headers={'Content-Type': 'application/json'}, method='POST')

try:
    res = urllib.request.urlopen(req)
    print(res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(e.read().decode('utf-8'))
