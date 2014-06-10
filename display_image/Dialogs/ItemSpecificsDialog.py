import wx

class ItemSpecificsDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title)
        self.panel = wx.ScrolledWindow(self, -1)
        #self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        fontsz = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPixelSize()
        self.panel.SetScrollRate(fontsz.x, fontsz.y)
        self.panel.EnableScrolling(True, True)
        self.currentItemSpecificsDict = {}
        self.prepareItemSpecificsFields()



    def prepareItemSpecificsFields(self):
        '''
        Prepares title buttons for SelectCorrectWatchTitle
        # currentTitleList = [title, str, row_index]
        '''
        print('\n# SelectCorrectWatchTitle.prepareTitleButtons #')
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # return row by sku
        line = MainFrame.csvTextReader.returnRowBySku(MainFrame.currentSkuText.GetValue())
        # get title_column index and find the title from the item row list line[1]
        title = line[1][line[0].index('title')]
        self.title = wx.StaticText(self.panel, label=title)
        self.sizer.Add(self.title)
        # MainFrame.itemSpecifics = [item_category, [specific, specific]]
        for item_specific in MainFrame.itemSpecifics[1]:
            # currentTitleList = [title, str, row_index]
            item_specific = 'C:'+item_specific

            self.label_text = str(item_specific)
            self.label_name = wx.StaticText(self.panel, label=self.label_text)
            if 'Brand' in self.label_text:
                text_len = 120
            else:
                text_len = 60
            self.itemSpecificText = wx.TextCtrl(self.panel, size=(text_len,-1), name=item_specific)
            self.itemSpecificText.Bind(wx.EVT_TEXT, self.on_text)
            self.sizer.Add(self.label_name, 0, wx.ALIGN_CENTER)
            self.sizer.Add(self.itemSpecificText, 0, wx.ALIGN_CENTER)
            if 'Style' in item_specific:
                self.itemSpecificText.SetValue('Casual')
                #wx.PostEvent(self.itemSpecificText, wx.CommandEvent(wx.EVT_TEXT))
            elif 'Size Type' in item_specific:
                self.itemSpecificText.SetValue('Regular')
                #wx.PostEvent(self.itemSpecificText, wx.CommandEvent(wx.EVT_TEXT))
            elif 'Brand' in item_specific:
                # requires that | comes after the brand in each item
                if "|" in title:
                    self.itemSpecificText.SetValue(title.split('|')[0])
                    #wx.PostEvent(self.itemSpecificText, wx.CommandEvent(wx.EVT_TEXT))
        self.ok = wx.Button(self.panel, wx.ID_OK)
        self.sizer.Add(self.ok, 0, wx.ALIGN_RIGHT)
        self.panel.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.panel.Layout()
        self.panel.Centre()
        self.panel.Show(True)

    def on_text(self, event):
        ''' updates self.currentItemSpecificsDict'''
        print(event.GetEventType())
        item_specific = event.GetEventObject().GetName()
        item_specific_value = event.GetEventObject().GetValue()
        self.currentItemSpecificsDict.update({item_specific: item_specific_value})
        #self.title_and_row_inde = event.GetEventObject().GetValue()
