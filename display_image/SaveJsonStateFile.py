import os
import json
from logs.logger_example import log_this
import sys

class Save(object):
    '''
    Save a MainFrame.currentItemInfo()
    '''
    def __init__(self, MainFrame):
        super(Save, self).__init__()
        self.MainFrame = MainFrame
        self.MainFrameDict = MainFrame.__dict__
        self.logger = log_this(__name__,self.MainFrame)
        self.writeJson()

    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return

    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+" "+this_function_name,debug_info)
        return

    def writeJson(self):
        self.infoLogger('\n# Save.writeJson(): #')
        self.json_state_file = str(os.path.join(self.MainFrameDict['jNumberFolderPath'],self.MainFrameDict['jNumber']+'.json'))
        if 'itemSelectedImages' not in self.MainFrameDict['currentItemInfo']:
            self.infoLogger('. itemSelectedImages was not set: Setting now.')
            #import pdb;pdb.set_trace()
            self.MainFrameDict['currentItemInfo']['itemSelectedImages'] = self.MainFrameDict['currentImgPath']
        try:
            self.MainFrameDict['currentItemInfo']['description'] = self.MainFrameDict['currentItemInfo']['description'].decode('utf8')
        except UnicodeEncodeError:
            self.infoLogger('. Caught UnicodeEncodeError: Save.writeJson: Not Modifying MainFrameDict[\'currentItemInfo\'][\'description\']')
        try:
            self.MainFrameDict['currentItemInfo']['specs'] = str(self.MainFrameDict['currentItemInfo']['specs'])
        except UnicodeEncodeError:
            self.infoLogger('. Caught UnicodeEncodeError: Save.writeJson: Not Modifying MainFrameDict[\'currentItemInfo\'][\'specs\']')


        # include itemSelectedImages
        #self.MainFrameDict['currentItemInfo']['itemSelectedImages'] = MainFrame.itemSelectedImages

        for item in self.MainFrameDict['currentItemInfo']:

            if isinstance(self.MainFrameDict['currentItemInfo'][item], str):
                self.infoLogger('. ###\n. ' + item + '\n. ###\n. str:' + self.MainFrameDict['currentItemInfo'][item])
            elif isinstance(self.MainFrameDict['currentItemInfo'][item], unicode):
                self.infoLogger('. ###\n. ' + item + '\n. ###\n. Unicode:' + self.MainFrameDict['currentItemInfo'][item].encode("ascii", 'ignore'))
            elif isinstance(self.MainFrameDict['currentItemInfo'][item], dict):
                self.infoLogger('. ###\n. ' + item + '\n###\n. Dict:' + unicode(self.MainFrameDict['currentItemInfo'][item]))
            elif isinstance(self.MainFrameDict['currentItemInfo'][item], list):
                self.infoLogger('. ###\n. ' + item + '\n###\n. List:' + unicode(self.MainFrameDict['currentItemInfo'][item]))
            else:
                self.infoLogger(type(self.MainFrameDict['currentItemInfo'][item]))
                exit()
        self.MainFrameDict['currentItemInfo']['description'] = self.MainFrameDict['currentItemInfo']['description'].replace('\"','').replace(',','')
        self.infoLogger('save:'+str(self.MainFrameDict['currentItemInfo']))
        with open(self.json_state_file,'wb') as f:
            json.dump(self.MainFrameDict['currentItemInfo'], f)
        self.MainFrame.statusbar.SetStatusText('Wrote json_state_file')



    def printJsonStateFile(self):
        self.infoLogger('\n# Save.printJsonStateFile(): #')
        with open(self.json_state_file,'rb') as f:
            json_data = json.loads(f.read())

        #self.infoLogger(unicode(json_data['description'])+'\n')
