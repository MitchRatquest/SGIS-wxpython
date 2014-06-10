import wx
import json
import os
from logs.logger_example import log_this
import sys

class ListingPreferencesDialog(wx.Dialog):

    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title)
        self.panel = wx.ScrolledWindow(self, -1)
        #self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        fontsz = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPixelSize()
        self.panel.SetScrollRate(fontsz.x, fontsz.y)
        self.panel.EnableScrolling(True, True)
        self.prepareListingPreferences()
        title_and_row_index = ''

    def setMainFrame(self,MainFrame):
        self.MainFrame = MainFrame
        self.logger = log_this(__name__,self.MainFrame)
        return
    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return
    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+this_function_name,debug_info)
        return
    def prepareListingPreferences(self):
        '''
        Prepares title buttons for SelectCorrectWatchTitle
        # currentTitleList = [title, str, row_index]
        '''
        print('\n# SelectCorrectWatchTitle.prepareTitleButtons #')
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        #----------------------------------------------------
        # These need to be updated to match the        
        # ebayHeaders.csv 
        # also the check_list.... further down the code
        #----------------------------------------------------
        self.settings_dict = {'*Format':{'Auction':False,
                                        'FixedPrice':False},
                            '*Duration':{'3':False,
                                         '5':False,
                                         '7':False,
                                         '10':False,
                                         '30':False,
                                         'GTC':False},
                            '*StartPrice':{'.99':False, 'percent of MSRP':False},
                            'BuyItNowPrice':{'percent of MSRP':False},
                            'ReservePrice': {'percent of MSRP':False},
                            'ShippingService-1:Option':{'FedExHomeDelivery':False, 'USPSPriority':False},
                            'ShippingService-1:Cost':{'Amount':False},
                            }
        required_check_list = ['*Format', 'ShippingService-1:Option', '*Duration', '*StartPrice', 'ShippingService-1:Cost']
        self.ids = {}
        self.button_ids = {}
        self.instructionsTxt = wx.StaticText(self.panel, label='Bolded Titles are Required')
        self.font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
        self.instructionsTxt.SetFont(self.font)
        self.sizer.Add(self.instructionsTxt, 0, wx.ALIGN_CENTER)
        self.topSeperator = wx.StaticLine(self.panel, wx.ID_ANY, style=wx.LI_HORIZONTAL)
        self.sizer.Add(self.topSeperator, 0, wx.ALL | wx.EXPAND, 5)
        for key in self.settings_dict.keys():
            self.key_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.key = wx.StaticText(self.panel, label=key)
            # check for required items and bold static text
            if key in required_check_list:
                self.font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.BOLD)
                self.key.SetFont(self.font)
            self.sizer.Add(self.key)
            # create buttons for items
            for key2 in self.settings_dict[key]:
                self.value = wx.Button(self.panel, label=key2, name=key)
                try:
                    self.button_ids[key]
                except KeyError:
                    self.button_ids[key] = {}
                self.button_ids[key][key2+'_btn_id'] = self.value.GetId()
                self.value.Bind(wx.EVT_BUTTON, self.on_button)
                self.key_sizer.Add(self.value, 2, wx.ALL, 2)
                print(key2)
                check_list = ['*StartPrice','BuyItNowPrice','ReservePrice','ShippingService-1:Cost']
                if key in check_list:
                    self.text = wx.TextCtrl(self.panel, size=(60,-1), name='text_'+key+'_'+key2)
                    self.text.Bind(wx.EVT_TEXT, self.on_button)
                    self.key_sizer.Add(self.text, 2, wx.ALL, 2)
                    try:
                        self.ids[key]
                    except KeyError:
                        self.ids[key] = {}
                    self.ids[key][key2+'_id'] = self.text.GetId()
                    self.text.ChangeValue(str(self.settings_dict[key][key2]))
                    self.text.Disable()
            self.sizer.Add(self.key_sizer, 2, wx.ALL, 2)
        self.bottomSeperator = wx.StaticLine(self.panel, wx.ID_ANY, style=wx.LI_HORIZONTAL)
        self.sizer.Add(self.bottomSeperator, 0, wx.ALL | wx.EXPAND, 5)
        self.ok = wx.Button(self.panel, wx.ID_OK)
        self.sizer.Add(self.ok, 0, wx.ALIGN_RIGHT)
        self.ok.Disable()
        self.panel.SetSizer(self.sizer)
        print(self.settings_dict)
        self.sizer.Fit(self)
        self.panel.Layout()
        self.panel.Centre()
        self.panel.Show(True)

    def on_button(self, event):
        ''' Returns title when clicked'''


        key1 = event.GetEventObject().GetName()
        key2 = event.GetEventObject().GetLabel()

        if 'text' in key1:
            split_keys = key1.split('_')
            key1 = split_keys[1]
            key2 = split_keys[2]
            print(' '.join(['key1:',key1]))
            print(' '.join(['key2:',key2]))
            print(' '.join(['Value Updated:',self.FindWindowById(self.ids[key1][key2+'_id']).GetValue()]))
            self.settings_dict[key1][key2] = self.FindWindowById(self.ids[key1][key2+'_id']).GetValue()

        else:
            print('\n\n'+' '.join(['key1:',key1]))
            print(' '.join(['key2:',key2]))
            # Check if the row only has one item if so toggle
            if len(self.settings_dict[key1]) is 1:
                if self.settings_dict[key1][key2] is True:
                    print(self.ids[key1][key2+'_id'])
                    self.FindWindowById(self.ids[key1][key2+'_id']).Disable()
                    self.settings_dict[key1][key2] = False
                else:
                    self.FindWindowById(self.ids[key1][key2+'_id']).Clear()
                    self.FindWindowById(self.ids[key1][key2+'_id']).Enable()
                    self.settings_dict[key1][key2] = True
                    print(self.ids[key1][key2+'_id'])
            # check if multiple buttons if so toggle all to false and set one to true
            elif len(self.settings_dict[key1]) > 1:
                event.GetEventObject().Disable()
                # set all to False except key2
                for keys in self.settings_dict[key1]:
                    self.settings_dict[key1][keys] = False
                self.settings_dict[key1][key2] = True
                # Check if it has a text box if so GetValue()
                try:
                    self.FindWindowById(self.ids[key1][key2+'_id']).GetValue()
                except KeyError:
                    print('no text box')
                # if sub item is false disable textctrl and enable button
                for keys in self.settings_dict[key1]:
                    if self.settings_dict[key1][keys]is False:
                        # Check if it has a text box
                        try:
                            self.FindWindowById(self.ids[key1][keys+'_id']).Disable()
                        except KeyError:
                            print('no text box')
                        self.FindWindowById(self.button_ids[key1][keys+'_btn_id']).Enable()
                try:
                    text_id = self.ids[key1][key2+'_id']
                    self.FindWindowById(text_id).Clear()
                    self.FindWindowById(text_id).Enable()
                except KeyError:
                    print('no text box')

        # check if required check list has been completed if so enable ok button
        count_dict = {}
        required_check_list = ['*Format', 'ShippingService-1:Option', '*Duration', '*StartPrice', 'ShippingService-1:Cost']
        for key in self.settings_dict:
            count = 0
            for key2 in self.settings_dict[key]:
                if key in required_check_list:
                    if self.settings_dict[key][key2] is not False:
                        count +=1
                else:
                    continue
            if key in required_check_list:
                count_dict[key] = count
            else:
                continue
        print count_dict
        count = 0
        for key in count_dict:
            count += count_dict[key]
        if count == len(required_check_list):
            self.ok.Enable()
            with open('listing_preferences.json','wb') as f:
                json.dump(self.settings_dict, f)
        self.panel.Layout()
        self.panel.Centre()
        self.panel.Show(True)
        print(self.settings_dict)

