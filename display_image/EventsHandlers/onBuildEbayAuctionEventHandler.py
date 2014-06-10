    def onBuildEbayAuction(self, event):
        '''
        Builds ebay auction from json? Generates and appends it to a ebay verification
        csv file. ?
        '''
        print('\n# PhotoCtrlEventsHandler.onBuildEbayAuction(): #')
        sku = MainFrame.currentSkuText.GetValue()
        palletNumber = MainFrame.palletNumberText.GetValue()
        initials = MainFrame.listerInitialsText.GetValue()
        beginShelfNumber = MainFrame.beginShelfNumberText.GetValue()
        ebayCategoryId = MainFrame.ebayCategoryIdText.GetValue()
        print('. '+str(MainFrame.currentItemInfo))
        if '#REQUIRED' in ebayCategoryId:
            tmp_dialog = wx.MessageDialog(MainFrame, 'Please fill in the Ebay Category ID.\n\n This means that this item has not been seen before and is not located in the unique_category_4numbeer_sku.csv file... jeez i need to rename this file to something useful...', 'Not Seen Before', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        if len(sku) is 0:
            tmp_dialog = wx.MessageDialog(MainFrame, 'CurrentSkuText is empty.\n\nFill it in.', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        if len(beginShelfNumber) is 0:
            tmp_dialog = wx.MessageDialog(MainFrame, 'Beginning Shelf Number is empty..\n\nFill it in.', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        if len(palletNumber) is 0:
            tmp_dialog = wx.MessageDialog(MainFrame, 'palletNumber is empty.\n\nFill it in.', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        if len(initials) is 0:
            tmp_dialog = wx.MessageDialog(MainFrame, 'Initials is empty.\n\nFill it in.', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        # not paranoid ... just good enough for what needs to be done
        sources = MainFrame.currentItemInfo['itemSelectedImages']
        MainFrame.currentItemInfo['image_sources'] = {}
        MainFrame.currentItemInfo['image_sources'].update(sources)
        print(sources)

        # with ebay archive open return item specifics for jnumber
        # returns item_category, item_specifics from sky_manifest.returnItemSpecifics()
        #
        MainFrame.itemSpecifics = MainFrame.itemSpecificsFetcher.returnItemSpecifics(MainFrame.scanNumberText.GetValue())
        print('# MainFrame.itemSpecifics onBuildEbayAuction(): ' +str(MainFrame.itemSpecifics))
        MainFrame.ebayCategoryIdLbl.Show()
        MainFrame.ebayCategoryIdText.Show()
        MainFrame.mainPanel.Fit()
        MainFrame.mainPanel.Layout()
        # if item is not in ebay archive itemSpecifics 'ValueError' will be in item
        try:
            int_ebay_category = int(MainFrame.ebayCategoryIdText.GetValue())
        except:
            pass
        if 'ValueError' in MainFrame.itemSpecifics:
            # ebayCategoryIdText is empty notify user and set MainFrame.itemSpecifics to '#REQUIRED'
            # build auction pressed and ebay category is empty
            if len(MainFrame.ebayCategoryIdText.GetValue()) is 0:
                tmp_dialog = wx.MessageDialog(MainFrame, 'Item not seen before.\n\nUnable to determine category number, or item_specifics', 'ValueError', style=wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                MainFrame.itemSpecifics = '#REQUIRED'
                MainFrame.ebayCategoryIdText.SetValue(MainFrame.itemSpecifics)
                return
            # build auction was pressed but ebay category was not filled in
            elif '#REQUIRED' in MainFrame.ebayCategoryIdText.GetValue():
                tmp_dialog = wx.MessageDialog(MainFrame, 'Please fill in currentEbayCategoryId', 'ValueError', style=wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
            # ValueError, but category number has been entered
            elif isinstance(int_ebay_category, int):
                tmp_dialog = wx.MessageDialog(MainFrame, 'Item not seen before.\n\nUnable to determine category number, or item_specifics. Building without specifics.', 'ValueError', style=wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                results = ['']
                self.currentItemSpecificsDict = results # [item_category, [item_specifics]] sky_manifest.returnItemSpecifcs()
                MainFrame.currentItemSpecificsDict = self.currentItemSpecificsDict
            else:
                print('item specifics issue')
                tmp_dialog = wx.MessageDialog(MainFrame, 'Item not seen before.\n\nUnable to determine category number, or item_specifics', 'ValueError', style=wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                import pdb; pdb.set_trace()
                return
        # if item in archive retrieve it and get title
        if 'ValueError' not in MainFrame.itemSpecifics:
            # ebay category is a number and is filled in.
            if isinstance(int_ebay_category, int):
                results = ItemSpecificsDialog(None, -1,title='Please Fill In The Item Specifics')
                if results.ShowModal() == wx.ID_OK:
                    self.currentItemSpecificsDict = results.currentItemSpecificsDict # [item_category, [item_specifics]]
                    MainFrame.currentItemSpecificsDict = self.currentItemSpecificsDict
                    results.Destroy()
                print('. Item Specifics:'+str(self.currentItemSpecificsDict))


        MainFrame.listingSku = '-'.join([str(sku), str(palletNumber), str(beginShelfNumber), str(initials)])
        buildAuction = BuildAuction(MainFrame.currentItemInfo, MainFrame.listingSku, self.currentItemSpecificsDict, MainFrame.ebayAuctionHeaders, MainFrame.listingPreferencesResults)
        MainFrame.ebayListingHtml = buildAuction.returnHtmlStringForListing()

        MainFrame.ebayCsvFp = buildAuction.generateEbayListingCsvLine()
        if 'IOError' in MainFrame.ebayCsvFp:
            tmp_dialog = wx.MessageDialog(MainFrame, 'Is the file open bro?', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return

        # begin ssh dialog
        if MainFrame.ssh_pass is None:
            tmp_dialog = wx.PasswordEntryDialog(MainFrame, 'SSH Transfer: Please enter the server password ', 'Password', style=wx.OK)
            tmp_dialog.ShowModal()
            MainFrame.ssh_pass =  tmp_dialog.GetValue()
            tmp_dialog.Destroy()
            if len(MainFrame.ssh_pass) is 0:
                tmp_dialog = wx.MessageDialog(MainFrame, 'No password was entered', 'Password', style=wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
        results = MainFrame.ssh.putFiles(sources, MainFrame.listingSku, MainFrame.ebayListingHtml, MainFrame.currentItemInfo)
        if results is True:
             MainFrame.statusbar.SetStatusText('Transfer Successful.')
             tmp_dialog = wx.MessageDialog(MainFrame, 'Nice!\n\nTODO:Now clear the screen and move to next.', 'Nice!', style=wx.OK)
             results = tmp_dialog.ShowModal()
             tmp_dialog.Destroy()

        # set and clear
        MainFrame.currentImagePath = MainFrame.starterImagePath
        img = wx.Image(MainFrame.starterImagePath, wx.BITMAP_TYPE_ANY)
        MainFrame.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        MainFrame.browseText.SetValue("")
        MainFrame.currentItemInfo['itemSelectedImages'] = {}
        MainFrame.descriptionTextField.Clear()
        MainFrame.scanNumberText.SetValue("")
        MainFrame.prevListingSku = MainFrame.listingSku
        MainFrame.imageCountLbl.SetLabel('Images Selected: '+str(len(MainFrame.currentItemInfo['itemSelectedImages'])))
        MainFrame.currentSkuText.SetValue("")
        MainFrame.ebayCategoryIdText.SetValue("")
        MainFrame.statusbar.SetStatusText('Ready.                                   Last Uploaded:'+str(MainFrame.prevListingSku))
        MainFrame.currentSkuText.SetFocus()

        try:
            MainFrame.rSizer.Hide(MainFrame.rSizerCurrentItemSizer)
        except AttributeError, e:
            print(traceback.format_exc())
            print(e)
        MainFrame.mainPanel.Fit()
        MainFrame.mainPanel.Refresh()

        MainFrame.currentItemInfo = {}

        return