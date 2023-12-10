import requests
import time
import json
import re
from bs4 import BeautifulSoup as bsoup

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': '*/*',
}

response = requests.get('https://2ip.ru')
ip = bsoup(response.text, 'html.parser').find('div', class_='ip').text.strip()

#путь самурая
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.maxmind.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

response = requests.get('https://www.maxmind.com/en/geoip2-precision-demo', headers)

pos_start   = response.text.find('window.MaxMind.X_CSRF_TOKEN = "') + 31
pos_end     = response.text.rfind('";')
token = response.text[pos_start:pos_end]
cookies = {'mm_session':response.headers['set-cookie'].split()[0][11:-1]}

#print(token, cookies)
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.maxmind.com/en/geoip2-precision-demo',
    'X-CSRF-Token': token,
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.maxmind.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

response = requests.post('https://www.maxmind.com/en/geoip2/demo/token', cookies=cookies, headers=headers, allow_redirects=True, verify=False)
#print(response.text)

auth_token = json.loads(response.text)
#print(auth_token['token'])

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.maxmind.com/',
    'Authorization': 'Bearer '+auth_token['token'],
    'Origin': 'https://www.maxmind.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

params = {
    'demo': '1',
}

response = requests.get('https://geoip.maxmind.com/geoip/v2.1/city/'+ip, params=params, headers=headers)
result = json.loads(response.text)
#print(result['location']['time_zone'])
time_zone = result['location']['time_zone']

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': '*/*',
}

response = requests.get('https://gist.github.com/salkar/19df1918ee2aed6669e2')
#print(response.text)

regions = re.findall(r'\[&quot;(.*)&quot;, &quot;'+time_zone+'&quot;\]', response.text)
#print(regions)

with open("part2.txt", "w") as file:
    file.write('Зона: ' + time_zone + "\n")
    file.write('Регионы: '+', '.join(regions))

print('ok')