class CheckListingPreferences(object):
    '''
    checks for listing_preferences.json and creates it if not exist
    '''
    def __init__(self, MainFrame):
        super(CheckListingPreferences, self).__init__()
        self.MainFrame = MainFrame
        self.logger = log_this(__name__,self.MainFrame)

    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return
    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+this_function_name,debug_info)
        return

    def check(self):
        '''
        Checks if listing_preferences.json exists
        '''
        if os.path.isfile('listing_preferences.json'):
            self.infoLogger('\n# ListingPreferencesDialog.CheckListingPreferences.check() #')
            with open('listing_preferences.json', 'r') as f:
                self.result = json.loads(f.read())
            self.infoLogger('######################## Listing Preferences #############\nType: '+str(type(self.result))+'\n'+str(self.result))
            return self.result
        else:
            return False

def main():

    app = wx.App(False)
    listingPreferences = CheckListingPreferences()
    listingPreferences = listingPreferences.check()
    if listingPreferences is False:
        results = ListingPreferencesDialog(None, -1,title='Listing Preferences')
        results.Show()
        if results.ShowModal() == wx.ID_OK:
            print(results.settings_dict)
            results.destroy()
        app.MainLoop()
    else:
        print listingPreferences
        exit()
if __name__ == '__main__':
    main()