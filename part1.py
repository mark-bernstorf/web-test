import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def wait_element(parent, by_, str_, attempt=0, sleep=1.0, single=True, hasbool=False):
    '''
    Функция ожидает появления элемента с заданым колличеством попыток и временем ожидания.

    Аргументы:
    parent - объект, в котором происходит поиск;
    by_ - по какому локатору осуществляется поиск;
    str_ - искомая строка;
    attempt - число попыток, если == 0 то неограничено;
    sleep - время ожидания после последней неудачи;
    single - ищем один элемент (True) или список элементов (False);
    hasbool - выводит буловскую переменую вместо объекта;

    Пример использования:
    div_element = wait_element(browser, By.CLASS_NAME, 'div');
    '''
    element_not_rdy = True
    try_count = 1  # Задаем счётчик попыток
    while element_not_rdy:
        # Если не привышен лимит попыток, либо если не задан лимит пробуем получить элементы
        if (attempt <= try_count):
            try:
                # При single == True получаем один элемент, при False = список элементов
                element = parent.find_element(
                    by_, str_) if single else parent.find_elements(by_, str_)
                element_not_rdy = False
            except NoSuchElementException:
                # Если ошибка связана с тем, что элемент не найден, ожидаем некоторое время перед началом новой попытки
                time.sleep(sleep)
            if attempt > 0:
                try_count += 1
        else:
            # В случае исчерпания попыток выводим сообщение, что элемент найти не удалось
            print('element not exist:', by_, str_)
            if hasbool:  # Если нужен булевский результат выводим его
                return False
    if hasbool:
        return True
    return element


# Перед созданием экземпляра WebDriver.Firefox зададим первоначальные настройки:
foptions = webdriver.FirefoxOptions()
# Будем доверять небезопасным сертификатам
foptions.accept_insecure_certs = True
# Пининг сертификатов не используется
foptions.set_preference('security.cert_pinning.enforcement_level', 0)
# Доверять корневым сертификатам, установленным и управляемым организацией или предприятием
foptions.set_preference('security.enterprise_roots.enabled', 1)
# Выдаем себя за обычный браузер
foptions.set_preference('general.useragent.override',
                        'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0')
# Скрываем использование автоматизированных средств.
foptions.set_preference('dom.webdriver.enabled', False)
# Прокси используем как в настройках системы
foptions.set_preference('network.proxy.type', 5)
# Создаем экземпляр браузера Mozilla Firefox с определенными выше параметрами веб-драйвера
browser = webdriver.Firefox(options=foptions)
# Для удобства и более понятного визуального понимания кода создадим словари с элементами
button, block, element = {}, {}, {}
# Приступаем к выполнению первой части задания
desc = '''
    1. Зайти на https://www.nseindia.com
    2. Навестись (hover) на MARKET DATA
    3. Кликнуть на Pre-Open Market
    4. Спарсить данные Final Price по всем позициям на странице и вывести их в csv файл. Имя;цена
    upd: по рекомендации используем CSS_SELECTOR там, где это более оправдано
'''
print(desc)
browser.get('https://www.nseindia.com')  # Зайти на https://www.nseindia.com
button['MARKET DATA'] = browser.find_element(
    By.CSS_SELECTOR, '#link_2')  # Поиск и выбор "MARKET DATA"
button['MARKET DATA'].click()
# Ищем и кликаем на Pre-Open Market
button['Pre-Open Market'] = browser.find_element(
    By.PARTIAL_LINK_TEXT, 'Pre-Open Market')
# Ошибка сертификата внезапно лечится убиением всех печенек
browser.delete_all_cookies()
button['Pre-Open Market'].click()
block['table'] = wait_element(
    browser, By.CSS_SELECTOR, '#livePreTable')  # Ждём таблицу
# Ждём загрузки таблицы и получаем имена
if wait_element(block['table'], By.CLASS_NAME, 'symbol-word-break', hasbool=True, single=False):
    element['label'] = block['table'].find_elements(
        By.CLASS_NAME, 'symbol-word-break')
# Ищём в таблице "Prise"
if wait_element(block['table'], By.CLASS_NAME, 'bold', hasbool=True, single=False):
    element['prise'] = block['table'].find_elements(
        By.CLASS_NAME, 'bold')  # Они единственные жирные
labels, prises = [], []  # Создадим списки с именем и ценой
for i in element['label']:
    labels.append(i.text)
for i in element['prise']:
    prises.append(i.text)
# Сохраняем результат в CSV файл
with open('part1.csv', 'w', newline='', encoding='utf8') as file:
    writer = csv.writer(file)
    writer.writerow(('label', 'price'))
    for i in zip(labels, prises):
        writer.writerow(i)
time.sleep(2)  # Ждём пару секунд, переходим ко второй части
desc = '''
    1. Зайти на главную страницу
    3. Выбрать график "NIFTY BANK"
    2. Пролистать вниз до графика
    4. Нажать “View all” под "TOP 5 STOCKS - NIFTY BANK"
    5. Выбрать в селекторе “NIFTY ALPHA 50”
    6. Пролистать таблицу до конца
'''
print(desc)
browser.delete_all_cookies()
browser.get('https://www.nseindia.com')  # Зайти на главную страницу
button['NIFTY BANK'] = browser.find_element(
    By.CSS_SELECTOR, '#tabList_NIFTYBANK')  # Выбрать график "NIFTY BANK"
button['NIFTY BANK'].click()
block['plot'] = browser.find_element(
    By.CSS_SELECTOR, '#tab4_container')  # Ждём график
# Пролистаем вниз до графика
browser.execute_script("arguments[0].scrollIntoView(true);", block['plot'])
browser.delete_all_cookies()
# Ищем и тыкаем на view all
button['View all'] = wait_element(
    browser, By.CSS_SELECTOR, '#tab4_gainers_loosers > div:nth-child(3) > a:nth-child(1)')  
button['View all'].click()
# Ищем и тыкаем на "NIFTY ALPHA 50"
button['selector'] = wait_element(
    browser, By.CSS_SELECTOR, '#equitieStockSelect > optgroup:nth-child(4) > option:nth-child(7)')
button['selector'].click()
# Поиск блока в конце таблицы
block['note'] = wait_element(
    browser, By.CSS_SELECTOR, 'div.note_container:nth-child(5)')
# Пролистываем до него
browser.execute_script("arguments[0].scrollIntoView(true);", block['note'])
print('Задание выполнено')
time.sleep(5)  # Ждём 5 секунд перед закрытием браузера
browser.quit()
