from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re, os
import httplib
import urllib2
import json
import traceback


def getVerifyQueue():
        '''
        urllib2 does not support javascript/AJAX implemented
        javascript_support.selenium_browser_save_page(url,fp) just in case?
        '''
        cwd = os.getcwd()
        verificationRequestsDirPath = os.path.join(cwd,'verificationRequestsQueue')

        year = str(time.localtime()[0])
        month = str(time.localtime()[1])
        day = str(time.localtime()[2])
        count = len([name for name in os.listdir(verificationRequestsDirPath) if '_'.join([year,month,day,'verificationRequestsQueue.csv']) in name])
        if count != 0:
            count += 1
        csv_fn = '_'.join([year,month,day,'verificationRequestsQueue.csv'])
        csv_fn = str(count)+'_'+csv_fn
        verificationRequestCsvName = csv_fn
        seleniumJson = str(count)+'_'+'_'.join([year,month,day,'selenium.json'])
        json_url = 'http://192.168.0.170/selenium/'+seleniumJson
        print('Found/Creating: ' + csv_fn)

        csv_fp = os.path.join(verificationRequestsDirPath,csv_fn)
        httplib.HTTPConnection.debuglevel = 1
        print("getVerifyQueue(): Fetching:" + json_url)
        try:
            print(json_url)
            json_url = 'http://192.168.0.170/selenium/'+seleniumJson
            try:
                request = urllib2.Request(json_url)
            except HTTPError, e:
                print(e)
                print(traceback.format_exc())
                return None
            request.add_header('User-Agent','jmunsch_thnx_v2.0 +http://jamesmunsch.com/')
            opener = urllib2.build_opener()
            data = opener.open(request).read()
            data = json.loads(data)
            data = ''.join(data)
            data = data.replace('\r\n','\n')
            print(repr(data))
            print(type(data))
            print(seleniumJson)
            print(csv_fn)
            print('Trying to Write:' + csv_fp)
            # write csv file return fp
            with open(csv_fp, 'w+') as f:
                f.write(data)
            print "Fetched."
        except Exception, e:
            print "\n# getVerifyQueue(): #"
            print traceback.format_exc()
            data = None
            print e
            return None

        return csv_fp




def getFn():
    '''
    hack? to pass fn from display_image.PhotoCtrl to local
    '''
    with open('tmp_fn','r') as f:
        verifyRequestFp = f.read()
    print(verifyRequestFp)
    os.remove('tmp_fn')
    return verifyRequestFp

cwd = os.getcwd()
verificationRequestsResultsDirPath = os.path.join(cwd,'VerificationRequestsResults')
verifyRequestNumberFp = os.path.join(verificationRequestsResultsDirPath,'verifyRequestRefNumber.csv')


class SeleniumEbayVerifyUploader(unittest.TestCase):
    def setUp(self):
        self.profile = webdriver.FirefoxProfile('C:\\Users\\User\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\7bxp5573.default')
        self.driver = webdriver.Firefox(self.profile)
        self.driver.implicitly_wait(30)
        self.base_url = "http://www.ebay.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.jsonFp = getVerifyQueue()
        if self.jsonFp is None:
            self.driver.close()
            self.tearDown(self)
        self.values = self.returnUsernamePassword()
        self.username = self.values[0]
        self.password = self.values[1].rstrip('\r\n')

    def returnUsernamePassword(self):
        with open('../../../really_secret.txt', 'r') as f:
            lines = f.readlines()[0]
        return lines.split(',')

    def test_selenium_ebay_verify_uploader(self):
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
        driver.get("http://bulksell.ebay.com/ws/eBayISAPI.dll?FileExchangeUploadForm&ssPageName=STRK:ME:LNLK")
        time.sleep(5)
        driver.find_element_by_name("uploadFile").send_keys(self.jsonFp)
        driver.find_element_by_id("Upload").click()
        time.sleep(5)
        page_data = driver.page_source
        print(page_data.encode('ascii','ignore'))
        ref_number = page_data.split('Your ref # is ')[-1][0:9]
        with open(verifyRequestNumberFp, 'a+') as f:
            f.write(','.join([time.asctime(),ref_number+'\n']))

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
