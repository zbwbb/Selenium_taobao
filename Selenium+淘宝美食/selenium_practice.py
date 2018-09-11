from selenium import webdriver
import time

# 声明浏览器对象
browser = webdriver.Chrome()
try:
    browser.get('https://www.taobao.com')
    # print(browser.page_source)
    input = browser.find_element_by_xpath("//*[@name='q']")
    input.send_keys("婴儿秋冬套装")
    time.sleep(1)
    input.clear()
    input.send_keys('iPhone')
    button = browser.find_element_by_xpath("//*[@class='btn-search tb-bg']")
    button.click()
    # browser.close()
finally:
    print("ok")