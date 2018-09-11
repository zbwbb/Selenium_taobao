from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
from bs4 import BeautifulSoup
from config import *
import pymongo
import json

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)
client = pymongo.MongoClient(MONGO_URL)
db = client.MONGO_DB
collection = db.MONGO_COLLECTION


def search():
    try:
        browser.get('https://www.taobao.com')
        # input_key = wait.until(EC.presence_of_element_located(By.XPATH, "//*[@name='q']"))
        input_key = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-search"))
        )
        input_key.send_keys("iPhone")
        submit.click()

        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total'))
        )
        return total.text
    except TimeoutException:
        search()
    finally:
        print("finally")
        # browser.close()


def next_page(page_number):
    try:
        input_key = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        submit = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit"))
        )
        input_key.clear()
        input_key.send_keys(str(page_number))
        submit.click()

        # 判断是否翻页成功
        wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > ul > li.item.active > span"), str(page_number))
        )

        # 解析数据
        product_info = get_products()
        for info in product_info:
            print(info)
            save_to_mongodata(info)

    except TimeoutException:
        next_page(page_number)


# 存取数据
def save_to_mongodata(result):
    try:
        if collection.insert(result):
            print("插入成功")
            return True
        return False
    except Exception as e:
        print(e.reason)
        return False


# 解析
def get_products():
    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item'))
        )
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        items = soup.select('#mainsrp-itemlist .items .item')
        for item in items:
            yield {
                'image': item.select('.pic img')[0].attrs['src'],
                'name': item.select('.pic img')[0].attrs['alt'],
                'price': item.select('.ctx-box .price span')[0].string + item.select('.ctx-box .price strong')[
                    0].string,
                'number': item.select('.ctx-box .deal-cnt')[0].get_text()
            }
    except TimeoutException:
        get_products(html)


def main():
    total = search()
    pattern = re.compile('(\d+)')
    number = int(re.search(pattern, total).group(1))
    number = 20
    for i in range(2, number + 1):
        next_page(i)


if __name__ == '__main__':
    main()
