import requests
import time
import json
import re
from bs4 import BeautifulSoup as bsoup

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0'


def parse_ip():
    '''Переходим на сайт 2ip.ru и получаем ip адрес'''
    # Перед отправкой запроса сформируем минимальный заголовок, представимся реальным браузером
    headers = {'User-Agent': USER_AGENT}
    # Нужно перейти по ссылке https://2ip.ru/ и спарсить свой ip-адрес
    response = requests.get('https://2ip.ru')
    # Для удобства будем использовать BeautifulSoup при парсинге
    ip = bsoup(response.text, 'html.parser').find(
        'div', class_='ip').text.strip()
    print(ip)
    return ip


def parse_x_csrf_token(html):
    '''Получаем x-csrf токен из тела'''
    pos_start = html.find('X_CSRF_TOKEN = "') + 16
    pos_end = html.rfind('";')
    return html[pos_start:pos_end]


def parse_timezone(ip):
    '''Получаем таймзону с maxmind.com'''
    # Нужно перейти по ссылке https://www.maxmind.com/en/geoip2-precision-demo и получить название таймзоны у своего ip-адреса
    # Сформируем заголовок таким, как если бы мы заходили с реального браузера и перейдём по ссылке
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.maxmind.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    response = requests.get(
        'https://www.maxmind.com/en/geoip2-precision-demo', headers)
    # Нам необходимо достать X-CSRF-Token и запомнить куки, которые пришли в ответ на запрос
    # 1. Получаем X-CSRF-Token:
    x_csrf_token = parse_x_csrf_token(response.text)
    # 2. Запоминаем куки
    cookies = {'mm_session': response.headers['set-cookie'].split()[0][11:-1]}
    print(f'X-CSRF-Token = {x_csrf_token}, cookies = {cookies}')
    # Передаем полученый токен в заголовок
    headers['X-CSRF-Token'] = x_csrf_token
    # Теперь нам нужно получить токен уже для доступа к geoip.maxmind.com
    # Отправляем запрос с токеном в заголовке и печеньками, разрешаем редиректы и отключаем проверку сертификата
    response = requests.post('https://www.maxmind.com/en/geoip2/demo/token',
                             cookies=cookies, headers=headers, allow_redirects=True, verify=False)
    # Нам пришёл токен для авторизации, сразу представим его в виде json объекта
    auth_token = json.loads(response.text)
    print(auth_token['token'])
    # Теперь мы можем получить информацию о временой зоне нашего адреса
    # Подставляем в заголовок полученый токен для авторизации
    headers['Authorization'] = 'Bearer '+auth_token['token']
    # Передадим парамерт demo=1
    params = {'demo': '1'}
    # Отправляем запрос с токеном авторизации в заголовке и параметром, подставляем IP
    response = requests.get(
        'https://geoip.maxmind.com/geoip/v2.1/city/'+ip, params=params, headers=headers)
    # В результате получаем много полезной информации в формате JSON, там есть и интересующая нас временая зона
    json_result = json.loads(response.text)
    print(f'full json = {response.text}')
    print(f'only time_zone = {json_result["location"]["time_zone"]}')
    return json_result["location"]["time_zone"]


def parse_regions(time_zone):
    '''Получаем список регинтов входящих во временую зону адреса'''
    # Теперь нужно перейти по ссылке https://gist.github.com/salkar/19df1918ee2aed6669e2 и получить список регионов, входящих в полученную таймзону
    # Снова представимся обычным браузером и отправим запрос
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(
        'https://gist.github.com/salkar/19df1918ee2aed6669e2')
    # Парсим из ответа все строки в которых встречаем нашу временую зону
    return re.findall(r'\[&quot;(.*)&quot;, &quot;' +
                      time_zone+'&quot;\]', response.text)


def save_data_to_txt(out_file, data):
    with open(out_file, "w") as file:
        file.write(data)


# Получаем IP:
ip = parse_ip()
# Получаем таймзону:
time_zone = parse_timezone(ip)
# Получаем регионы
regions = parse_regions(time_zone)
# Сохраняем результат в текстовый файл
save_data_to_txt('part2.txt', time_zone+'\n'+', '.join(regions))
print('Задание выполнено')
