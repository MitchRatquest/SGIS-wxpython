import os
import json
import traceback
import urllib2
import difflib
from logs.logger_example import log_this
import sys

class Check():
    def __init__(self, MainFrame):
        self.MainFrame = MainFrame
        self.logger = log_this(__name__,self.MainFrame)
        self.currentItemInfo = MainFrame.currentItemInfo
        self.setJPagesFolderPath()

    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return
    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+this_function_name,debug_info)
        return

    def guessImageName(self):
        jNumber = self.MainFrame.jNumber
        tmp_ratios = []

        img_list_len = len(self.MainFrame.currentItemInfo['image_list'])
        if img_list_len is 0:
            self.debugLogger("img_list_len is 0, this item has not been seen or no items were assigned",self.MainFrame.currentItemInfo)
            return Exception('ImageListEmpty: "image_list" is empty ',self.MainFrame.currentItemInfo)
        self.debugLogger("currentItemInfo:",self.MainFrame.currentItemInfo)
        for i in range(img_list_len):
           tmp = self.MainFrame.currentItemInfo['image_list'][i]
           ratio = difflib.SequenceMatcher(None,tmp.split('_')[0],self.MainFrame.jNumber).quick_ratio()
           tmp_ratios.append(ratio) 
        guess = self.MainFrame.currentItemInfo['image_list'][tmp_ratios.index(max(tmp_ratios))] # grab index by max tmp_ratio
        self.debugLogger("image name guess: ",guess)
        guess = guess.split('?')[0]+'.JPEG'
        return guess
    def defaultImageSelections(self):
        '''
        returns previously selected images
        '''
        self.infoLogger('\n# Check.defaultImageSelections(): #')
        prev_selected = self.currentItemInfo['itemSelectedImages']
        self.infoLogger('prev_selected:'+str(prev_selected))
        if isinstance(prev_selected, unicode):
            self.infoLogger('. Previous selected is type(): Unicode. Default image not selected on first scan?')
            prev_selected = unicode(prev_selected)
        try:
            for key in prev_selected.keys():
                # { 'image_name': bool}
                if "True" in prev_selected[key]:
                    self.infoLogger(key)
                    if key is not None or "":
                        self.infoLogger('# Check.defaultImageSelections: '+str(key))
                        return str(key)
                else:
                    self.infoLogger('. Check.defaultImageSelection() not found')
                    pass
            self.key = None
            if self.key is None or "":
                return None
        except AttributeError, e:
            self.infoLogger('. prev_selected does not have keys()')
            self.infoLogger('. prev_selected: '+ str(prev_selected))
            return None
    def loadMainFrameJson(self):
        '''
        Check if loadself.MainFrameJson exist if so load it, if not carry on and save it
        This is overwriting any changed info?
        '''
        self.infoLogger('\n# Check.loadself.MainFrameJson(): #')
        self.MainFrame.jsonFilePath = os.path.join(self.MainFrame.jNumberFolderPath,self.MainFrame.jNumber+'.json')
        self.infoLogger(self.MainFrame.jsonFilePath)
        #-------------------------------------------------------
        # Check if json exists
        #-------------------------------------------------------
        if os.path.isfile(self.MainFrame.jsonFilePath):
            try:
                with open(self.MainFrame.jsonFilePath,'rb') as f:
                    json_data = json.loads(f.read())
            except Exception, e:
                self.infoLogger(traceback.format_exc())
                self.debugLogger("Json jNumber not found",e,self.MainFrame.jsonFilePath)
                return Exception('Json jNumber not found')
            tmp_list = []
            for item in json_data:
                self.infoLogger('. ' + item)
                if 'itemSelectedImages' in json_data[item]:
                    self.itemSelectedImagesCheck = str(json_data[item]['itemSelectedImages'])
                    self.infoLogger('. ' + str(json_data[item]['itemSelectedImages']))
                    if self.itemSelectedImagesCheck is None or "":
                        self.infoLogger('. itemSelectedImages not set last json save')
                #tmp_list.update{item}
            self.infoLogger("Updating currentItemInfo"+
                                     " in loadMainFrameJson"+
                                     str(json_data))
            self.MainFrame.currentItemInfo.update(json_data)
            self.infoLogger('self.MainFrame.currentItemInfo Updated')
            return True
        #-------------------------------------------------------
        # if not exist
        #-------------------------------------------------------
        else:
            self.debugLogger("Json jNumber not found",self.MainFrame.jsonFilePath)
            self.MainFrame.statusbar.SetStatusText('. loadMainFrameJson jNumber.json does not exist: '+self.MainFrame.jsonFilePath)
            return False

    def jsonStateFileExists(self, jNumber, jNumberFolder):
        '''
        returns true if json StateFileExists
        '''
        folder = self.MainFrame.defaultJPagesFolder
        self.jNumberFolderPath = os.path.join(folder,jNumberFolder)
        self.jsonFilePath = os.path.join(self.MainFrame.jNumberFolderPath,jNumber+'.json')
        if os.path.isfile(self.jsonFilePath):
            return True
        else:
            return False

    def description(self):
        '''
         description see if anything is messing and which
        format it is in isinstance( str_name, unicode | str)
        '''
        #self.infoLogger(isinstance(self.currentItemInfo['description'], str))

        if (type(self.currentItemInfo['specs']) and type(self.currentItemInfo['description'])) is str:
            description = self.currentItemInfo['specs'] + self.currentItemInfo['description']
            return description

        if type(self.currentItemInfo['specs']) or type(self.currentItemInfo['description']) is None:
            tmp_str = ''
            try:
                description_str = str(self.currentItemInfo['description'].encode('utf8'))
                tmp_str = tmp_str.join(description_str)
            except Exception, e:
                self.infoLogger([str(e) +
                ": Location: Check: description: " +
                "self.currentItemInfo['description']:\nWTH "])
                pass
            try:
                tmp_str = ' '.join([tmp_str, str(self.currentItemInfo['specs'].encode('utf8'))])
            except Exception, e:
                self.infoLogger([str(e) +
                    ": Location: Check: description: self.currentItemInfo['specs']: "])
                pass
            description = tmp_str
        elif isinstance(self.currentItemInfo['description'], str):
            tmp_str = ''
            try:
                tmp_str = tmp_str.join(str(self.currentItemInfo['description'].decode('utf8')))
            except Exception, e:
                self.infoLogger(str(e)+": Location: Check: description: self.currentItemInfo['description'].decode(): ")
                pass
            try:
                tmp_str = ' '.join( [tmp_str, str(self.currentItemInfo['specs'].decode('utf8'))] )
            except Exception, e:
                self.infoLogger(str(e)+": Location: Check: description: self.currentItemInfo['specs']: ")
                pass
            description = tmp_str
        else:
            description = str(self.currentItemInfo['description']) #+ '\n' + str(self.currentItemInfo['specs'])

        return description

    def setJPagesFolderPath(self):
        if self.MainFrame.scanNumberTextValue is not None:
            if self.MainFrame.fingerRadio.GetValue() is True:
                self.MainFrame.jNumberFolderPath = os.path.join(self.MainFrame.defaultJPagesFolder, self.MainFrame.scanNumberTextValue[1:6])

            if self.MainFrame.shopHqRadio.GetValue() is True:
                self.MainFrame.scanNumberTextValue =  self.MainFrame.scanNumberTextValue.split('-')[0]
                self.MainFrame.jNumber = self.MainFrame.scanNumberTextValue
                self.MainFrame.jNumberFolderPath = os.path.join(self.MainFrame.defaultJPagesFolder, self.MainFrame.scanNumberTextValue)
        return


    def storeRadioSelection(self):
        '''
        Check which store radio button is selected update self.MainFrame.itemFolder
        '''

        self.MainFrame.scanNumberTextValue = self.MainFrame.scanNumberText.GetValue().upper()

        if self.MainFrame.fingerRadio.GetValue() is True:
            self.MainFrame.jNumberFolderPath = os.path.join(self.MainFrame.defaultJPagesFolder, self.MainFrame.scanNumberTextValue[1:6])

        if self.MainFrame.shopHqRadio.GetValue() is True:
            self.MainFrame.scanNumberTextValue =  self.MainFrame.scanNumberTextValue.split('-')[0]
            self.MainFrame.jNumber = self.MainFrame.scanNumberTextValue
            self.MainFrame.jNumberFolderPath = os.path.join(self.MainFrame.defaultJPagesFolder, self.MainFrame.scanNumberTextValue)
        return

    def downloadImages(self):
        '''
        Why is downloadImages in Check and not
        in fetch page?
        
        Well anyways this downloads image_list
        '''
        def mkdir(fp):
            try:
                os.mkdir(fp)
                return
            except Exception,e:
                return
        self.infoLogger("###Downloading Images####\n")
        self.debugLogger("WHAT IS IN THE itemInfo IMAGE LIST",self.currentItemInfo['image_list'])
        self.debugLogger("WHAT IS IN THE currentItemInfo IMAGE LIST",self.MainFrame.currentItemInfo['image_list'])
        for img_name in self.currentItemInfo['image_list']:
            #------------------------------------
            # download FH images
            #------------------------------------
            if 'DefaultImage' not in img_name:
                try:
                    uts_number = self.MainFrame.scanNumberTextValue[1:6]
                    self.MainFrame.jNumber = uts_number
                    self.debugLogger('downloadImages: uts_number: ',uts_number)
                    self.debugLogger("img_name: ",img_name)
                    url_ = img_name + '?'
                    self.debugLogger('downloadImages(): self.MainFrame.itemFolder: ', self.MainFrame.jNumberFolderPath)
                    mkdir(self.MainFrame.jNumberFolderPath)
                    imgName = img_name+'.JPEG'
                    img_fp = os.path.join(self.MainFrame.jNumberFolderPath, imgName)
                    self.infoLogger(img_fp)
                    self.MainFrame.statusbar.SetStatusText('Checking for:'+img_fp)
                    if os.path.isfile(img_fp) is False:
                        self.MainFrame.statusbar.SetStatusText('Downloading:'+img_fp)
                        # build the url
                        image_url = "http://s7d5.scene7.com/is/image/bluestembrands/"+url_
                        self.debugLogger(". Check.downloadImages(): Fetching Image: " + image_url)
                        # build request header
                        user_agent = 'jmunsch_v3.5 (+http://jamesmunsch.com/)'
                        headers = { 'User-Agent' : user_agent }
                        imgRequest = urllib2.Request(image_url, headers=headers)
                        # get the image data
                        imgData = urllib2.urlopen(imgRequest).read()
                        #write teh image data
                        # uh... windows requires wb ...
                        with open(img_fp, 'wb') as imgFile:
                            imgFile.write(imgData)
                            self.infoLogger('. Check.downloadImages(): Wrote Image:' + str(img_fp))

                # except problem i.e. wrong filepath / 403 / incorrect request
                except Exception, e:
                    self.infoLogger("display_image: Check: downloadImages: Oops1: "+str(e))
                    self.MainFrame.statusbar.SetStatusText('ERROR:'+img_fp+' '+str(e))
                    self.infoLogger(traceback.format_exc())
                    pass
             #------------------------------------
             # Download Shophq photos
             #------------------------------------
            else: 
                try:
                    url_ = img_name
                    imgName = img_name.split('?')[0]+'.JPEG'
                    folder = self.MainFrame.defaultJPagesFolder
                    self.MainFrame.jNumberFolderPath = os.path.join(folder, self.MainFrame.jNumber)
                    mkdir(self.MainFrame.jNumberFolderPath)
                    img_fp = os.path.join(self.MainFrame.jNumberFolderPath, imgName)
                    self.MainFrame.statusbar.SetStatusText('Checking for:'+img_fp)
                    if os.path.isfile(img_fp) is False:
                        self.MainFrame.statusbar.SetStatusText('Downloading:'+img_fp)
                        # build the url
                        image_url = "http://images.shophq.com/is/image/ShopHQ/"+url_
                        self.infoLogger(". Check.downloadImages(): Fetching Image: " + image_url)
                        # build request header
                        user_agent = 'jmunsch_v3.5 (+http://jamesmunsch.com/)'
                        headers = { 'User-Agent' : user_agent }
                        imgRequest = urllib2.Request(image_url, headers=headers)
                        # get the image data
                        imgData = urllib2.urlopen(imgRequest).read()
                        #write teh image data
                        # uh... windows requires wb ...
                        with open(img_fp, 'wb') as imgFile:
                            imgFile.write(imgData)
                # except problem i.e. wrong filepath / 403 / incorrect request
                except Exception, e:
                    self.infoLogger("# [except]:display_image: Check: downloadImages: Oops2: "+str(e))
                    self.MainFrame.statusbar.SetStatusText('ERROR:'+img_fp+' '+str(e))
                    self.infoLogger(traceback.format_exc())
                    pass
        return
