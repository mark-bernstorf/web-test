from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv

foptions = webdriver.FirefoxOptions()
foptions.accept_insecure_certs = True
foptions.set_preference('security.cert_pinning.enforcement_level', 0)
foptions.set_preference('security.enterprise_roots.enabled', 1)
foptions.set_preference('general.useragent.override', 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0')
foptions.set_preference('dom.webdriver.enabled', False)

#проксю используем как в настройках системы
foptions.set_preference('network.proxy.type', 5)

browser = webdriver.Firefox(options=foptions)
button, block, element = {}, {}, {}

browser.get('https://www.nseindia.com')

# напишем процедуру, которая будет выдавать элементы по мере их появления (ждать, когда загрузятся таблицы, графики и т.д.)
def wait_element(parent, by_, str_, attempt = 0, sleep = 1, single = True, hasbool = False):
    '''
    attempt = число попыток
    sleep = время ожидания после последней неудачи
    single = ищем один элемент (True) или список элементов (False)
    hasbool = выводит буловскую переменую вместо объекта, True = успех, False = провал
    '''
    element_not_rdy = True
    try_count = 0
    while element_not_rdy:
        if (attempt <= try_count):
            try:
                if single:
                    element = parent.find_element(by_, str_)
                else:
                    element = parent.find_elements(by_, str_)
                element_not_rdy = False
            except:
                time.sleep(sleep)
            if attempt > 0:
                try_count += 1
        else:
            print('element not exist:', by_, str_)
            if hasbool:
                return False
                exit()
    if hasbool:
        return True
    return element

#часть 1
desc = '''
    1. Зайти на https://www.nseindia.com
    2. Навестись (hover) на MARKET DATA
    3. Кликнуть на Pre-Open Market
    4. Спарсить данные Final Price по всем позициям на странице и вывести их в csv файл. Имя;цена
'''

print(desc)


button['MARKET DATA'] = browser.find_element(By.XPATH,'//*[@id="link_2"]')
button['MARKET DATA'].click()

#button['Pre-Open Market'] = browser.find_element(By.LINK_TEXT,'Pre-Open Market')
button['Pre-Open Market'] = browser.find_element(By.XPATH,'/html/body/header/nav/div[2]/div/div/ul/li[3]/div/div[1]/div/div[1]/ul/li[1]/a')
#ошибка сертификата внезапно лечится убиением всех печенек
browser.delete_all_cookies()
button['Pre-Open Market'].click()

#block['table'] = browser.find_element(By.ID, 'livePreTable');
block['table'] = wait_element(browser, By.XPATH, 'html/body/div[10]/div/section/div/div/div/div/div/div/div[3]/div/table/tbody');
if wait_element(block['table'], By.CLASS_NAME,'symbol-word-break', hasbool=True, single=False):
    element['label'] = block['table'].find_elements(By.CLASS_NAME,'symbol-word-break')
if wait_element(block['table'], By.CLASS_NAME,'bold', hasbool=True, single=False):
    element['prise'] = block['table'].find_elements(By.CLASS_NAME,'bold') #они единственные жирные

#print(element['label'], element['prise'])
labels, prises = [], []

for i in element['label']:
    labels.append(i.text)

for i in element['prise']:
    prises.append(i.text)

with open('part1.csv', 'w', newline='', encoding='utf8') as file:
    writer = csv.writer(file)
    writer.writerow(('label', 'price')) 
    for i in zip(labels, prises):
        writer.writerow(i) 

#ждём пару секунд, переходим ко второй части
time.sleep(2)

#часть 2
desc = '''
    1. Зайти на главную страницу
    3. Выбрать график "NIFTY BANK"
    2. Пролистать вниз до графика
    4. Нажать “View all” под "TOP 5 STOCKS - NIFTY BANK"
    5. Выбрать в селекторе “NIFTY ALPHA 50”
    6. Пролистать таблицу до конца
'''
print(desc)

#1 заходим на страницу
browser.delete_all_cookies()
browser.get('https://www.nseindia.com')
#2 ищем кнопку, тыкаем
button['NIFTY BANK'] = browser.find_element(By.XPATH, '//*[@id="tabList_NIFTYBANK"]')
button['NIFTY BANK'].click()
#3 скролим до графика
block['plot'] = browser.find_element(By.XPATH, '//*[@id="tab4_container"]')
browser.execute_script("arguments[0].scrollIntoView(true);", block['plot'])
#4 тыкаем на view all
browser.delete_all_cookies()
button['View all'] = wait_element(browser, By.CSS_SELECTOR, '#tab4_gainers_loosers > div:nth-child(3) > a:nth-child(1)')
button['View all'].click()

# тыкаем на "NIFTY ALPHA 50"
button['selector'] = wait_element(browser, By.XPATH, '/html/body/div[10]/div/section/div/div/div/div/div[1]/div/div/div/div[1]/div[1]/div/select/optgroup[4]/option[7]')
button['selector'].click()

#ну и сразу перематываем к концу таблицы, начало другого блока
block['note'] = wait_element(browser, By.CLASS_NAME, '/html/body/div[10]/div/section/div/div/div/div/div[1]/div/div/div/div[5]')
browser.execute_script("arguments[0].scrollIntoView(true);", block['note'])

#ждём 5 секунд, закрываем браузер
time.sleep(5)
browser.quit()
