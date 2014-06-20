import wx
import traceback
from display_image.Check import Check
import os
from logs.logger_example import log_this
import sys
from display_image.sky_scraper import FetchPage
from multiprocessing import Process
from display_image.SaveJsonStateFile import Save
from display_image.Dialogs.ReturnCorrectTitleDialog import ReturnCorrectTitleDialog
from display_image.Dialogs.ImageSelectionFrame import ImageSelectionFrame
from display_image.build_auction import BuildAuction
from display_image.PreFetcher import PreFetcher
from display_image.Dialogs.ListingPreferencesDialog import ListingPreferencesDialog
import time

class MainFrameEventHandler(object):
    '''
    Use these to seperate controls and logic?
    '''
    def __init__(self,MainFrame):
        super(MainFrameEventHandler, self).__init__()
        self.MainFrame = MainFrame
        self.logger = log_this(__name__,self.MainFrame)
        self.checkIfManifestedResults = None
    def infoLogger(self,msg=None):
        try:
            this_function_name = sys._getframe().f_back.f_code.co_name
            self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
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
            self.logger.log_debug(this_function_name,str(msg)+" "+this_function_name,debug_info)
            return
        except Exception, e:
            print(e)
            print(traceback.format_exc())
            exit()
    def onPdbSetTrace(self, event):
        '''
        Help Menu pdb set trace for variable debugging
        '''
        self.infoLogger("Inside: ")
        import pdb;pdb.set_trace()
        return
    def csvFileBrowse(self):
        '''
        Creates file dialog to select CSV files
        '''
        self.debugLogger("Inside: ")
        self.infoLogger("Inside: ")
        self.MainFrame.statusbar.SetStatusText('Browsing for UTF8 comma delimited CSV file.')
        wildcard = "CSV files (*.csv)|*.csv"
        dialog = wx.FileDialog(None, "Choose a file",
                               wildcard=wildcard,
                               style=wx.OPEN | wx.FD_MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            filenames = dialog.GetPaths()
        dialog.Destroy()
        try:
            self.debugLogger("Filenames:",filenames)
        except Exception,e:
            self.debugLogger(e)
        return filenames
    def onCurrentTitleText(self, event):
        '''
        Displays current title, and saves dict on change
        '''
        self.infoLogger("Inside: ")
        self.MainFrame.currentItemInfo['title'] = self.MainFrame.currentTitleText.GetValue().rstrip(' ')
        
        return
    def onListerInitialsText(self, event):
        '''
        onListerInitialsText not complete does nothing
        '''
        status = 'Initials set:' + self.MainFrame.listerInitialsText.GetValue()
        self.MainFrame.statusbar.SetStatusText(status)
        self.MainFrame.currentItemInfo['listerInitials'] = self.MainFrame.listerInitialsText.GetValue()
        self.infoLogger(status)
        return
    def onPrefetch(self, event):
        '''
        Start Prefetch thread
        '''
        self.infoLogger("Inside: ")
        filenames = self.csvFileBrowse()
        self.MainFrame.threading = True
        prefetcher = PreFetcher(filenames,self.MainFrame)
        for status in prefetcher.run():
            wx.Yield()
            self.MainFrame.statusbar.SetStatusText(status)
        self.MainFrame.threading = False
        return
    def onListingPreferencesMenu(self, event):
        '''
        Starts ListingPreferencesDialog
        '''
        self.infoLogger("Inside: ")
        results = ListingPreferencesDialog(None, -1,title='Listing Preferences')
        if results.ShowModal() == wx.ID_OK:
            self.MainFrame.settingsDict = results.settings_dict
            results.Destroy()
        try:
            print(self.MainFrame.settingsDict)
        except Exception, e:
            print(e)
            self.infoLogger('Dialog closed without pressing OK? or something else'+str(e))
        return
    def onClose(self, event):
        '''
        onClose self.MainFrame.Close()
        '''
        self.infoLogger("Inside: ")
        tmp_dialog = wx.MessageDialog(self.MainFrame, 'Close the program?\n\n Press *Yes*', 'QUITTER', wx.YES | wx.NO)
        results = tmp_dialog.ShowModal()
        if results == wx.ID_YES:
            tmp_dialog.Destroy()
            self.MainFrame.Close()
            exit()
        return
    def onLoadManifest(self, event):
        '''
        onLoadManifest() Loads manifest into seperate window to begin manifesting?
        '''
        self.infoLogger("Inside: ")
        # sky_manifest.ManifestReader(filename)
        return
    def onUpcNumberText(self, event):
        '''
        Updates self.MainFrame.currentItemInfo['upc']
        '''
        self.infoLogger("Inside: ")
        self.MainFrame.currentItemInfo['upc'] = self.MainFrame.upcNumberText.GetValue()
        self.infoLogger("upc entered, and updated."+str(self.MainFrame.currentItemInfo['upc']))
        # upc_len = len(self.MainFrame.currentItemInfo['upc'])
        # if upc_len is not 0:
            # self.infoLogger("Entering Save(self.MainFrame)")
            # Save(self.MainFrame)
            # self.infoLogger('Called Save(self.MainFrame')
        # else:
            # self.infoLogger('Not Saving'+str(upc_len))
        return
    def onCurrentConditionText(self, event):
        '''
        Updates self.MainFrame.currentItemInfo['*ConditionID']
        '''
        self.infoLogger("Inside: ")
        value = self.MainFrame.currentConditionText.GetValue()
        if '5' in value:
            self.MainFrame.currentItemInfo['*ConditionID'] = '1000'
        if '4' in value:
            self.MainFrame.currentItemInfo['*ConditionID'] = '1500'
        if '3' in value:
            self.MainFrame.currentItemInfo['*ConditionID'] = '1750'
        if '2' in value:
            self.MainFrame.currentItemInfo['*ConditionID'] = '3000'
        if 'New' in value:
            self.MainFrame.currentItemInfo['*ConditionID'] = '1000'
        self.infoLogger('Calling Save(self.MainFrame)')
        # Save(self.MainFrame)
        return
    def onLookUpBySkuBtnShopHq(self):
        '''
        update rSizer with mainFrame.itemRow
        update MainFrame Image
        updates currentItemInfo
        # depending on which retailer, different columns are needed
        '''
        self.infoLogger("Inside: ")
        self.infoLogger(self.MainFrame.itemRow)
        try:
            for key in self.MainFrame.itemRow[0]: # itemRow = [[column_indexes],[itemRow]]
                index = self.MainFrame.itemRow[0].index(key)
                self.MainFrame.currentItemInfo.update({key:self.MainFrame.itemRow[1][index]})        
            jnumber_column_index = self.MainFrame.itemRow[0].index('jnumber')
            jnumber = self.MainFrame.itemRow[1][jnumber_column_index]
            box_column_index = self.MainFrame.itemRow[0].index('box')
            pallet_number_index  = self.MainFrame.itemRow[0].index('pallet_number')
            pallet_number = self.MainFrame.itemRow[1][pallet_number_index]
            box = self.MainFrame.itemRow[1][box_column_index]
            condition_column_index = self.MainFrame.itemRow[0].index('condition')
            condition = self.MainFrame.itemRow[1][condition_column_index]
            condition_notes_column_index = self.MainFrame.itemRow[0].index('condition_notes')
            condition_notes = self.MainFrame.itemRow[1][condition_notes_column_index]
            date_listed_column_index = self.MainFrame.itemRow[0].index('date_listed')
            date_listed = self.MainFrame.itemRow[1][date_listed_column_index]
            manifested_column_index = self.MainFrame.itemRow[0].index('manifested')
            manifested = self.MainFrame.itemRow[1][manifested_column_index]
            title_index = self.MainFrame.itemRow[0].index('title')
            title = self.MainFrame.itemRow[1][title_index]
            title = title.lower().title()
        except ValueError,e:
            self.infoLogger("A dialog giving a reason why we can't continue should appear.")
            tmp_dialog = wx.MessageDialog(self.MainFrame, str(str(e)+'\n\nCheck the HEADERS within the CSV file.\n\n Is this value there?\n\n *Hint*: It is Case Sensitive.'), 'ValueError', wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        self.MainFrame.currentItemInfo['jNumber'] = self.MainFrame.itemRow[1][jnumber_column_index]
        self.MainFrame.jNumber = jnumber
        # --------------------------------
        # updates MainFrame Image, checks Json
        # maybe should be just a call to imageUpdate?
        # --------------------------------
        # sets scanNumberText and looks up json_state_file ... also resets currentItemInfo
        self.MainFrame.currentItemInfo['jNumber'] = self.MainFrame.itemRow[1][jnumber_column_index]
        self.MainFrame.jNumber = jnumber
        self.MainFrame.scanNumberText.Clear()
        self.MainFrame.scanNumberText.AppendText(jnumber)
        self.MainFrame.palletNumberText.SetValue(pallet_number)
        self.onScanNumberText(self)
        # update MainFrame.currentItemInfo with itemRow information ... msrp, type, etc
        for key in self.MainFrame.itemRow[0]: # itemRow = [[column_indexes],[itemRow]]
            index = self.MainFrame.itemRow[0].index(key)
            self.MainFrame.currentItemInfo.update({key:self.MainFrame.itemRow[1][index]})
        self.MainFrame.currentItemInfo['jNumber'] = self.MainFrame.jNumber # :( why are so many variables mixed naming GRRRRRRRRR
        self.infoLogger('Added MainFrame.itemRow to currentItemInfo'+str(self.MainFrame.itemRow))
        # set values
        #self.MainFrame.currentBoxText.SetValue(box)
        self.MainFrame.currentConditionText.SetValue(condition)
        self.MainFrame.currentConditionNotesText.Clear()
        self.MainFrame.palletNumberText.SetValue(pallet_number)
        self.MainFrame.currentConditionNotesText.AppendText(condition_notes)
        self.MainFrame.currentDateListedText.SetValue(date_listed)
        self.MainFrame.rSizer.Show(self.MainFrame.rSizerCurrentItemSizer)
        self.MainFrame.currentTitleText.Clear()
        self.MainFrame.currentTitleText.AppendText(title)
        self.MainFrame.ebayCategoryIdText.SetValue('31387')
        self.MainFrame.mainSizer.Fit(self.MainFrame)
        self.MainFrame.mainPanel.Layout()
        self.MainFrame.mainPanel.Refresh()
        return
        
    def onLookUpBySkuBtnFinger(self):
        '''
        update rSizer with Finger info
        # self.MainFrame.itemRow set in onLookUpBySkuBtn
        # depending on which retailer, different columns are needed
        '''
        self.infoLogger("Inside: ")
        try:    # test tat all the headers are there
            for key in self.MainFrame.itemRow[0]: # itemRow = [[column_indexes],[itemRow]]
                index = self.MainFrame.itemRow[0].index(key)
                self.MainFrame.currentItemInfo.update({key:self.MainFrame.itemRow[1][index]})
            jnumber_column_index = self.MainFrame.itemRow[0].index('jnumber')
            jnumber = self.MainFrame.itemRow[1][jnumber_column_index]
            pallet_number_index  = self.MainFrame.itemRow[0].index('pallet_number')
            pallet_number = self.MainFrame.itemRow[1][pallet_number_index]
            condition_column_index = self.MainFrame.itemRow[0].index('condition')
            condition = self.MainFrame.itemRow[1][condition_column_index]
            condition_notes_column_index = self.MainFrame.itemRow[0].index('condition_notes')
            condition_notes = self.MainFrame.itemRow[1][condition_notes_column_index]
            date_listed_column_index = self.MainFrame.itemRow[0].index('date_listed')
            date_listed = self.MainFrame.itemRow[1][date_listed_column_index]
            manifested_column_index = self.MainFrame.itemRow[0].index('manifested')
            manifested = self.MainFrame.itemRow[1][manifested_column_index]
            title_index = self.MainFrame.itemRow[0].index('title')
            title = self.MainFrame.itemRow[1][title_index]
        except ValueError,e:
            self.infoLogger("A dialog giving a reason why we can't continue should appear.")
            tmp_dialog = wx.MessageDialog(self.MainFrame, str(str(e)+'\n\nCheck the HEADERS within the CSV file.\n\n Is this value there?\n\n *Hint*: It is Case Sensitive.'), 'ValueError', wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        # --------------------------------
        # updates MainFrame Image, checks Json
        # maybe should be just a call to imageUpdate?
        # --------------------------------
        self.MainFrame.currentItemInfo['jNumber'] = self.MainFrame.itemRow[1][jnumber_column_index]
        self.MainFrame.jNumber = jnumber
        self.MainFrame.scanNumberText.Clear()
        self.MainFrame.scanNumberText.AppendText(jnumber)
        self.MainFrame.palletNumberText.SetValue(pallet_number)
        self.onScanNumberText(self)
        # update MainFrame.currentItemInfo with itemRow information ... msrp, type, etc
        for key in self.MainFrame.itemRow[0]: # itemRow = [[column_indexes],[itemRow]]
            index = self.MainFrame.itemRow[0].index(key)
            self.MainFrame.currentItemInfo.update({key:self.MainFrame.itemRow[1][index]})
        self.MainFrame.currentItemInfo['jNumber'] = self.MainFrame.jNumber # :( why are so many variables mixed naming GRRRRRRRRR
        self.infoLogger('Added MainFrame.itemRow to currentItemInfo'+str(self.MainFrame.itemRow))
        # sets scanNumberText and looks up json_state_file
        # hide clear 
        self.MainFrame.currentConditionText.Clear()
        self.MainFrame.currentConditionText.AppendText(condition)
        self.MainFrame.currentConditionNotesText.Clear()
        self.MainFrame.currentConditionNotesText.AppendText(condition_notes)
        self.MainFrame.currentDateListedText.Clear()
        self.MainFrame.currentTitleText.Clear()
        self.MainFrame.currentTitleText.AppendText(title)
        self.MainFrame.rSizer.Show(self.MainFrame.rSizerCurrentItemSizer)
        self.MainFrame.currentBoxLbl.Hide()
        self.MainFrame.currentBoxText.Hide()
#        self.MainFrame.scanNumberText.Clear()
 #       self.MainFrame.scanNumberText.AppendText(jnumber)
        self.MainFrame.ebayCategoryIdText.SetValue('')
        self.infoLogger('Found item row, and set values onLookUpBySkuBtn')
        self.MainFrame.palletNumberText.SetValue(pallet_number)
        # redraw frame
        self.MainFrame.mainSizer.Fit(self.MainFrame)
        self.MainFrame.mainPanel.Layout()
        self.MainFrame.mainPanel.Refresh()
        return
    def onLookUpBySkuBtn(self, event):
        '''
        Begins lookup process when lookUpBySkuBtn is pressed
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventsHandler.onLookUpBySkuBtn(): #')
        self.MainFrame.scanNumberText.SetValue("")
        # check which action needs to be taken
        if self.MainFrame.lookupManifestedRadio.GetValue() is True:
            self.currentSkuText = self.MainFrame.currentSkuText.GetValue()
            if self.currentSkuText is "" or None:
                tmp_dialog = wx.MessageDialog(self.MainFrame, 'Sku was not entered', 'ValueError', wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
            #-------------------------------------------
            # Begin lookup of item info.
            #-------------------------------------------
            self.MainFrame.itemRow = self.MainFrame.csvTextReader.returnRowBySku(self.currentSkuText)
            # store retailer_code
            try:
                self.MainFrame.retailer_code = self.MainFrame.itemRow[0][0].split(":")[-1]
            except Exception,e:
                self.debugLogger("retailer_code",e)
                pass
            # if TypeError then self.MainFrame.itemRow returned None, or nil
            try:
                self.MainFrame.itemRowDict = dict(zip(self.MainFrame.itemRow[0], self.MainFrame.itemRow[1]))
            except TypeError, e:
                self.infoLogger(e)
                tmp_dialog = wx.MessageDialog(self.MainFrame, str(e)+'\n\nDidnt find the sku:\n'+self.currentSkuText, 'ValueError', wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
        else:
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'What!?!?\n\n Are you sure you want to look up by sku when manifesting? Maybe switch the action to Lookup Manifested?', 'ValueError', wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        # make sure retailer_code matches retailerRadio
        if ( self.MainFrame.fingerRadio.GetValue() is True ) and ( self.MainFrame.retailer_code is '0' ):
            self.onLookUpBySkuBtnFinger()
        elif ( self.MainFrame.shopHqRadio.GetValue() is True ) and ( self.MainFrame.retailer_code is '1' ):
            self.onLookUpBySkuBtnShopHq()
        else:
            self.MainFrame.retailerLbl.SetForegroundColour((255,0,0))
            self.defaultFont = self.MainFrame.retailerLbl.GetFont()
            font = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
            self.MainFrame.retailerLbl.SetFont(font)
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'Retailer Code doesnt match selected retailer.\n\n Please select the correct Retailer.', 'UserError', wx.OK)
            results = tmp_dialog.ShowModal()
            if results == wx.ID_OK:
                tmp_dialog.Destroy()
            self.MainFrame.retailerLbl.SetForegroundColour((0,0,0))
            self.MainFrame.retailerLbl.SetFont(self.defaultFont)
            return
        return
        
    def onEbayCategoryIdText(self, event):
        '''
        Saves
        '''
        self.infoLogger("Inside: ")
        self.MainFrame.currentItemInfo['ebay_category'] = self.MainFrame.ebayCategoryIdText.GetValue()
        self.MainFrame.currentItemInfo['*Category'] = self.MainFrame.currentItemInfo['ebay_category']
        self.debugLogger(str(self.MainFrame.currentItemInfo['ebay_category']))
        cat_len = len(self.MainFrame.currentItemInfo['ebay_category']) 
        # if cat_len is not 0:
            # self.infoLogger("Entering Save(self.MainFrame)")
            # Save(self.MainFrame)
        # else:
            # self.infoLogger('Not Saving'+str(cat_len))
        return
        
    def onCurrentSkuText(self, event):
        '''
        Updates self.MainFrame.startingSkuNumber to self.MainFrame.currentSkuText.GetValue()
        '''
        self.infoLogger("Inside: ")
        self.MainFrame.startingSkuNumber = self.MainFrame.currentSkuText.GetValue()
        self.debugLogger(". self.MainFrame.startingSkuNumber Updated to: ", str(self.MainFrame.startingSkuNumber))
        return
        
    def updateCurrentItemSku(self, event):
        '''
        Updates self.MainFrame.currentItemInfo['sku']
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventHandler.updateCurrentItemSku(): #')
        self.MainFrame.currentItemInfo['sku'] = str(self.MainFrame.startingSkuNumber + 1)
        self.infoLogger(". self.MainFrame.startingSkuNumber Updated to: " + self.MainFrame.startingSkuNumber)
        return
        
    def onPalletNumberText(self, event):
        '''
        save palletNumbertTxt Value when text is entered
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventHandler.onPalletNumberText(): #')
        self.MainFrame.palletNumber = self.MainFrame.palletNumberText.GetValue()
        self.MainFrame.palletNumber = self.MainFrame.palletNumber
        self.MainFrame.currentItemInfo['palletNumber'] = self.MainFrame.palletNumber
        self.MainFrame.statusbar.SetStatusText('Updated palletNumber to:'+self.MainFrame.palletNumber)
        return
        
    def onRetailerRadio(self, event):
        '''
        updates current self.MainFrame.jNumberFolder
        self.MainFrame.currentItemInfo['jNumber']
        set statusbar
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventsHandler.onRetailerRadio() ')
        if self.MainFrame.fingerRadio.GetValue() is True:
            self.MainFrame.statusbar.SetStatusText('Finger Radio Selected. CWD:' + self.MainFrame.defaultJPagesFolder)
        if self.MainFrame.shopHqRadio.GetValue() is True:
            self.MainFrame.statusbar.SetStatusText('ShopHq Radio Selected. CWD:' + self.MainFrame.defaultJPagesFolder)
        return
        
    def onDateListedText(self, event):
        '''
        updates the date listed box with the current date
        '''
        self.infoLogger("inside: ")
        self.infoLogger('date listed things')
        currentdate = time.strftime("%m/%d")
        self.MainFrame.currentDateListedText.SetValue(currentdate) 
        return
        
    def onSaveCurrentTextBtn(self, event):
        '''
        ###########################################
        # Save the state of self.descriptionTextField when
        # saveDescriptionTextBtn is clicked (wx.EVT_BUTTON)
        #
        # #########################################
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventHandler.onSaveCurrentTextBtn(): #')
        # get value of self.descriptionTextField
        self.descriptionText = self.MainFrame.descriptionTextField.GetValue()
        self.MainFrame.currentItemInfo['description'] = self.descriptionText
        Save(self.MainFrame)
        self.infoLogger('Called Save(self.MainFrame)')
        print self.descriptionText.encode('ascii','ignore')
        # write value
        return
        
    def onSelectImageBtn(self, event):
        '''
        Creates a dialogue with item image choices. Radio button
        images
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventHandler.onSelectImageBtn(): #')
        self.MainFrame.currentItemInfo['itemSelectedImages'] = {}
        onSelectImageBtnFrame = ImageSelectionFrame(None, -1, 'Select The Correct Image')
        onSelectImageBtnFrame.setMainFrame(self.MainFrame)
        onSelectImageBtnFrame.Show(True)
        onSelectImageBtnFrame.Centre()
        self.infoLogger('. onSelectImageBtn: Clicked...')
        return
        
    def onbeginShelfNumberText(self, event):
        '''
        Not completed Does nothing
        '''
        self.infoLogger("Inside: ")
        return
        
    def updateCurrentItemInfo(self):
        '''
        updates self.MainFrame.currentItemInfo so that it contains all required
        information to onBuildEbayAuction
        
        '''
        self.infoLogger("Inside: ")
        try:
            self.MainFrame.currentItemInfo['title'] = self.MainFrame.itemRowDict['title'].rstrip(' ')
            self.MainFrame.currentItemInfo['msrp'] = self.MainFrame.itemRowDict['msrp']
            self.MainFrame.currentTitleText.SetValue(self.MainFrame.currentItemInfo['title'].lower().title())
        except Exception, e:
            self.infoLogger(traceback.format_exc())
            self.debugLogger(e)
            pass
        return
        
    def onBuildEbayAuction(self, event):
        '''
        Builds ebay auction from json? Generates and appends it to a ebay verification
        csv file. ?
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventsHandler.onBuildEbayAuction(): #')
        sku = self.MainFrame.currentSkuText.GetValue()
        palletNumber = self.MainFrame.palletNumberText.GetValue()
        initials = self.MainFrame.listerInitialsText.GetValue()
        beginShelfNumber = self.MainFrame.beginShelfNumberText.GetValue()
        ebayCategoryId = self.MainFrame.ebayCategoryIdText.GetValue()
        self.infoLogger('. '+str(self.MainFrame.currentItemInfo))
        if '#REQUIRED' in ebayCategoryId:
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'Please fill in the Ebay Category ID.\n\n This means that this item has not been seen before and is not located in the unique_category_4numbeer_sku.csv file... jeez i need to rename this file to something useful...', 'Not Seen Before', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        if len(sku) is 0:
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'CurrentSkuText is empty.\n\nFill it in.', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        if len(beginShelfNumber) is 0:
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'Beginning Shelf Number is empty..\n\nFill it in.', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        if len(palletNumber) is 0:
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'palletNumber is empty.\n\nFill it in.', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        if len(initials) is 0:
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'Initials is empty.\n\nFill it in.', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        sources = self.MainFrame.currentItemInfo['itemSelectedImages']
        self.debugLogger('Assign pictures to ebay auction: ', sources)
        self.MainFrame.currentItemInfo['image_sources'] = None
        self.MainFrame.currentItemInfo.update({'image_sources':sources})
        self.infoLogger(sources)
        #-------------------------------------------------------
        # with ebay archive open return item specifics for jnumber
        # returns item_category, item_specifics from sky_manifest.returnItemSpecifics()
        #
        #  item_specifics = item_row[ErrorMessageIndex].split('Please provide the required item specifics.|')[-1].split('|')[0].split('#comma# ')
        #
        #-------------------------------------------------------
        # Item specifics fetcher  Searches through
        # ebay Verification_Results by category number
        # if the catefory number is found
        # it will return a list
        # returns [item_category, item_specifics]
        self.MainFrame.itemSpecifics = self.MainFrame.itemSpecificsFetcher.returnItemSpecifics(self.MainFrame.scanNumberText.GetValue())
        self.infoLogger('# self.MainFrame.itemSpecifics onBuildEbayAuction(): ' +str(self.MainFrame.itemSpecifics))
        self.MainFrame.ebayCategoryIdLbl.Show()
        self.MainFrame.ebayCategoryIdText.Show()
        self.MainFrame.mainPanel.Fit()
        self.MainFrame.mainPanel.Layout()
        # if item is not in ebay archive itemSpecifics 'ValueError' will be in item
        try:
            int_ebay_category = int(self.MainFrame.ebayCategoryIdText.GetValue())
        except:
            pass
        if 'ValueError' in self.MainFrame.itemSpecifics:
            # ebayCategoryIdText is empty notify user and set self.MainFrame.itemSpecifics to '#REQUIRED'
            # build auction pressed and ebay category is empty
            if len(self.MainFrame.ebayCategoryIdText.GetValue()) is 0:
                tmp_dialog = wx.MessageDialog(self.MainFrame, 'Item not seen before.\n\nUnable to determine category number, or item_specifics', 'ValueError', style=wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                self.MainFrame.itemSpecifics = '#REQUIRED'
                self.MainFrame.ebayCategoryIdText.SetValue(self.MainFrame.itemSpecifics)
                return
            # build auction was pressed but ebay category was not filled in
            elif '#REQUIRED' in self.MainFrame.ebayCategoryIdText.GetValue():
                tmp_dialog = wx.MessageDialog(self.MainFrame, 'Please fill in currentEbayCategoryId', 'ValueError', style=wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
            # ValueError, but category number has been entered
            elif isinstance(int_ebay_category, int):
                tmp_dialog = wx.MessageDialog(self.MainFrame, 'Item not seen before.\n\nUnable to determine category number, or item_specifics. Building without specifics.', 'ValueError', style=wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                results = ['']
                self.currentItemSpecificsDict = results # [item_category, [item_specifics]] sky_manifest.returnItemSpecifcs()
                self.MainFrame.currentItemSpecificsDict = self.currentItemSpecificsDict
            else:
                self.infoLogger('item specifics issue')
                tmp_dialog = wx.MessageDialog(self.MainFrame, 'Item not seen before.\n\nUnable to determine category number, or item_specifics', 'ValueError', style=wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
        # if item in archive retrieve it and get title
        if 'ValueError' not in self.MainFrame.itemSpecifics:
            # ebay category is a number and is filled in.
            if isinstance(int_ebay_category, int):
                results = ItemSpecificsDialog(None, -1,title='Please Fill In The Item Specifics')
                if results.ShowModal() == wx.ID_OK:
                    self.currentItemSpecificsDict = results.currentItemSpecificsDict # [item_category, [item_specifics]]
                    self.MainFrame.currentItemSpecificsDict = self.currentItemSpecificsDict
                    results.Destroy()
                self.infoLogger('. Item Specifics:'+str(self.currentItemSpecificsDict))
        self.MainFrame.listingSku = '-'.join([str(sku), str(palletNumber), str(beginShelfNumber), str(initials)])
        self.infoLogger("Starting BuildAuction")
        buildAuction = BuildAuction(self.MainFrame.currentItemInfo, self.MainFrame.listingSku, self.currentItemSpecificsDict, self.MainFrame.ebayAuctionHeaders, self.MainFrame.listingPreferencesResults, self.MainFrame)
        self.infoLogger("Trying to returnHtmlStringForListing")
        self.MainFrame.ebayListingHtml = buildAuction.returnHtmlStringForListing()
        self.infoLogger("Trying to generateEbayListingCsvLine")
        self.MainFrame.ebayCsvFp = buildAuction.generateEbayListingCsvLine()
        if 'IOError' in self.MainFrame.ebayCsvFp:
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'Is the file open bro?', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        # begin ssh dialog
        if self.MainFrame.ssh_pass is None:
            tmp_dialog = wx.PasswordEntryDialog(self.MainFrame, 'SSH Transfer: Please enter the server password ', 'Password', style=wx.OK)
            tmp_dialog.ShowModal()
            self.MainFrame.ssh_pass =  tmp_dialog.GetValue()
            tmp_dialog.Destroy()
            if len(self.MainFrame.ssh_pass) is 0:
                tmp_dialog = wx.MessageDialog(self.MainFrame, 'No password was entered', 'Password', style=wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
        results = self.MainFrame.ssh.putFiles(sources, self.MainFrame.listingSku, self.MainFrame.ebayListingHtml, self.MainFrame.currentItemInfo)
        if results is True:
             self.MainFrame.statusbar.SetStatusText('Transfer Successful.')
             tmp_dialog = wx.MessageDialog(self.MainFrame, 'Nice!\n\nTODO:Now clear the screen and move to next.', 'Nice!', style=wx.OK)
             results = tmp_dialog.ShowModal()
             tmp_dialog.Destroy()
        # set and clear
        self.MainFrame.currentImgPath = self.MainFrame.defaultImgPath
        img = wx.Image(self.MainFrame.defaultImgPath, wx.BITMAP_TYPE_ANY)
        self.MainFrame.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        self.MainFrame.browseText.SetValue("")
        self.MainFrame.currentItemInfo['itemSelectedImages'] = {}
        self.MainFrame.descriptionTextField.Clear()
        self.MainFrame.scanNumberText.SetValue("")
        self.MainFrame.jNumber = self.MainFrame.defaultJNumber
        self.MainFrame.currentItemInfo = self.MainFrame.defaultJNumberInfo
        self.MainFrame.prevListingSku = self.MainFrame.listingSku
        self.MainFrame.imageCountLbl.SetLabel('Images Selected: '+str(len(self.MainFrame.currentItemInfo['itemSelectedImages'])))
        self.MainFrame.currentSkuText.SetValue("")
        self.MainFrame.ebayCategoryIdText.SetValue("")
        self.MainFrame.statusbar.SetStatusText('Ready.                                   Last Uploaded:'+str(self.MainFrame.prevListingSku))
        self.MainFrame.currentSkuText.SetFocus()
        try:
            self.MainFrame.rSizer.Hide(self.MainFrame.rSizerCurrentItemSizer)
        except AttributeError, e:
            self.infoLogger(traceback.format_exc())
            self.infoLogger(e)
        self.MainFrame.mainPanel.Fit()
        self.MainFrame.mainPanel.Refresh()
        self.MainFrame.currentItemInfo = {}
        return
        
    def onLookupManifestedRadio(self, event):
        '''
        Prepares self.MainFrame.items for Lookup of items
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventsHandler: onLookupManifestedRadio #')
        filename = self.csvFileBrowse()
        self.MainFrame.statusbar.SetStatusText('Opening: ' + str(filename[0]))
        self.MainFrame.startingSkuLbl.SetLabel('Lookup Sku')
        self.MainFrame.csvTextReader = self.MainFrame.sky_manifest.ManifestReader(filename[0],self.MainFrame)
        self.MainFrame.statusbar.SetStatusText('Opened: ' + str(filename[0]))
        self.MainFrame.lookUpBySkuBtn.Show()
        self.MainFrame.lookUpBySkuSizer.Layout()
        self.MainFrame.buildAuctionButton.Show()
        self.MainFrame.beginShelfNumberLbl.Show()
        self.MainFrame.beginShelfNumberText.Show()
        self.MainFrame.listerInitialsLbl.Show()
        self.MainFrame.listerInitialsText.Show()
        self.MainFrame.newItemButton.Hide()
        self.MainFrame.upcNumberLbl.Hide()
        self.MainFrame.upcNumberText.Hide()
        self.MainFrame.scanNumberText.Hide()
        self.MainFrame.scanNumberLbl.Hide()
        self.MainFrame.mainSizer.Fit(self.MainFrame)
        self.MainFrame.mainPanel.Layout()
        self.MainFrame.mainPanel.Refresh()
        return
        
    def onBeginManifestingRadio(self, event):
        '''
        Prepares Mainframe.items to begin manifesting items
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventsHandler: onBeginManifestingRadio #')
        try:
            self.MainFrame.rSizer.Hide(self.MainFrame.rSizerCurrentItemSizer)
        except AttributeError, e:
            self.infoLogger(traceback.format_exc())
            self.infoLogger(e)
        filename = self.csvFileBrowse()
        self.MainFrame.statusbar.SetStatusText('Opening: ' + str(filename[0]))
        self.MainFrame.startingSkuLbl.SetLabel('Starting Sku')
        self.MainFrame.scanNumberText.Clear()
        self.MainFrame.csvTextReader = self.MainFrame.sky_manifest.ManifestReader(filename[0],self.MainFrame)
        self.MainFrame.csvTextWriter = self.MainFrame.sky_manifest.ManifestWriter(filename[0],self.MainFrame)
        self.MainFrame.statusbar.SetStatusText('Opened: ' + str(filename[0]))
        self.MainFrame.buildAuctionButton.Hide()
        self.MainFrame.lookUpBySkuBtn.Hide()
        self.MainFrame.beginShelfNumberLbl.Hide()
        self.MainFrame.beginShelfNumberText.Hide()
        self.MainFrame.listerInitialsLbl.Hide()
        self.MainFrame.listerInitialsText.Hide()
        self.MainFrame.ebayCategoryIdLbl.Hide()
        self.MainFrame.ebayCategoryIdText.Hide()
        self.MainFrame.listerInitialsLbl.Hide()
        self.MainFrame.listerInitialsText.Hide()
        self.MainFrame.upcNumberLbl.Hide()
        self.MainFrame.upcNumberText.Hide()
        self.MainFrame.scanNumberLbl.Show()
        self.MainFrame.scanNumberText.Show()
        self.MainFrame.newItemButton.Show()
        self.MainFrame.mainSizer.Fit(self.MainFrame)
        self.MainFrame.mainPanel.Layout()
        self.MainFrame.mainPanel.Refresh()
        return
        
    def onBrowse(self, event):
        '''
        #############################
        # Browse for file (wildcards for JPEG files)
        ##############################
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventHandler: onBrowse: #')
        self.MainFrame.currentItemInfo['itemSelectedImages'] = {}
        wildcard = "JPEG files (*.jpg,*.JPEG,*.jpeg,*.JPG)|*.jpg;*.JPEG;*.jpeg;*.JPG|( PNG*.png*)|*.png"
        dialog = wx.FileDialog(None, "Choose a file",
                               wildcard=wildcard,
                               style=wx.OPEN | wx.FD_MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.infoLogger(('. ' + str(self.MainFrame.__dict__.keys())))
            self.imgPaths = dialog.GetPaths()
            self.infoLogger('. type(paths):'+str( type(self.imgPaths)))
            self.MainFrame.browseText.SetValue("\""+'\"; \"'.join(self.imgPaths)+"\"")
            for item in self.imgPaths:
                self.MainFrame.currentItemInfo['itemSelectedImages'].update({item:'True'})
            self.infoLogger('. GetPath:'+ str(dialog.GetPath()))
            self.infoLogger('. GetFilenames:'+ str(dialog.GetFilenames()))
            self.infoLogger('. GetPaths: '+ str(dialog.GetPaths()))
            self.infoLogger('. GetDirectory: '+ str(dialog.GetDirectory()))
        dialog.Destroy()
        self.updateMainframeImage()
        return
        
    def updateMainframeImage(self):
        '''
        ##########
        # refreshes self.panel with a given image path
        ###########
        This is used for JPEG onBrowse.... should be used
        for each onJPEG change.
        '''
        self.infoLogger("Inside: ")
        self.fp = self.MainFrame.browseText.GetValue()
        self.infoLogger('# PhotoCtrlEventHandler: onView: #')
        self.infoLogger('. self.imgPaths:'+ str( self.imgPaths))
        print(self.imgPaths)
        img = wx.Image(self.imgPaths[0], wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.MainFrame.PhotoMaxSize
            NewH = self.MainFrame.PhotoMaxSize * H / W
        else:
            NewH = self.MainFrame.PhotoMaxSize
            NewW = self.MainFrame.PhotoMaxSize * W / H
        img = img.Scale(NewW, NewH)
        self.MainFrame.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        self.MainFrame.imageCountLbl.SetLabel('Current Number of Selections:'+str(len(self.imgPaths)))
        self.MainFrame.mainPanel.Refresh()
        return
        
    def setJNumberFolder(self,retailer_code):
        '''
        Sets MainFrame.jNumberFolder based on retailer_code
        '''
        if '0' in retailer_code:
            self.MainFrame.scanNumberTextValue = self.MainFrame.scanNumberText.GetValue().split('-')[0].upper()
            self.MainFrame.jNumber = self.MainFrame.scanNumberTextValue[1:6]
            self.MainFrame.jNumberFolder = self.MainFrame.jNumber
            self.MainFrame.jNumberFolderPath = os.path.join(self.MainFrame.defaultJPagesFolder,self.MainFrame.jNumberFolder)
            self.MainFrame.currentItemInfo['jNumberFolderPath'] = self.MainFrame.jNumberFolderPath
        if '1' in retailer_code:
            self.MainFrame.scanNumberTextValue = self.MainFrame.scanNumberText.GetValue().split('-')[0].upper()
            self.MainFrame.jNumber = self.MainFrame.scanNumberTextValue
            self.MainFrame.jNumberFolder = self.MainFrame.jNumber
            self.MainFrame.jNumberFolderPath = os.path.join(self.MainFrame.defaultJPagesFolder,self.MainFrame.jNumberFolder)
            self.MainFrame.currentItemInfo['jNumberFolderPath'] = self.MainFrame.jNumberFolderPath
        return
        
    def updateMainFrameCurrentItemInfo(self,retailer_code):
        '''a
        determine which action needs to be taken based off of
        json_results
        if json_results is True
            load json
        if json_results is False
            fetchPage()
        '''
        self.MainFrame.currentItemInfo['retailer_code'] = retailer_code
        # set the jNumber from scanNumberText
        check = Check(self.MainFrame)
        self.setJNumberFolder(retailer_code)
        #-------------------------------------------------------
        # load json if exists  (json created on scanNewItem ... or Save(  self.Mainframe)
        # updates currentItemInfo
        # return True
        # else return False
        #-------------------------------------------------------
        json_exists = check.loadMainFrameJson() # updates currentItemInfo if True
        self.infoLogger('Post json_exists: '+str(self.MainFrame.currentItemInfo) )
        print('json_exists:',json_exists)
        if json_exists is True:
            self.MainFrame.statusbar.SetStatusText('Found json_state_file.')
            self.prev_image = check.defaultImageSelections() # returns image path or None
            self.MainFrame.currentImgPath = self.prev_image
            self.infoLogger('\n# PhotoCtrlEventHandler.onScanNumberText(): self.prev_image #')
            self.infoLogger('. Previous Images: ')
            self.infoLogger('. '+str(self.MainFrame.currentItemInfo['itemSelectedImages']))
            self.MainFrame.imageCountLbl.SetLabel('Images Selected: '+str(len(self.MainFrame.currentItemInfo['itemSelectedImages'])))
            self.infoLogger(('. ' + str(self.prev_image)))
            self.infoLogger('. Found Previous Image Selection: '+str(self.MainFrame.currentImgPath))
            #-------------------------------------------------------
            # 
            # prev_image -> currentImgPath if seen
            # else if currentImgPath is empty update image
            #-------------------------------------------------------
            if ("None" in str(self.MainFrame.currentImgPath)) or (self.MainFrame.currentImgPath is None):
                self.infoLogger('None in self.MainFrame.currentImgPath: '+str(self.MainFrame.currentImgPath))
                results = FetchPage(self.MainFrame).results # updates currentItemInfo
                if isinstance(results,Exception):
                    if 'ImageListEmpty' in results[0]:
                        int_dialog = wx.MessageDialog(self.MainFrame, 'Page not found for?: ' + str(self.MainFrame.jNumber)+'\n\n', 'IndexError', wx.OK)
                        int_dialog.ShowModal()
                        int_dialog.Destroy()
                        return None
                self.img_name = check.guessImageName()
                self.MainFrame.currentImgPath = os.path.join(self.MainFrame.jNumberFolderPath,self.img_name)
                self.infoLogger(self.img_name)
            self.infoLogger('Before updateMainFrameCurrentItemInfo Return: '+str(self.MainFrame.currentItemInfo)) 
            return True
        #-------------------------------------------------------
        # if no json, fetchPage()
        # download images
        # 
        #-------------------------------------------------------
        else:
            self.MainFrame.statusbar.SetStatusText('Didnt find json_state_file.')
            try:
                try:
                    results = FetchPage(self.MainFrame).results     # results = {image_list:[],description:''}
                    self.debugLogger('MainFrameEventHandler.updateMainFrameCurrentItemInfo',results)
                    
                except Exception, results:
                    if isinstance(results,Exception):
                        if 'ImageListEmpty' in results[0]:
                            self.debugLogger(results)
                            int_dialog = wx.MessageDialog(self.MainFrame, 'Page not found for?: ' + str(self.MainFrame.jNumber)+'\n\n', 'IndexError', wx.OK)
                            int_dialog.ShowModal()
                            int_dialog.Destroy()
                            return None
                if isinstance(results,Exception):
                    return Exception('ImageListEmpty Item page may not exist?',results)
                self.MainFrame.currentItemInfo['image_list'] = results['image_list']
                self.MainFrame.currentItemInfo['description'] = results['description']
            except Exception, e:
                int_dialog = wx.MessageDialog(self.MainFrame, 'We had an Unhandled Exception ' + str(self.MainFrame.jNumber), 'Error', wx.OK)
                results = int_dialog.ShowModal()
                int_dialog.Destroy()
                return
            #---------------------------------------------
            # download image_list
            #
            # image_list created in sky_scraper
            # image_list downloaded in Check.downloadimages
            #---------------------------------------------
            try:
                self.infoLogger('############### Begin download images ##############')
                images = check.downloadImages()
                self.MainFrame.statusbar.SetStatusText('Done Getting images')
                p = Process(target=images, args=())
                p.start()
                p.join()
            except Exception:
                self.infoLogger(traceback.format_exc())
            self.debugLogger("json results",results)
            # set currentItemInfo to found resuls
            self.MainFrame.currentItemInfo['image_list'] = results['image_list']
            self.MainFrame.currentItemInfo['description'] = results['description']
            self.img_name = check.guessImageName() # relies on self.MainFrame.currentItemInfo['jNumber'] image_list
            self.infoLogger('MainFrameEventHandler.updateMainFrameCurrentItemInfo.img_name'+str(self.img_name))
            if self.img_name is None:
                print(results)
                exit()
            self.MainFrame.currentImgPath = os.path.join(self.MainFrame.jNumberFolderPath,self.img_name)
            self.MainFrame.currentImgPath = self.MainFrame.currentImgPath
            #Save(self.MainFrame)
            return
            
    def onScanNumberText(self, event):
        '''
        onScanNumberText checks retailer jnumber type and updates self.MainFrame
        to display the current item info. Whether from json, or as a first item
        '''
        self.infoLogger("Inside: ")
        self.infoLogger('\n# PhotoCtrlEventHandler.scanNumberText() #')
        self.MainFrame.palletNumber = self.MainFrame.palletNumberText.GetValue()
        self.MainFrame.scanNumberTextValue = self.MainFrame.scanNumberText.GetValue().upper()
        if len(self.MainFrame.palletNumber) is 0:
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'palletNumber is empty.\n\nFill it in.', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        #---------------------------------------------
        # Check if the wrong retailerRadio
        #---------------------------------------------
        if (( '4' not in self.MainFrame.scanNumberTextValue[0]) or ( 'J' not in self.MainFrame.scanNumberTextValue[0])) is False :
            self.MainFrame.statusbar.SetStatusText('I dont understand:' + self.MainFrame.currentItemInfo['jNumber'] + ' Maybe it should start with a J or a 4?')
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'ERROR: Please enter a Jnumber or a 4number.\n\nEntered:' + str(self.MainFrame.jNumber)+'\n\nexamples. J123456 or 4NK420000001', 'UserError', wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        if 'J' in self.MainFrame.scanNumberTextValue[0]:
            self.MainFrame.statusbar.SetStatusText('I see a Jnumber')
            if self.MainFrame.fingerRadio.GetValue() is True:
                    tmp_dialog = wx.MessageDialog(self.MainFrame, 'ERROR: Please select ShopHQ Radio button for: ' + str(self.MainFrame.scanNumberTextValue) + '\n\nCurrent selection: FingerHut', 'UserError', wx.OK)
                    results = tmp_dialog.ShowModal()
                    tmp_dialog.Destroy()
                    return
        elif '4' in self.MainFrame.scanNumberTextValue[0]:
            self.MainFrame.statusbar.SetStatusText(' I see a 4number')
            if self.MainFrame.shopHqRadio.GetValue() is True:
                    tmp_dialog = wx.MessageDialog(self.MainFrame, 'ERROR: Please select Fingerhut Radio button for:' + str(self.MainFrame.scanNumberTextValue) + '\n\nCurrent selection: ShopHQ', 'UserError', wx.OK)
                    results = tmp_dialog.ShowModal()
                    tmp_dialog.Destroy()
                    return
        #---------------------------------------------
        # Check if action selected
        #---------------------------------------------
        # lookupManifested action selected
        #---------------------------------------------
        if self.MainFrame.lookupManifestedRadio.GetValue() is True:
            #----------------------------------------------------
            # results  returned is 
                    # results_dict = {'sku_column_index': sku_column_index,
                        # 'jnumber_column_index': jnumber_column_index,
                        # 'manifested_column_index': manifested_column_index,
                        # 'manifested_column': manifested_column,
                        # 'row_index_matches': row_index_matches,
                        # 'manifested_count': manifested_count,
                        # 'title_column': title_column,
                        # 'title_column_index': title_column_index,
                        # 'upc_column_index': upc_column_index,
                        # 'pallet_number_index': pallet_number_index,
                        # 'pallet_number_column': pallet_number_column,
                        # 'currentSku': '',
                        # 'titleModelSelection': '',
                        # 'jnumber': jnumber,
                        # 'retailer_code': retailer_code
                        # }
            #-----------------------------------------------------
            results = self.MainFrame.csvTextReader.checkIfManifested(self.MainFrame.jNumber, self.MainFrame.palletNumber)
            self.checkIfManifestedResults = results
            if isinstance(results, dict):
                self.MainFrame.statusbar.SetStatusText('Found item dictionary.')
            else:
                self.MainFrame.statusbar.SetStatusText(str(results))
         #-------------------------------------------------------
         # begin manifesting  action selected
         #-------------------------------------------------------
        elif self.MainFrame.beginManifestingRadio.GetValue() is True:
            self.infoLogger('. PhotoCtrlEventsHandler.onScanNumberText(): Updating dictionaryManifestResults.')
            results = self.MainFrame.csvTextReader.checkIfManifested(self.MainFrame.scanNumberTextValue, self.MainFrame.palletNumber)
            self.checkIfManifestedResults = results
            self.debugLogger(results)
            #----------------------------------------------------
            # Check for any missing/incorrect headers
            #----------------------------------------------------
            try:
                if 'retailer_code is incorrect' in str(results):
                    self.infoLogger("A dialog should pop up indicating that the retailer_code is wrong")
                    tmp_dialog = wx.MessageDialog(self.MainFrame, str(results)+'\n\nCheck Cell A1 in csv. Format: \"retailer_code:#\"\nFH is 0\n shophq is 1', 'UserError', wx.OK)
                    results = tmp_dialog.ShowModal()
                    tmp_dialog.Destroy()
                    self.MainFrame.statusbar.SetStatusText(str(results))
                    return
                if 'is not in list' in str(results):
                    self.infoLogger("A dialog should pop up indicating that a HEADER is missing")
                    tmp_dialog = wx.MessageDialog(self.MainFrame, str(str(results)+'\n\nThis would indicate that one of the headers is missing. Check the csv file for all headers (jnumber, sku, upc, pallet_number, retailer_code:X, msrp, title, manifested, etc)\n\n Are one of these missing?\n\n *HINT:*You can edit the csv, and retry scanning.'), 'UserError', wx.OK)
                    results = tmp_dialog.ShowModal()
                    tmp_dialog.Destroy()
                    self.MainFrame.statusbar.SetStatusText(str(results))
                if isinstance(results, dict):
                    self.MainFrame.statusbar.SetStatusText('Found item dictionary.')
                    self.MainFrame.dictionaryManifestResults = results
                else:
                    raise results
                    #self.debugLogger("Issue with MainFrame.csvTextReader.checkIfManifested",results)
            except Exception:
                self.debugLogger('HEADER Not Found in CSV, or some error with results = self.MainFrame.csvTextReader.checkIfManifested',results)
                return
         #-------------------------------------------------------
         # Catch no action selected
         #-------------------------------------------------------
        else:
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'No action was selected:\n\n *Begin Manifesting\n    or\n *Lookup Manifested Item', 'UserError', wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        #--------------------------------------
        # Test retailer_code
        # updateMainFrameCurrentItemInfo
        #       Checks json results
        #       Determines image_list from json
        #
        # ----------------------------------------------------
        retailer_code = self.checkIfManifestedResults['retailer_code']
        try:
            results = self.updateMainFrameCurrentItemInfo(retailer_code) #<---------------------- 
            self.infoLogger('updateMainFrameCurrentItemInfo results:'+str(results))
        except Exception, results:
            self.debugLogger('results issue: ',results)
            return results
        if isinstance(results,Exception):
            if 'ImageListEmpty' in results[0]:
                self.debugLogger(results)
                int_dialog = wx.MessageDialog(self.MainFrame, 'Page not found for?: ' + str(self.MainFrame.jNumber)+'\n\n', 'IndexError', wx.OK)
                int_dialog.ShowModal()
                int_dialog.Destroy()
                return results

        #----------------------------------------------------
        # update variables and mainframe image
        # SetValues  and Refresh mainPanel
        #----------------------------------------------------
        self.infoLogger('onScanNumberText currentItemInfo: '+str(self.MainFrame.currentItemInfo) )
        self.infoLogger('Trying to open: '+str(self.MainFrame.currentImgPath))
        try:
            self.description = self.MainFrame.currentItemInfo['description']
            img = wx.Image(self.MainFrame.currentImgPath, wx.BITMAP_TYPE_ANY)
            # scale the image, preserving the aspect ratio
            W = img.GetWidth()
            H = img.GetHeight()
            if W > H:
                NewW = self.MainFrame.PhotoMaxSize
                NewH = self.MainFrame.PhotoMaxSize * H / W
            else:
                NewH = self.MainFrame.PhotoMaxSize
                NewW = self.MainFrame.PhotoMaxSize * W / H
            img = img.Scale(NewW, NewH)
            self.MainFrame.currentImgPath = self.MainFrame.currentImgPath
            self.MainFrame.descriptionTextField.Clear()
            try:
                self.MainFrame.descriptionTextField.AppendText(self.description.decode('utf8'))
            except UnicodeEncodeError, e:
                self.MainFrame.descriptionTextField.AppendText(self.description)
            try: # show lables
                self.MainFrame.ebayCategoryIdLbl.Show()
                self.MainFrame.ebayCategoryIdText.Show()
            except Exception, e:
                self.MainFrame.ebayCategoryIdLbl.Hide()
                self.MainFrame.ebayCategoryIdText.Hide()
                self.infoLogger(e)
                self.infoLogger(traceback.format_exc())
            self.MainFrame.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
            self.setJNumberFolder(retailer_code)
            #---------------------------------------------
            # SetValue of upc
            #---------------------------------------------
            try:
                self.MainFrame.upcNumberText.SetValue(self.MainFrame.currentItemInfo['upc'])
            except Exception,e:
                print(e)
                self.infoLogger("currentItemInfo['upc']"+str(e))
            try:
                self.MainFrame.ebayCategoryIdText.SetValue(self.MainFrame.currentItemInfo['ebay_category'])
            except Exception,e:
                print(e)
                self.infoLogger("currentItemInfo['ebay_category']"+str(e))
            self.MainFrame.statusbar.SetStatusText('Item Loaded:'+ self.MainFrame.currentItemInfo['jNumberFolderPath'])
            self.MainFrame.upcNumberLbl.Show()
            self.MainFrame.upcNumberText.Show()
            self.MainFrame.mainSizer.Fit(self.MainFrame)
            self.MainFrame.mainPanel.Layout()
            self.MainFrame.mainPanel.Refresh()
            return
        except Exception,e:
            self.infoLogger("A dialog should pop up indicating why we were unable to onScanNumberText")
            tmp_dialog = wx.MessageDialog(self.MainFrame, str(str(e)+"\n\nCheck the logs. Or, go to help PDB set trace and inspect the results. 'self.results.keys()' or 'self.results.['some_key']"), 'Error', wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            self.MainFrame.statusbar.SetStatusText(str(results))
            self.debugLogger("Couldn't update MainFrame",e)
            
    def onNewItemButton(self, event):
        '''
        Clear the frame/screen and begin process for new item
        '''
        self.infoLogger("Inside: ")
        if self.MainFrame.defaultImgPath in self.MainFrame.currentImgPath:
            tmp_dialog = wx.MessageDialog(self.MainFrame, 'No Item was loaded? Pizza?', 'ValueError', wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        self.infoLogger('\n# PhotoCtrlEventsHandler: onNewItemButton: #')
        Save(self.MainFrame)
        self.infoLogger('Called Save(self.MainFrame)')
        self.infoLogger('\n# PhotoCtrlEventsHandler: onNewItemButton: #')
        try:
            self.MainFrame.nextSkuNumber = str(int(self.MainFrame.currentSkuText.GetValue()) + 1).zfill(4)
        except ValueError, e:
            int_dialog = wx.MessageDialog(self.MainFrame, 'Sku was not entered', 'ValueError', wx.OK)
            results = int_dialog.ShowModal()
            int_dialog.Destroy()
            self.MainFrame.startingSkuLbl.SetLabel('Current Sku')
            self.MainFrame.currentSkuText.SetValue('HALP!')
            return
        # check which action needs to be taken
        if self.MainFrame.lookupManifestedRadio.GetValue() is True:
            results = self.MainFrame.csvTextReader.checkIfManifested(self.MainFrame.jNumber, self.MainFrame.palletNumber)
            self.MainFrame.statusbar.SetStatusText(str(results))
            self.MainFrame.palletNumber = self.MainFrame.palletNumberText.GetValue()
            self.currentSkuText = self.MainFrame.currentSkuText.GetValue()
            if self.MainFrame.fingerRadio.GetValue() is True:
                if len(self.MainFrame.palletNumberText.GetValue()) is 0:
                    tmp_dialog = wx.MessageDialog(self.MainFrame, 'Pallet Number not entered.\n\nEnter a pallet number', 'ValueError', wx.OK)
                    results = tmp_dialog.ShowModal()
                    tmp_dialog.Destroy()
            if self.currentSkuText is "" or None:
                tmp_dialog = wx.MessageDialog(self.MainFrame, 'Sku was not entered', 'ValueError', wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
            # Begin lookup of item info.
            self.itemRow = self.MainFrame.csvTextReader.returnRow()
            self.infoLogger(self.itemRow)
        #--------------------------------------------
        # begin manifesting action selected
        #--------------------------------------------
        elif self.MainFrame.beginManifestingRadio.GetValue() is True:
            self.MainFrame.dictionaryManifestResults['currentSku'] = str(int(self.MainFrame.currentSkuText.GetValue())).zfill(4)
            if self.MainFrame.fingerRadio.GetValue() is True:
                if len(self.MainFrame.palletNumberText.GetValue()) is 0:
                    tmp_dialog = wx.MessageDialog(self.MainFrame, 'Pallet Number not entered.\n\nEnter a pallet number', 'ValueError', wx.OK)
                    results = tmp_dialog.ShowModal()
                    tmp_dialog.Destroy()
                    return
                else:
                    self.MainFrame.dictionaryManifestResults['palletNumber'] = self.MainFrame.palletNumberText.GetValue()
                    self.MainFrame.dictionaryManifestResults['upc'] = self.MainFrame.upcNumberText.GetValue()
                    titles = self.MainFrame.csvTextWriter.returnTitlesForJnumber(self.MainFrame.dictionaryManifestResults)
            elif self.MainFrame.shopHqRadio.GetValue() is True:
                self.MainFrame.dictionaryManifestResults['palletNumber'] = self.MainFrame.palletNumberText.GetValue()
                self.MainFrame.dictionaryManifestResults['upc'] = self.MainFrame.upcNumberText.GetValue()
                titles = self.MainFrame.csvTextWriter.returnTitlesForJnumber(self.MainFrame.dictionaryManifestResults)
            self.MainFrame.currentTitleList = titles
            if len(self.MainFrame.currentTitleList) is not 0:
                titleSelectionDialog = ReturnCorrectTitleDialog(None, -1,title='Select the correct Title')
                titleSelectionDialog.setMainFrame(self.MainFrame)
                titleSelectionDialog.ShowModal()
                self.MainFrame.dictionaryManifestResults['titleModelSelection'] = titleSelectionDialog.title_and_row_index
            else:
                tmp_dialog = wx.MessageDialog(self.MainFrame, 'Did not find jNumber in manifest.\nAppending to end of file', 'ValueError', wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                self.MainFrame.dictionaryManifestResults['titleModelSelection'] = str('row_index:' + str(1) + ':' + '#TITLE HERE#')
            results = self.MainFrame.csvTextWriter.writeManifestedRow(self.MainFrame.dictionaryManifestResults)
            print results
            if results[0] is 13:
                print results
                print 'caught error'
                tmp_dialog = wx.MessageDialog(self.MainFrame, 'ERROR:\n\nFile is currently open in another program?\n\n'+results[1], 'IOError', wx.OK)
                tmp_selection = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
        #--------------------------------------------
        # Clear self.MainFrame and set to Defaults
        #--------------------------------------------
        self.infoLogger('\n##\n##\n## Clearing self.MainFrame ##\n##\n##\n##')
        self.MainFrame.statusbar.SetStatusText('Ready. Last Scan: '+str(self.MainFrame.jNumber)+' '+str(self.MainFrame.dictionaryManifestResults['titleModelSelection']))
        self.MainFrame.startingSkuLbl.SetLabel('Current Sku')
        self.MainFrame.currentSkuText.SetValue(self.MainFrame.nextSkuNumber)
        self.MainFrame.currentImgPath = self.MainFrame.defaultImgPath
        img = wx.Image(self.MainFrame.defaultImgPath, wx.BITMAP_TYPE_ANY)
        self.MainFrame.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        self.MainFrame.browseText.Clear()
        self.MainFrame.currentItemInfo['itemSelectedImages'] = {}
        self.MainFrame.descriptionTextField.SetValue("")
        self.MainFrame.descriptionTextField.Clear()
        self.MainFrame.jNumber = self.MainFrame.defaultJNumber
        self.MainFrame.descriptionTextField.SetValue(self.MainFrame.defaultJNumberInfo['description'])
        self.MainFrame.currentItemInfo = self.MainFrame.defaultJNumberInfo
        self.MainFrame.scanNumberText.Clear()
        self.MainFrame.ebayCategoryIdText.Clear()
        self.MainFrame.upcNumberText.Clear()
        self.MainFrame.upcNumberLbl.Hide()
        self.MainFrame.upcNumberText.Hide()

        self.MainFrame.imageCountLbl.SetLabel('Images Selected: '+str(len(self.MainFrame.currentItemInfo['itemSelectedImages'])))
        self.MainFrame.scanNumberText.SetFocus()
        self.MainFrame.mainSizer.Fit(self.MainFrame)
        self.MainFrame.mainPanel.Layout()
        self.MainFrame.mainPanel.Refresh()
        return