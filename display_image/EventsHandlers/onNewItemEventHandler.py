    def onNewItemButton(self, event):
        '''
        Clear the frame/screen and begin process for new item
        '''
        #import pdb; pdb.set_trace()
        if MainFrame.starterImagePath in MainFrame.currentImagePath:
            tmp_dialog = wx.MessageDialog(MainFrame, 'No Item was loaded? Pizza?', 'ValueError', wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        print('\n# PhotoCtrlEventsHandler: onNewItemButton: #')
        print('. Beginning Save(MainFrame.__dict__)')
        Save(MainFrame.__dict__)
        print('\n# PhotoCtrlEventsHandler: onNewItemButton: #')
        try:
            MainFrame.nextSkuNumber = str(int(MainFrame.currentSkuText.GetValue()) + 1).zfill(4)
        except ValueError, e:
            int_dialog = wx.MessageDialog(MainFrame, 'Sku was not entered', 'ValueError', wx.OK)
            results = int_dialog.ShowModal()
            int_dialog.Destroy()
            MainFrame.startingSkuLbl.SetLabel('Current Sku')
            MainFrame.currentSkuText.SetValue('HALP!')
            return
        # check which action needs to be taken
        if MainFrame.lookupManifestedRadio.GetValue() is True:
            results = MainFrame.csvTextReader.checkIfManifested(MainFrame.itemNumber, MainFrame.palletNumber)
            MainFrame.statusbar.SetStatusText(str(results))
            self.palletNumber = MainFrame.palletNumberText.GetValue()
            self.currentSkuText = MainFrame.currentSkuText.GetValue()
            if MainFrame.fingerRadio.GetValue() is True:
                if len(MainFrame.palletNumberText.GetValue()) is 0:
                    tmp_dialog = wx.MessageDialog(MainFrame, 'Pallet Number not entered.\n\nEnter a pallet number', 'ValueError', wx.OK)
                    results = tmp_dialog.ShowModal()
                    tmp_dialog.Destroy()
            if self.currentSkuText is "" or None:
                tmp_dialog = wx.MessageDialog(MainFrame, 'Sku was not entered', 'ValueError', wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
            # Begin lookup of item info.
            self.itemRow = MainFrame.csvTextReader.returnRow()
            print(self.itemRow)
        # begin manifesting action selected
        elif MainFrame.beginManifestingRadio.GetValue() is True:
            MainFrame.watchDictManifestResults['currentSku'] = str(int(MainFrame.currentSkuText.GetValue())).zfill(4)
            if MainFrame.fingerRadio.GetValue() is True:
                if len(MainFrame.palletNumberText.GetValue()) is 0:
                    tmp_dialog = wx.MessageDialog(MainFrame, 'Pallet Number not entered.\n\nEnter a pallet number', 'ValueError', wx.OK)
                    results = tmp_dialog.ShowModal()
                    tmp_dialog.Destroy()
                    return
                else:
                    MainFrame.watchDictManifestResults['palletNumber'] = MainFrame.palletNumberText.GetValue()
                    MainFrame.watchDictManifestResults['upc'] = MainFrame.upcNumberText.GetValue()
                    titles = MainFrame.csvTextWriter.returnTitlesForJnumber(MainFrame.watchDictManifestResults)
            elif MainFrame.shopHqRadio.GetValue() is True:
                MainFrame.watchDictManifestResults['palletNumber'] = MainFrame.palletNumberText.GetValue()
                titles = MainFrame.csvTextWriter.returnTitlesForJnumber(MainFrame.watchDictManifestResults)
            MainFrame.currentTitleList = titles

            if len(MainFrame.currentTitleList) is not 0:
                titleSelectionDialog = ReturnCorrectWatchTitle(None, -1,title='Select the correct Title')
                titleSelectionDialog.ShowModal()
                MainFrame.watchDictManifestResults['titleModelSelection'] = titleSelectionDialog.title_and_row_index
            else:
                tmp_dialog = wx.MessageDialog(MainFrame, 'HUB ASB HOON SHON!!\n\nTHIS ITEM NUMBER IS NOT IN TH MANIFEST\nAppending to end of file', 'ValueError', wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                MainFrame.watchDictManifestResults['titleModelSelection'] = str('row_index:' + str(1) + ':' + '#TITLE HERE#')

            results = MainFrame.csvTextWriter.writeManifestedRow(MainFrame.watchDictManifestResults)
            print results
            if results[0] is 13:
                print results
                print 'caught error'
                tmp_dialog = wx.MessageDialog(MainFrame, 'ERROR:\n\nFile is currently open in another program?\n\n'+results[1], 'IOError', wx.OK)
                tmp_selection = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                return
        print('\n# Clearing MainFrame #')
        MainFrame.startingSkuLbl.SetLabel('Current Sku')
        MainFrame.currentSkuText.SetValue(MainFrame.nextSkuNumber)
        MainFrame.currentImagePath = MainFrame.starterImagePath
        img = wx.Image(MainFrame.starterImagePath, wx.BITMAP_TYPE_ANY)
        MainFrame.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        MainFrame.browseText.SetValue("")
        MainFrame.currentItemInfo['itemSelectedImages'] = {}
        MainFrame.descriptionTextField.SetValue("")
        MainFrame.scanNumberText.SetValue("")
        MainFrame.ebayCategoryIdText.SetValue("")
        MainFrame.imageCountLbl.SetLabel('Images Selected: '+str(len(MainFrame.currentItemInfo['itemSelectedImages'])))
        MainFrame.statusbar.SetStatusText('Ready.                                   Last Scan:'+str(MainFrame.watchDictManifestResults['titleModelSelection']))
        MainFrame.mainPanel.Layout()
        MainFrame.scanNumberText.SetFocus()
        return