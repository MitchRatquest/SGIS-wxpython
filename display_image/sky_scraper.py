# James Munsch
# http://jamesmunsch.com/
# james.a.munsch@gmail.com
# -*- coding: utf8 -*-
import csv, time, os, random, difflib, re, json
from itertools import islice
import httplib
import urllib2
from bs4 import BeautifulSoup as BS
from shutil import copyfile
import traceback
from logs.logger_example import log_this
import sys


class FetchPage(object):
    '''
    FetchPage(MainFrame).results updates with dictionary information
    given FetchPage(MainFrame).fetchpage(retailer_code,scanNumber)
    '''
    def __init__(self, MainFrame):
        super(FetchPage, self).__init__()
        self.MainFrame = MainFrame
        self.logger = log_this(__name__,self.MainFrame)
        self.retailer_code = self.MainFrame.currentItemInfo['retailer_code']
        self.results = self.fetchPage(self.retailer_code,self.MainFrame.scanNumberTextValue)



    def infoLogger(self,msg=None):
        try:
            this_function_name = sys._getframe().f_back.f_code.co_name
            self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
            return
        except Exception, e:
            print(e)
            print(traceback.format_exc())
            exit()

    def debugLogger(self,msg=None,*args,**kwargs):
        try:
            debug_info = {'ARGS':args, 'KWARGS':kwargs}
            this_function_name = sys._getframe().f_back.f_code.co_name
            self.logger.log_debug(this_function_name,str(msg)+this_function_name,debug_info)
            return
        except Exception, e:
            print(e)
            print(traceback.format_exc())
            exit()

    def fetchPage(self,retailer_code,scanNumber):
        self.debugLogger("retailer_code,jNumber",retailer_code,scanNumber)
        if '0' in retailer_code:
            self.infoLogger("starting getFingertHutProductInfo")
            jNumber = scanNumber[1:6].upper()
            results = self.getFingerHutProductInfo(jNumber)
            self.infoLogger('Updating currentItemInfo in FetchPage')
            self.MainFrame.currentItemInfo.update(results)
            results = self.MainFrame.currentItemInfo
            self.debugLogger('getFinderHutProductInfo(jNumber) fetchPage results:',results,jNumber,scanNumber)
            return results
        if '1' in retailer_code:
            jNumber = scanNumber.split('-')[0].upper()
            self.infoLogger("starting getShopHqProductInfo")
            results = self.getShopHqProductInfo(jNumber)
            self.infoLogger('Updating currentItemInfo in FetchPage')
            self.MainFrame.currentItemInfo.update(results)
            results = self.MainFrame.currentItemInfo
            self.debugLogger('getShopHqProductInfo(jNumber) fetchPage results:',results, jNumber,scanNumber)
            return results

    def getFingerHutProductInfo(self,jNumber):
        ''' Returns a dictionary of item information '''

        # offer_id_orig = '#NK420#########'
        offer_id_orig = jNumber
        itemUtsNumber = offer_id_orig
        self.infoLogger(offer_id_orig)
        self.debugLogger('itemJnumber',jNumber)
        # DOWNLOAD PRODUCT INFO IF WE DON"T HAVE IT
        def download_page_info(itemUtsNumber):
            '''
            urllib2 does not support javascript/AJAX implemented
            javascript_support.selenium_browser_save_page(url,fp) just in case?
            '''
            httplib.HTTPConnection.debuglevel = 1
            self.infoLogger("get: download_page_info(): Fetching:" + html_file_path)
            try:
                request = urllib2.Request('http://www.fingerhut.com/product/' + itemUtsNumber.upper() + '.uts')
                request.add_header('User-Agent','jmunsch_thnx_v2.0 +http://jamesmunsch.com/')
                opener = urllib2.build_opener()
                data = opener.open(request).read()
                with open(html_file_path, 'w+') as f:
                    f.write(data)
                time.sleep(1 + random.random())
                self.infoLogger("Fetched.")
            except Exception, e:
                self.infoLogger("#~#get_product_info: download_page_info: Problem fetching.")
                self.infoLogger(traceback.format_exc())
                data = None
                self.infoLogger(e)
            return data

        def extract_product_info(data):
            ''' Extract product info from the data from download_page_info '''
            #from bs4 import BeautifulSoup as BS
            #id="productTabs_tab1"
            #id="productTabs_tab3"
            # Grab Description

            json_data = data.split("page.init(")[1].split("});")[0]
            json_data = json_data + "}"

            try:

                self.infoLogger("Trying to load json")
                json_data_desc = json.loads(json_data.replace('\\uXXXX', ''))
                description = json_data_desc['product']['description']
                d_soup = BS(description)
                # Remove tags with information that can lead back to FH
                for tag in d_soup.find_all('h3'):
                    tag.replaceWith('')
                for tag in d_soup.find_all('script'):
                    tag.replaceWith('')
                for tag in d_soup.find_all('a'):
                    tag.replaceWith('')
                for tag in d_soup.find_all('li'):
                    if "Available" in tag.text:
                        tag.replaceWith('')
                description = d_soup
            except Exception, e:
                self.infoLogger(e)
                self.infoLogger(['#~#get_product_info: extract_product_info:' +
                        ' unable to get description'])
                #self.infoLogger(description)
                #self.infoLogger(json_data)
                description = None
            # Grab Specifications
            try:
                self.infoLogger("Trying to load json")
                json_data_specs = json.loads(json_data)
                specifications = json_data_specs['product']['specifications']
                specs = "<br>".join(x for x in specifications)
            except Exception, e:
                self.infoLogger(e)
                self.infoLogger(['#~#get_product_info: extract_product_info:' +
                        ' unable to get specs'])
                specs = None

            # Grab Images
            image_list = []
            try:

                self.infoLogger("Trying to load json")
                json_data_imgs = json.loads(json_data)
                images = json_data_imgs['product']['media']['image']
                print(images)
                if len(images) is not 0:
                    for url in images:
                        tmp_str = url['hiRes'].encode('utf8').split('?')[0].split('/')[-1]
                        #self.infoLogger(tmp_str)
                        image_list.append(tmp_str)
                if len(images) is 0:
                    self.infoLogger(" images is empty ")
                    split_data = data.split('\"')
                    for line in split_data:
                        if (offer_id_orig[1:6] and "is/bluestembrands") in line:
                            image_list.append(line.split('/')[-1].split('?')[0])
                if len(image_list) is 0:
                    raise NameError('imgList0')
            except NameError, n:
                self.infoLogger("\n###" + str(n))
                if 'imgList0' in n:
                    self.infoLogger(['##~#get_product_info: extract_product_info: imgList0:' +
                    'Didnt find any images...? Good luck.'])
                    image_list = [offer_id_orig]
                    pass
            except Exception, e:
                self.infoLogger(e)
                #self.infoLogger(json_data)
                self.infoLogger(["##~#get_product_info: extract_product_info:" +
                        " Unable to get image_list: Empty?"])
                image_list = None
            image_list = list(set(image_list))
            if len(image_list) is not 0:
                self.infoLogger("Got Images.")
            print(image_list)
            results = {'description': description,
                        'specs': specs,
                        'image_list': image_list
                        }
            return results

        # Check if item page has been downloaded
        # Get page data
        # Make item folder
        folder = self.MainFrame.defaultJPagesFolder
        itemFolder = os.path.join(folder, itemUtsNumber)
        html_file_path = os.path.join(itemFolder, itemUtsNumber + "_html")
        self.infoLogger('folder:' + folder)
        self.infoLogger('itemFolder:' + itemFolder)
        self.infoLogger('html_file_path:' + html_file_path)

        try:
            os.mkdir(folder)
        except Exception, e:
            self.infoLogger(e)
            pass
        try:
            os.mkdir(itemFolder)
        except Exception, e:
            self.infoLogger(e)
            pass

        # Check if the file exists if not download it
        if os.path.isfile(html_file_path):
            with open(html_file_path, 'r') as f:
                data = f.read()
        else:
            data = download_page_info(itemUtsNumber)

        # extract product info returns
        # 'description','specs','image_list'
        #
        ########################################

        results = extract_product_info(data)
        self.infoLogger(results)
        return results

    def getShopHqProductInfo(self,jNumber):
        ''' Returns a dictionary of item information '''

        itemJNumber = jNumber

        # DOWNLOAD PRODUCT INFO IF WE DON"T HAVE IT
        def download_page_info(itemJNumber):
            '''
            urllib2 does not support javascript/AJAX implemented
            javascript_support.selenium_browser_save_page(url,fp) just in case?
            '''

            httplib.HTTPConnection.debuglevel = 1
            self.debugLogger('itemJnumber',itemJNumber)
            try:
                url = 'http://www.shophq.com/product/?&familyid=' + itemJNumber
                self.infoLogger("get: download_page_info(): Fetching:" + html_file_path + ' ' )
                request = urllib2.Request(url)


                request.add_header('User-Agent',
                    'jmunsch_thnx_v2.0 +http://jamesmunsch.com/')
                opener = urllib2.build_opener()
                data = opener.open(request).read()
                with open(html_file_path, 'w+') as f:
                    f.write(data)
                time.sleep(1 + random.random())
                self.infoLogger("Fetched.")
            except Exception, e:
                self.infoLogger("#~#get_product_info: download_page_info: Problem fetching.")
                self.infoLogger(e)
                data = None
            if data is None:
                return Exception('Data is None')
            return data


        def extract_product_info(data):
            ''' Extract product info from the data from download_page_info '''
            #from bs4 import BeautifulSoup as BS
            # Given data extract watch description and specs
            # return results

            tmp_watch_data = data.split('mboxCreate(')[-1].split("'entity.inventory")
            tmp_price_title_info = tmp_watch_data[0]
            tmp_price_title_info = tmp_price_title_info.split(',')
            price_title_info = []
            for item in tmp_price_title_info:
                price_title_info.append(item.lstrip('\r\n \'').replace("'","").replace("\"",""))

            tmp_watch_data = data.split('<div class=\"panelDetail\" id=\"prod_description\">')[-1].split('<li><strong>Warranty:')[0].split('<p><strong>Additional Features:')[0].split('<!--googleoff: all-->')[0].split('<li><strong>Additional Information:')[0].split('</table>')[-1]
            watch_description = tmp_watch_data

            specs = str(price_title_info)
            description = str(watch_description)
            self.infoLogger(description)
            #--------------------------------------------
            # create image_list
            #---------------------------------------------
            image_list = []
            for img_str in data.split('/is/image/ShopHQ/'):
                if ('swatch' not in img_str) or ( '80x80' not in img_str):            
                    if 'DefaultImage' in img_str:
                        image_list.append(img_str.split("\"")[0].rstrip("\r\n ',"))

            results = {'description': description,
                        'specs': specs,
                        'image_list': image_list
                        }
                        
            
            if len(results['image_list']) is 0:
                return Exception('ImageListEmpty: "image_list" is empty',results)

            return results

        # Check if item page has been downloaded
        # Get page data
        # Make item folder
        folder = self.MainFrame.defaultJPagesFolder
        itemFolder = os.path.join(folder, itemJNumber)
        html_file_path = os.path.join(itemFolder, itemJNumber + "_html")
        self.infoLogger('folder:' + folder)
        self.infoLogger('itemFolder:' + itemFolder)
        self.infoLogger('html_file_path:' + html_file_path)

        try:
            os.mkdir(folder)
        except Exception, e:
            self.infoLogger(e)
            pass
        try:
            os.mkdir(itemFolder)
        except Exception, e:
            self.infoLogger(e)
            pass

        # Check if the file exists if not download it
        if os.path.isfile(html_file_path):
            with open(html_file_path, 'r') as f:
                data = f.read()
        else:
            data = download_page_info(itemJNumber)

        # extract product info returns
        # 'description','specs','image_list'
        #
        ########################################

        results = extract_product_info(data)
        #---------------------
        # remove smaller photos
        #-----------------------

        
        self.infoLogger(results)
        return results
