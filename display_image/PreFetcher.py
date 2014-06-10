import threading
import sky_manifest
from display_image.sky_scraper import FetchPage
import traceback
from display_image.Check import Check
from logs.logger_example import log_this
import sys

class PreFetcher(threading.Thread):

    def __init__(self, filenames, MainFrame):
        super(PreFetcher, self).__init__()
        self.MainFrame = MainFrame
        self.filenames = filenames
        #self.logger = log_this(__name__)
    #def infoLogger(self,msg=None):
        #this_function_name = sys._getframe().f_back.f_code.co_name
        #self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        #return
    #def debugLogger(self,msg=None,*args,**kwargs):
        #debug_info = {'ARGS':args, 'KWARGS':kwargs}
        #this_function_name = sys._getframe().f_back.f_code.co_name
        #self.logger.log_debug(this_function_name,str(msg)+this_function_name,debug_info)
        #return
    def run(self):
        import pdb;pdb.set_trace()
        for file_name in self.filenames:
            yield ('Opening: ' + file_name)
            results = sky_manifest.ManifestReader(file_name,self.MainFrame).getJnumbers()
            self.retailer_code = results[0]
            self.MainFrame.currentItemInfo['retailer_code'] = self.retailer_code
            self.jnumbers = results[1]
            self.total_count = len(self.jnumbers)
            self.current_count = 1
            if 'jnumber' in self.jnumbers:
                self.jnumbers.remove('jnumber')
            if '4number' in self.jnumbers:
                self.jnumbers.remove('4number')

            for jnumber in self.jnumbers:
                self.itemNumber = jnumber
                self.MainFrame.scanNumberTextValue = jnumber
                self.MainFrame.currentItemInfo['retailer_code'] = self.retailer_code
                self.data = FetchPage(self.MainFrame).results
                if self.itemNumber is "" or None:
                    continue

                if 'jnumber' not in jnumber:
                    self.data = FetchPage(self.MainFrame).results
                    self.infoLogger("self.data"+str(self.data))
                    try:
                        itemResults = Check(self.MainFrame)
                        images = itemResults.downloadImages()
                    except Exception:
                        print(traceback.format_exc())
                else:
                    print('Retailer Code Not Recognized:'+str(self.retailer_code))
                self.current_count += 1
                yield ('Pre-Fetching: Manifests: ' +
                        str(len(self.filenames)) +
                        ' Items in Current: '+str(self.current_count) +
                        '/' + str(self.total_count))
        yield('Completed PreFetching.')
