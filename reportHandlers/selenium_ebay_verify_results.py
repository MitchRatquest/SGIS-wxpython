from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re, os
import HTMLParser


class SeleniumEbayVerifyResults(unittest.TestCase):
    def setUp(self):
        self.profile = webdriver.FirefoxProfile('C:\\Users\\User\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\7bxp5573.default')
        self.driver = webdriver.Firefox(self.profile)
        self.driver.implicitly_wait(30)
        self.base_url = "http://www.ebay.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.values = self.returnUsernamePassword()
        self.username = self.values[0]
        self.password = self.values[1].rstrip('\r\n')

    def returnUsernamePassword(self):
        with open('../really_secret.txt', 'r') as f:
            lines = f.readlines()[0]
        return lines.split(',')

    def test_selenium_ebay_verifier(self):
        driver = self.driver
        driver.get(self.base_url + "/")
        try:
            driver.find_element_by_link_text("Sign in").click()
            driver.find_element_by_id("userid").clear()
            driver.find_element_by_id("userid").send_keys(self.username)
            driver.find_element_by_id("pass").clear()
            driver.find_element_by_id("pass").send_keys(self.password)
            driver.find_element_by_id("sgnBt").click()
        except:
            pass
        driver.get("http://bulksell.ebay.com/ws/eBayISAPI.dll?FileExchangeUploadResults")
        Select(driver.find_element_by_name("filter")).select_by_visible_text("7 days")
        driver.find_element_by_css_selector("form > input[type=\"submit\"]").click()
        time.sleep(5)
        page_data = driver.page_source
        print(page_data.encode('ascii','ignore'))
        h = HTMLParser.HTMLParser()
        link_list = []
        for link in page_data.split("<a href=\""):
            unescaped_link = link.split('\">Download</a>')[0]
            if unescaped_link.startswith("http://bulksell.ebay.com/ws/eBayISAPI.dll?FileExchangeDownload"):
                if ('>' not in unescaped_link) or ('>' not in unescaped_link):
                    link_list.append(h.unescape(unescaped_link))
            else:
                continue
        # TODO: check previous downloads, if downloaded skip
        for link in link_list:
            try:
                driver.get(link)
                time.sleep(4)
            except Exception, e:
                print(e)
            #u'http://bulksell.ebay.com/ws/eBayISAPI.dll?FileExchangeDownload&jobId=669900377'


        # ERROR: Caught exception [ERROR: Unsupported command [openWindow | ${download_link} | ]]

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True

    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
