from zapv2 import ZAPv2
import requests

zap = ZAPv2(apikey='', proxies={
    'http': 'http://54.180.42.140:8090',
    'https': 'http://54.180.42.140:8090'
})

print("ZAP 연결됨:", zap.core.version)

response = requests.get('https://chick-pay.com')
print("응답 코드:", response.status_code)
