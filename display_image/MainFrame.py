# -*- coding: utf8 -*-
# James Munsch
# http://jamesmunsch.com/
# james.a.munsch@gmail.com
import wx, urllib2, os
import difflib
import json
from PIL import Image
from PIL import ImageEnhance
from multiprocessing import Process
from EventsHandlers.MainFrameEventHandler import MainFrameEventHandler
from Ssh_Put import Ssh
import sky_manifest
import traceback
from Dialogs.ListingPreferencesDialog import ListingPreferencesDialog
from Dialogs.ListingPreferencesDialog import  CheckListingPreferences
from Check import Check
import logging
from logs.logger_example import log_this
import sys
import yaml
from logs.log_queue import logQueue


class MainFrame(wx.Frame):
    '''
    MainFrame class takes wx.Frame and initializes panel and widgets
    This class generates a window that includes a picture of the item,
    description of the item, and other item specifics.
    '''
    def __init__(self, parent, title):
        self.threading = False
        self.logger = log_this(__name__, self)
        wx.Frame.__init__(self, parent, title=title)
        self.mainPanel = wx.Panel(self)
        # self.Maximize()
        with open('config.yaml','r') as f:
            self.defaults = yaml.load(f)
        self.currentItemInfo = self.defaults['currentItemInfo']
        self.defaultJNumber = self.defaults['defaultJNumber']
        self.defaultJNumberInfo = self.defaults['defaultJNumberInfo']
        self.jNumber = self.defaults['defaultJNumber']
        self.PhotoMaxSize = self.defaults['PhotoMaxSize']
        self.defaultJPagesFolder = os.path.join(self.defaults['displayImageFolder'], self.defaults['jPages'])
        self.jNumberFolderPath = os.path.join(self.defaultJPagesFolder, self.defaults['jNumberFolder'])
        self.defaultJNumberFolder = os.path.join(self.defaultJPagesFolder, self.defaults['defaultJNumber'])
        self.defaultImgPath = os.path.join(self.defaultJNumberFolder, self.defaults['defaultJNumberInfo']['image_list'][0] + '.JPEG')
        self.currentImgPath = self.defaultImgPath
        self.archivedDataFolderPath = os.path.join(self.defaults['displayImageFolder'], self.defaults['archivedData'])
        self.uniqueCategoryArchive = os.path.join(self.archivedDataFolderPath, self.defaults['lookUpTable'])
        self.itemSpecificsFetcher = sky_manifest.ManifestReader(self.uniqueCategoryArchive, self)
        self.ebayHeadersFile = os.path.join(self.archivedDataFolderPath, self.defaults['ebayHeaderFile'])
        self.ebayAuctionHeaders = sky_manifest.ManifestReader(self.ebayHeadersFile, self).returnTitleHeaders()
        self.scanNumberTextValue = None
        self.sky_manifest = sky_manifest
        self.eventsHandler = MainFrameEventHandler(self)
        self.ssh_pass = self.defaults['ssh_pass']
        self.ssh = Ssh(self)
        #--------------------------------------
        # check if listing preferences exists
        #--------------------------------------
        self.listingPreferences = CheckListingPreferences(self)
        self.listingPreferencesResults = self.listingPreferences.check()
        #-----------------------------
        # set mainframe for listing preferences dialog
        #-----------------------------
        self.ListingPreferencesDialog = ListingPreferencesDialog
        
        if self.listingPreferencesResults is False:
            self.results = self.ListingPreferencesDialog(None, -1,title='Listing Preferences')
            self.results.setMainFrame(self)
            self.results.Show()
            if self.results.ShowModal() == wx.ID_OK:
                self.listingPreferencesResults = self.results.settings_dict
                self.results.Destroy()
        self.createWidgets()
        self.Show()

    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return
    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+this_function_name,debug_info)
        return

    def lsizerCreate(self):
        '''
        # PhotoCtrl lsizer
        # listerInitials = self.defaults['listerInitials']
        # beginShelf = self.defaults['defaultShelf']
        #####################
        '''
        #self.logger.autolog("im in lsizerCreate")
        self.logger.log_info(self.lsizerCreate.__name__,"THIS IS A MESSAGE IN lsizerCreate")
        self.emptyRadio = wx.RadioButton(self.mainPanel, id=wx.ID_ANY, label='', style=wx.RB_GROUP)
        self.emptyRadio.Hide()
        self.beginManifestingRadio = wx.RadioButton(self.mainPanel, id=wx.ID_ANY, label='Begin Manifesting')
        self.beginManifestingRadio.SetValue(False)
        self.beginManifestingRadio.Bind(wx.EVT_RADIOBUTTON, self.eventsHandler.onBeginManifestingRadio)
        self.lookupManifestedRadio = wx.RadioButton(self.mainPanel, id=wx.ID_ANY, label='Lookup Manifested Item')
        self.lookupManifestedRadio.Bind(wx.EVT_RADIOBUTTON, self.eventsHandler.onLookupManifestedRadio)
        self.actionSeperator = wx.StaticLine(self.mainPanel, wx.ID_ANY, style=wx.LI_HORIZONTAL)

        self.retailerLbl = wx.StaticText(self.mainPanel, label='Retailer:Code')
        self.fingerRadio = wx.RadioButton(self.mainPanel, id=wx.ID_ANY, label='FingerHut:0', style=wx.RB_GROUP)
        self.fingerRadio.Bind(wx.EVT_RADIOBUTTON, self.eventsHandler.onRetailerRadio)
        self.shopHqRadio = wx.RadioButton(self.mainPanel, id=wx.ID_ANY, label='ShopHQ:1')
        self.shopHqRadio.Bind(wx.EVT_RADIOBUTTON, self.eventsHandler.onRetailerRadio)

        self.palletNumberLbl = wx.StaticText(self.mainPanel, label='Pallet Number')
        self.palletNumberText = wx.TextCtrl(self.mainPanel, size=(120, -1))
        self.palletNumberText.Bind(wx.EVT_TEXT, self.eventsHandler.onPalletNumberText)
        self.scanNumberLbl = wx.StaticText(self.mainPanel, label='Scan Number (Press Enter to Load)')
        self.scanNumberText = wx.TextCtrl(self.mainPanel, size=(120, -1), style=wx.TE_PROCESS_ENTER)
        self.scanNumberText.Bind(wx.EVT_TEXT_ENTER, self.eventsHandler.onScanNumberText)
        self.scanNumberSeperator = wx.StaticLine(self.mainPanel, wx.ID_ANY, style=wx.LI_HORIZONTAL)
        self.startingSkuLbl = wx.StaticText(self.mainPanel, label='Enter the starting Sku# (i.e. 0001)')
        self.currentSkuText = wx.TextCtrl(self.mainPanel, size=(60,-1))
        self.currentSkuText.Bind(wx.EVT_TEXT, self.eventsHandler.onCurrentSkuText)
        self.lookUpBySkuBtn = wx.Button(self.mainPanel, label='Look Up By Sku')
        self.lookUpBySkuBtn.Bind(wx.EVT_BUTTON, self.eventsHandler.onLookUpBySkuBtn)
        self.upcNumberLbl = wx.StaticText(self.mainPanel, label='upc number')
        self.upcNumberText = wx.TextCtrl(self.mainPanel, size=(130, -1), style=wx.TE_PROCESS_ENTER)
        self.upcNumberText.Bind(wx.EVT_TEXT, self.eventsHandler.onUpcNumberText)
        self.beginShelfNumberLbl = wx.StaticText(self.mainPanel, label='Beginning Shelf')
        self.beginShelfNumberText = wx.TextCtrl(self.mainPanel, size=(70, -1))
        self.beginShelfNumberText.Bind(wx.EVT_TEXT, self.eventsHandler.onbeginShelfNumberText)
        self.ebayCategoryIdLbl = wx.StaticText(self.mainPanel, label='Ebay Category ID')
        self.ebayCategoryIdText = wx.TextCtrl(self.mainPanel, size=(120, -1))
        self.ebayCategoryIdText.Bind(wx.EVT_TEXT, self.eventsHandler.onEbayCategoryIdText)
        self.listerInitialsLbl = wx.StaticText(self.mainPanel, label='Your Initials')
        self.listerInitialsText = wx.TextCtrl(self.mainPanel, size=(30, -1), style=wx.TE_PROCESS_ENTER)
        self.listerInitialsText.Bind(wx.EVT_TEXT, self.eventsHandler.onListerInitialsText)
        self.buildAuctionButton = wx.Button(self.mainPanel, label='&Build Ebay Auction')
        self.buildAuctionButton.Bind(wx.EVT_BUTTON, self.eventsHandler.onBuildEbayAuction)


        self.newItemButton = wx.Button(self.mainPanel, label='Scan &New Item')
        self.newItemButton.Bind(wx.EVT_BUTTON, self.eventsHandler.onNewItemButton)

        self.lSizer = wx.BoxSizer(wx.VERTICAL)
        self.lookUpBySkuSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.lSizer.Add(self.beginManifestingRadio, 0, wx.ALL, 5)
        self.lSizer.Add(self.lookupManifestedRadio, 0, wx.ALL, 5)
        self.lSizer.Add(self.actionSeperator, 0, wx.ALL | wx.EXPAND, 5)
        self.lSizer.Add(self.retailerLbl, 0, wx.ALL, 5)
        self.lSizer.Add(self.fingerRadio, 0, wx.ALL, 5)
        self.lSizer.Add(self.shopHqRadio, 0, wx.ALL, 5)
        self.lSizer.Add(self.palletNumberLbl, 0, wx.ALL, 5)
        self.lSizer.Add(self.palletNumberText, 0, wx.ALL, 5)
        self.lSizer.Add(self.scanNumberLbl, 0, wx.ALL, 5)
        self.lSizer.Add(self.scanNumberText, 0, wx.ALL, 5)
        self.lSizer.Add(self.scanNumberSeperator, 0, wx.ALL | wx.EXPAND, 5)
        self.lSizer.Add(self.startingSkuLbl, 0, wx.ALL, 5)
        self.lookUpBySkuSizer.Add(self.currentSkuText, 0, wx.ALL, 5)
        self.lookUpBySkuSizer.Add(self.lookUpBySkuBtn, 0, wx.ALL, 5)

        self.lSizer.Add(self.lookUpBySkuSizer, 0, wx.ALL, 5)
        self.lSizer.Add(self.upcNumberLbl, 0, wx.ALL, 5)
        self.lSizer.Add(self.upcNumberText, 0, wx.ALL, 5)
        self.lSizer.Add(self.ebayCategoryIdLbl, 0, wx.ALL, 5)
        self.lSizer.Add(self.ebayCategoryIdText, 0, wx.ALL, 5)
        self.lSizer.Add(self.beginShelfNumberLbl , 0, wx.ALL, 5)
        self.lSizer.Add(self.beginShelfNumberText , 0, wx.ALL, 5)
        self.beginShelfNumberText.SetValue(self.defaults['defaultShelf'])

        self.lSizer.Add(self.listerInitialsLbl, 0, wx.ALL, 5)
        self.lSizer.Add(self.listerInitialsText, 0, wx.ALL, 5)
        self.listerInitialsText.SetValue(self.defaults['listerInitials'])
        self.lSizer.Add(self.newItemButton, 0, wx.ALL, 5)
        self.lSizer.Add(self.buildAuctionButton, 0, wx.ALL, 5)
        return

    def csizerCreate(self):
        '''
        ####################################
        # cSizer photo txt and browse Button
        #
        #
        ####################################
        '''
        self.logger.log_info(self.csizerCreate.__name__,"THIS IS A MESSAGE in csizerCreate")
        if self.defaultImgPath is not None:
            try:
                img = wx.Image(self.defaultImgPath, wx.BITMAP_TYPE_ANY)
            except Exception, e:
                print("\n# PhotoCtrl: createWidgets(): csizer: img variable" + str(e))
                self.img_path = None
        if self.defaultImgPath is None:
            img = wx.EmptyImage(240, 240)
        self.imageCtrl = wx.StaticBitmap(self.mainPanel, wx.ID_ANY,
                                         wx.BitmapFromImage(img))
        self.imageCountLbl = wx.StaticText(self.mainPanel, label='')
        self.instructions = 'Is this image correct?'
        self.instructLbl = wx.StaticText(self.mainPanel, label=self.instructions)
        self.browseText = wx.TextCtrl(self.mainPanel, size=(200, -1))
        self.browseBtn = wx.Button(self.mainPanel, label='Browse')
        self.browseBtn.Bind(wx.EVT_BUTTON, self.eventsHandler.onBrowse)
        self.SelectImageBtn = wx.Button(self.mainPanel, label="Select Image Choices")
        self.SelectImageBtn.Bind(wx.EVT_BUTTON, self.eventsHandler.onSelectImageBtn)

        self.cSizer = wx.BoxSizer(wx.VERTICAL)
        self.cSizer.Add(self.instructLbl, 0, wx.ALL, 5)
        self.cSizer.Add(self.imageCtrl, 0, wx.ALL, 5)
        self.cSizer.Add(self.imageCountLbl,0,wx.ALL, 5)
        self.cSizer.Add(self.browseText, 0, wx.ALL, 5)
        self.cSizer.Add(self.browseBtn, 0, wx.ALL, 5)
        self.cSizer.Add(self.SelectImageBtn, 0, wx.ALL, 5)
        return

    def rsizerCreate(self):
        '''
        ###################################
        # rSizer Description Text
        #
        ## globals itemInfo, itemNumber
        ####################################
        '''
        self.logger.log_info(self.rsizerCreate.__name__,"THIS IS A MESSAGE in rsizerCreate")
        self.descriptionTextField = wx.TextCtrl(self.mainPanel, size=(300, 500),
                                         style=wx.TE_MULTILINE | wx.TE_RICH2)

        results = Check(self)
        description = results.description()
        self.descriptionTextField.AppendText(description)

        self.rSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rSizer.Add(self.descriptionTextField, 0, wx.ALL, 5)
        # Create Lbls/Text
        self.saveDescriptionTextBtn = wx.Button(self.mainPanel, label='Save Current')
        self.saveDescriptionTextBtn.Bind(wx.EVT_BUTTON,
                                self.eventsHandler.onSaveCurrentTextBtn)
        self.currentBoxLbl = wx.StaticText(self.mainPanel, label='Current Box')
        self.currentBoxText = wx.TextCtrl(self.mainPanel, size=(40,-1))
        self.currentConditionLbl = wx.StaticText(self.mainPanel, label='Condition 1-5')
        self.currentConditionText = wx.TextCtrl(self.mainPanel, size=(40,-1))
        self.currentConditionText.Bind(wx.EVT_TEXT, self.eventsHandler.onCurrentConditionText)
        self.currentConditionNotesLbl = wx.StaticText(self.mainPanel, label='Condition Notes')
        self.currentConditionNotesText = wx.TextCtrl(self.mainPanel, size=(120,40), style=wx.TE_MULTILINE)
        self.currentDateListedLbl = wx.StaticText(self.mainPanel, label='Date Listed')
        self.currentDateListedText = wx.TextCtrl(self.mainPanel, size=(60,-1))
        self.currentRepairLbl = wx.StaticText(self.mainPanel, label='Repair Date/Notes')
        self.currentRepairText = wx.TextCtrl(self.mainPanel, size=(60,-1))
        self.currentTitleLbl = wx.StaticText(self.mainPanel, label='Title')
        self.currentTitleText = wx.TextCtrl(self.mainPanel, size=(140,-1))
        self.currentTitleText.Bind(wx.EVT_TEXT, self.eventsHandler.onCurrentTitleText)
        # Create rSizerCurrentItemSizer add lbl/text
        self.rSizerCurrentItemSizer = wx.BoxSizer(wx.VERTICAL)
        self.rSizerCurrentItemSizer.Add(self.saveDescriptionTextBtn, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentBoxLbl, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentBoxText, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentConditionLbl, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentConditionText, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentConditionNotesLbl, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentConditionNotesText, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentDateListedLbl, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentDateListedText, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentRepairLbl, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentRepairText, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentTitleLbl, 0, wx.ALL, 5)
        self.rSizerCurrentItemSizer.Add(self.currentTitleText, 0, wx.ALL, 5)
        self.rSizer.Add(self.rSizerCurrentItemSizer)
        self.rSizer.Hide(self.rSizerCurrentItemSizer,recursive=True)

        return


    def createWidgets(self):
        '''
        creates/adds/appends/builds the widgets that are added to the
        mainPanels/frame/window of parent (photoctrl)
        '''

        ####################
        #
        # menubar
        #####################
        self.logger.log_info(self.createWidgets.__name__,"THIS IS A MESSAGE in CreateWidgets")
        self.file = wx.Menu()
        self.edit = wx.Menu()
        self.help = wx.Menu()

        self.loadManifest = wx.MenuItem(self.file,101, '&Load Manifest', 'Load a manifest into the scanner')
        self.Bind(wx.EVT_MENU, self.eventsHandler.onLoadManifest, self.loadManifest)
        self.file.AppendItem(self.loadManifest)
        self.fetchManifestItemInfo = wx.MenuItem(self.file, 102, '&PreFetch Manifest Items', 'Fetch all unseen items from online and stores them locally for faster lookup.')
        self.Bind(wx.EVT_MENU, self.eventsHandler.onPrefetch, self.fetchManifestItemInfo)
        self.file.AppendItem(self.fetchManifestItemInfo)
        self.file.AppendSeparator()

        self.resetSsh = wx.MenuItem(self.edit, 106, '&Reset SSH password', 'Resets SSH password to None')
        self.Bind(wx.EVT_MENU, self.ssh.resetPass, self.resetSsh)
        self.edit.AppendItem(self.resetSsh)
        self.listingPreferences = wx.MenuItem(self.edit,107, 'Listing &Preferences', 'Set Listing Preferences')
        self.Bind(wx.EVT_MENU, self.eventsHandler.onListingPreferencesMenu, self.listingPreferences)
        self.edit.AppendItem(self.listingPreferences)
        self.quit = wx.MenuItem(self.file, 105, '&Quit\tCtrl+Q', 'Quit the Application')
        self.Bind(wx.EVT_MENU, self.eventsHandler.onClose, self.quit)
        self.file.AppendItem(self.quit)

        self.pdbSetTrace = wx.MenuItem(self.help,201, '&PDB trace','starts pdb.set_trace() for variable debugging')
        self.Bind(wx.EVT_MENU, self.eventsHandler.onPdbSetTrace, self.pdbSetTrace)
        self.help.AppendItem(self.pdbSetTrace)
        self.reloadModules = wx.MenuItem(self.help,202, '&Reload Modules','reloads all of the current modules')
        self.Bind(wx.EVT_MENU, self.onReloadModules, self.reloadModules)
        self.help.AppendItem(self.reloadModules)

        menubar = wx.MenuBar()
        menubar.Append(self.file, '&File')
        menubar.Append(self.edit, '&Edit')
        menubar.Append(self.help, '&Help')
        self.SetMenuBar(menubar)
        self.statusbar = self.CreateStatusBar()

        self.lsizerCreate()
        self.csizerCreate()
        self.rsizerCreate()


        #################################
        # Add Widgets
        #
        #
        #########################
        #sizers
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(wx.StaticLine(self.mainPanel, wx.ID_ANY),
                           0, wx.ALL | wx.EXPAND, 5)

        #mainsizer add
        self.mainSizer.Add(self.lSizer, flag=wx.ALIGN_CENTER)
        self.mainSizer.Add(wx.StaticLine(self.mainPanel, wx.ID_ANY,
                                         style=wx.LI_VERTICAL),
                                         0, wx.ALL | wx.EXPAND, 5)
        self.mainSizer.Add(self.cSizer)  # flag=wx.ALIGN_CENTER)
        self.mainSizer.Add(self.rSizer)  # flag=wx.ALIGN_RIGHT)

        # hides
        self.scanNumberLbl.Hide()
        self.scanNumberText.Hide()
        self.lookUpBySkuBtn.Hide()
        self.upcNumberLbl.Hide()
        self.upcNumberText.Hide()
        self.ebayCategoryIdLbl.Hide()
        self.ebayCategoryIdText.Hide()
        self.beginShelfNumberLbl.Hide()
        self.beginShelfNumberText.Hide()
        self.buildAuctionButton.Hide()
        self.upcNumberLbl.Hide()
        self.upcNumberText.Hide()
        

        #Panel Layout
        self.mainPanel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)
        self.mainPanel.Layout()


    def onReloadModules(self, event):
        '''
        meant to reload the modules without having to close the program
        every time... but it doesn't work. So now it is a way to inspect
        MainFrame varibles from within MainFrame class.

        #import sky_manifest
        #import Ssh_Put
        #import EventsHandlers
        #import display_image
        #import Dialogs
        #import Check
        #import logs
        #Check = reload(Check)
        #Ssh_Put = reload(Ssh_Put)
        #Dialogs = reload(Dialogs)
        #display_image = reload(display_image)
        #sky_manifest = reload(sky_manifest)
        #logs = reload(logs)
        #EventsHandlers = reload(EventsHandlers)

        #from Check import Check
        #from Ssh_Put import Ssh
        #from Dialogs.ListingPreferencesDialog import ListingPreferencesDialog
        #from Dialogs.ListingPreferencesDialog import  CheckListingPreferences
        #from display_image.Check import Check
        #from logs.logger_example import log_this
        #from EventsHandlers.MainFrameEventHandler import MainFrameEventHandler


        self.infoLogger("Reloading modules")
        self.statusbar.SetStatusText("Reloaded Modules")
        '''

        import pdb;pdb.set_trace()

        return

# if run as main
def main():
    global MainFrame
    app = wx.App(False)
    MainFrame = PhotoCtrl(None, 'Sky Group Scanner')
    print('\n# main(): #\n' + 'MainFrame.__dict__.keys():\n' + str(MainFrame.__dict__.keys()))
    app.MainLoop()


if __name__ == '__main__':
    main()


