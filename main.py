import sys
import urllib
from time import sleep, time
from urllib.request import urlopen
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException, NoSuchElementException
import logging

start_time = time()
firefox_driver = 'geckodriver.exe' if sys.platform == "win32" else 'geckodriver'

_logger = logging.getLogger('YAD2')
_logger.setLevel('INFO')
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)s - %(message)s - %(asctime)s')
sh.setFormatter(formatter)
_logger.addHandler(sh)

# options.add_argument('headless')  # for open headless-browser
options = webdriver.FirefoxOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.headless = True

print("#" * 40)


def get_pages(link):
    headers = dict()
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (HTML, like Gecko) ' \
                            'Chrome/24.0.1312.27 Safari/537.17'
    request = urllib.request.Request(link, headers=headers)
    html = urlopen(request)
    bs_obj = BeautifulSoup(html.read(), features="html.parser")

    for p in bs_obj.findAll("a", {"class": "page-num"}):
        _logger.debug(f'start url: {p.get("href")}')
        yield p.get('href')


i = 0
while True:
    with webdriver.Firefox(executable_path=firefox_driver, firefox_options=options) as browser:
        link_page = "https://www.yad2.co.il/vehicles/private-cars"
        browser.get(link_page)

        _logger.debug(f'get url: {link_page}')

        counter = 0
        while counter != 11000:
            option = 'window.scrollTo(0,' + str(counter) + ')'
            browser.execute_script(option)
            counter += 100

        for item in list(browser.find_elements_by_class_name('feed_item'))[:20]:
            print(f"Value is {i}: {item.get_attribute('item-id')}")
            # item.click()
            browser.execute_script("arguments[0].click();", item)

            sleep(5)
            print('\t', item.find_element_by_class_name('title').text)
            try:
                tel = item.find_element_by_class_name('contact-seller-btn')
                browser.execute_script("arguments[0].click();", tel)
            except NoSuchElementException:
                continue
            # tel.click()
            sleep(2)
            num_tel = item.find_element_by_class_name('phone')
            print(f"\t{num_tel.get_attribute('id')}:")
            for n in num_tel.find_elements_by_tag_name('a'):
                print(f"\t\t{n.get_attribute('href')}")
            i += 1

        el = browser.page_source

        browser.quit()

        bsObj = BeautifulSoup(el, "html.parser")
        my_divs = bsObj.findAll("div", {"class": "private"})

        _logger.info(my_divs)

        print("#" * 40)

        print("--- %s seconds ---" % (time() - start_time))
        sleep(60 * 20)
