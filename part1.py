import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


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
    try_count = 0  # Обнуляем счётчик попыток
    while element_not_rdy:
        # Если не привышен лимит попыток, либо если не задан лимит пробуем получить элементы
        if (attempt >= try_count):
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
            print('NoSuchElementException:', by_, str_)
            return False
    # Возращаем либо найденый элемент, либо булевское значение при hasbool=True
    return element if not hasbool else True


def close_ad(browser):
    '''Процедура закрывает всплывающее модальное окно если оно активно'''
    # У открытого модального окна класс "modal fade show", проверяем его наличие
    modal_wnd_show = wait_element(
        browser, By.CLASS_NAME, 'modal fade show', attempt=1, hasbool=True)
    if modal_wnd_show:
        # Если окно найдено, ищем кнопку закрытия и кликаем, на всякий случай ставим две попытки
        modal_wnd = wait_element(
            browser, By.CSS_SELECTOR, 'button.close:nth-child(1)', attempt=2)
        if modal_wnd:
            modal_wnd.click()


def click_without_exception(browser, element, attempt=0, sleep=1.0):
    '''Функция ждёт пока элемент не станет кликабельным и кликает по нему.

    Аргументы:
    element - элемент, на который нужно кликнуть;
    attempt - число попыток, если == 0 то неограничено;
    sleep - время ожидания после последней неудачи;

    Примечание:
    Если страница динамически подгружается после загрузки (например, при загрузке таблиц либо графиков) 
    некоторые элементы являются некликабельны, пока всё не прогрузится окончательно. Чтоб не получать ошибку
    и дождаться "кликабельности" кнопки можно воспользоваться этой функцией. Так же помогает если
    внезапно вылезло модальное окно.
    '''
    element_not_rdy = True
    try_count = 0  # Обнуляем счётчик попыток
    while element_not_rdy:
        # Если не привышен лимит попыток, либо если не задан лимит пробуем кликнуть
        if (attempt >= try_count):
            try:
                element.click()
                element_not_rdy = False
            except ElementClickInterceptedException:
                # На всякий случай проверяем, если внезапно вылезло модальное окно или мы не успели кликнуть до его появления
                close_ad(browser)
                # Если клик по элементу не может быть выполнен, ожидаем некоторое время перед началом новой попытки
                time.sleep(sleep)
            if attempt > 0:
                try_count += 1
        else:
            # В случае исчерпания попыток выводим сообщение
            print('ElementClickInterceptedException:', element)
            return False
    return True


def browser_init():
    '''Функция создает экземпляр WebDriver.Firefox'''
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
    return webdriver.Firefox(options=foptions)


def scroll_to_element(browser, element, behavior='smooth', block='center', inline='start'):
    '''
    Пролистывает страницу до нужного элемента

    Аргументы:
    browser - экземпляр браузера;
    element - элемент, до коротого нужно проскролить;
    behavior - анимация прокрутки. Принимает значения "auto" или "smooth";
    block - вертикальное выравнивание. Одно из значений: "start", "center", "end" или "nearest";
    inline - горизонтальное выравнивание. Одно из значений: "start", "center", "end" или "nearest";

    Пример использования:
    scroll_to_element(browser, element, block='end')
    '''
    scroll_options = {'behavior': behavior, 'block': block, 'inline': inline}
    browser.execute_script(
        f'arguments[0].scrollIntoView({scroll_options});', element)


def save_data_to_csv(out_file, data):
    '''Сохраняем данные в CSV файл'''
    with open(out_file, 'w', newline='', encoding='utf8') as file:
        writer = csv.writer(file)
        for i in data:
            writer.writerow(i)


def task_1():
    '''
    Задача 1:
    1. Зайти на https://www.nseindia.com
    2. Навестись (hover) на MARKET DATA
    3. Кликнуть на Pre-Open Market
    4. Спарсить данные Final Price по всем позициям на странице и вывести их в csv файл. Имя;цена
    upd: по рекомендации используем CSS_SELECTOR там, где это более оправдано
    upd2: разбить код на логические блоки (функции)
    '''
    # Создаем экземпляр браузера
    browser = browser_init()
    # Для удобства и более понятного визуального понимания кода создадим словари с элементами
    button, block, element = {}, {}, {}
    # Зайти на https://www.nseindia.com
    browser.get('https://www.nseindia.com')
    button['MARKET DATA'] = browser.find_element(
        By.CSS_SELECTOR, '#link_2')  # Поиск и выбор "MARKET DATA"
    click_without_exception(browser, button['MARKET DATA'])
    # Ищем и кликаем на Pre-Open Market
    button['Pre-Open Market'] = browser.find_element(
        By.PARTIAL_LINK_TEXT, 'Pre-Open Market')
    # Ошибка сертификата внезапно лечится убиением всех печенек
    browser.delete_all_cookies()
    click_without_exception(browser, button['Pre-Open Market'])
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
    labels, prises = ['label'], ['prise']  # Создадим списки с именем и ценой
    for i in element['label']:
        labels.append(i.text)
    for i in element['prise']:
        prises.append(i.text)
    # Сохраняем результат в CSV
    save_data_to_csv('part1.csv', zip(labels, prises))
    # Закрываем браузер и завершаем работу вебдрайвера
    browser.quit()
    return True


def task_2():
    '''
    Задание 2:
    1. Зайти на главную страницу
    3. Выбрать график "NIFTY BANK"
    2. Пролистать вниз до графика
    4. Нажать “View all” под "TOP 5 STOCKS - NIFTY BANK"
    5. Выбрать в селекторе “NIFTY ALPHA 50”
    6. Пролистать таблицу до конца
    '''
    # Создаем экземпляр браузера
    browser = browser_init()
    # Для удобства и более понятного визуального понимания кода создадим словари с элементами
    button, block, element = {}, {}, {}
    browser.get('https://www.nseindia.com')  # Зайти на главную страницу
    button['NIFTY BANK'] = browser.find_element(
        By.CSS_SELECTOR, '#tabList_NIFTYBANK')  # Выбрать график "NIFTY BANK"
    click_without_exception(browser, button['NIFTY BANK'])
    block['plot'] = browser.find_element(
        By.CSS_SELECTOR, '#tab4_container')  # Ждём график
    # Пролистаем вниз до графика
    scroll_to_element(browser, block['plot'])
    browser.delete_all_cookies()
    # Ищем и тыкаем на view all
    button['View all'] = wait_element(
        browser, By.CSS_SELECTOR, '#tab4_gainers_loosers > div:nth-child(3) > a:nth-child(1)')
    # Если график подгружается с задержкой, иногда кнопка не кликабельна, процедура "click_without_exception" это фиксит:
    click_without_exception(browser, button['View all'])
    # Ищем и тыкаем на "NIFTY ALPHA 50"
    button['selector'] = wait_element(
        browser, By.CSS_SELECTOR, '#equitieStockSelect > optgroup:nth-child(4) > option:nth-child(7)')
    click_without_exception(browser, button['selector'])
    # Поиск блока в конце таблицы
    block['note'] = wait_element(
        browser, By.CSS_SELECTOR, 'div.note_container:nth-child(5)')
    # Пролистываем до него
    scroll_to_element(browser, block['note'])
    time.sleep(2)  # Ждём пару секунд перед закрытием браузера
    browser.quit()
    return True


# Разобьём две части задания на два блока:
if task_1():
    print('Первая часть задания выполнена')
if task_2():
    print('Вторая часть задания выполнена')
