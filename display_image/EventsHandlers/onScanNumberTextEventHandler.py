    def onScanNumberText(self, event):
        '''
        onScanNumberText checks retailer jnumber type and updates MainFrame
        to display the current item info. Whether from json, or as a first item
        '''
        print('\n# PhotoCtrlEventHandler.scanNumberText() #')
        self.palletNumber = MainFrame.palletNumberText.GetValue()
        if len(self.palletNumber) is 0:
            tmp_dialog = wx.MessageDialog(MainFrame, 'palletNumber is empty.\n\nFill it in.', 'UserError', style=wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        MainFrame.itemNumber = MainFrame.scanNumberText.GetValue().split('-')[0].upper()
        MainFrame.currentItemInfo['itemNumber'] = MainFrame.itemNumber
        MainFrame.statusbar.SetStatusText('scanNumberText: '+ MainFrame.itemNumber)
        self.itemNumber = MainFrame.itemNumber

        # Check if the wrong retailerRadio
        if (( '4' not in self.itemNumber[0]) or ( 'J' not in self.itemNumber[0])) is False :
            MainFrame.statusbar.SetStatusText('I dont understand:' + MainFrame.currentItemInfo['itemNumber'] + ' Maybe it should start with a J or a 4?')
            tmp_dialog = wx.MessageDialog(MainFrame, 'ERROR: Please enter a Jnumber or a 4number.\n\nEntered:' + str(self.itemNumber)+'\n\nexamples. J123456 or 4NK420000001', 'UserError', wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        if 'J' in self.itemNumber[0]:
            MainFrame.statusbar.SetStatusText('I see a Jnumber')
            if MainFrame.fingerRadio.GetValue() is True:
                    tmp_dialog = wx.MessageDialog(MainFrame, 'ERROR: Please select ShopHQ Radio button for: ' + str(self.itemNumber) + '\n\nCurrent selection: FingerHut', 'UserError', wx.OK)
                    results = tmp_dialog.ShowModal()
                    tmp_dialog.Destroy()
                    return
        elif '4' in self.itemNumber[0]:
            MainFrame.statusbar.SetStatusText(' I see a 4number')
            if MainFrame.shopHqRadio.GetValue() is True:
                    tmp_dialog = wx.MessageDialog(MainFrame, 'ERROR: Please select Fingerhut Radio button for:' + str(self.itemNumber) + '\n\nCurrent selection: ShopHQ', 'UserError', wx.OK)
                    results = tmp_dialog.ShowModal()
                    tmp_dialog.Destroy()
                    return

        # Check if action selected
        if MainFrame.lookupManifestedRadio.GetValue() is True:
            results = MainFrame.csvTextReader.checkIfManifested(self.itemNumber, self.palletNumber)
            if isinstance(results, dict):
                MainFrame.statusbar.SetStatusText('Found item dictionary.')
            else:
                MainFrame.statusbar.SetStatusText(str(results))
        elif MainFrame.beginManifestingRadio.GetValue() is True:
            print('. PhotoCtrlEventsHandler.onScanNumberText(): Updating watchDictManifestResults.')
            results = MainFrame.csvTextReader.checkIfManifested(self.itemNumber, self.palletNumber)
            if 'exceptions.ValueError' in results:
                print results
                MainFrame.statusbar.SetStatusText(str(results))
                return
            elif 'ERROR: Wrong retailer_code for jnumber/4number entered' in results:
                tmp_dialog = wx.MessageDialog(MainFrame, results+'\n\nCheck Cell A1 in csv. Format: \"retailer_code:#\"', 'UserError', wx.OK)
                results = tmp_dialog.ShowModal()
                tmp_dialog.Destroy()
                MainFrame.statusbar.SetStatusText(str(results))
                return
            elif isinstance(results, dict):
                MainFrame.statusbar.SetStatusText('Found item dictionary.')
                MainFrame.watchDictManifestResults = results
            else:
                print('help')
                print(results)
                exit()
        else:
            tmp_dialog = wx.MessageDialog(MainFrame, 'No action was selected:\n\n *Begin Manifesting\n    or\n *Lookup Manifested Item', 'UserError', wx.OK)
            results = tmp_dialog.ShowModal()
            tmp_dialog.Destroy()
            return
        # fingerhut
        if MainFrame.fingerRadio.GetValue() is True:
            check = Check(None)
            check.storeRadioSelection()
            MainFrame.itemFolder = os.path.join('item_number_pages', MainFrame.itemNumber[1:6])
            MainFrame.currentItemInfo['itemFolder'] = MainFrame.itemFolder
            self.itemFolder = MainFrame.itemFolder
            # check json
            self.updateCurrentItemInfo()

            json_check = Check(MainFrame.currentItemInfo)
            json_results = json_check.loadMainFrameJson()
            if json_results is True:
                MainFrame.statusbar.SetStatusText('Found json_state_file.')
                self.prev_image_check = Check(MainFrame.currentItemInfo)
                self.prev_image = self.prev_image_check.defaultImageSelections()
                print('\n# PhotoCtrlEventHandler.onScanNumberText(): self.prev_image #')
                print('. Previous Images: ')
                print('. '+str(MainFrame.currentItemInfo['itemSelectedImages']))
                MainFrame.imageCountLbl.SetLabel('Images Selected: '+str(len(MainFrame.currentItemInfo['itemSelectedImages'])))
                print(('. ' + str(self.prev_image)))
                self.img_path = self.prev_image

                print('. Found Previous Image Selection: '+str(self.img_path))
                if "None" in str(self.img_path):
                    results = getFingerHutProductInfo(self.itemNumber)
                    itemResults = Check(results)
                    self.img_name = itemResults.guessImageName(self.itemNumber).split('?')[0]+'.JPEG'
                    self.img_path = os.path.join(self.itemFolder,self.img_name)
            # if no json, go get it
            else:
                MainFrame.statusbar.SetStatusText('Didnt find json_state_file.')
                try:
                    results = getFingerHutProductInfo(self.itemNumber)
                except IndexError, e:
                    int_dialog = wx.MessageDialog(MainFrame, 'Page not found for: ' + str(self.itemNumber), 'IndexError', wx.OK)
                    results = int_dialog.ShowModal()
                    int_dialog.Destroy()
                MainFrame.currentItemInfo.update(results)
                try:
                    itemResults = Check(results)
                    MainFrame.statusbar.SetStatusText('Getting images')
                    images = itemResults.downloadImages()
                    MainFrame.statusbar.SetStatusText('Done Getting images')
                    p = Process(target=images, args=())
                    p.start()
                    p.join()
                except Exception:
                    print(traceback.format_exc())
                # itemResults = Check(results)
                self.img_name = itemResults.guessImageName(self.itemNumber).split('?')[0]+'.JPEG'
                self.img_path = os.path.join(self.itemFolder, results['image_list'][0] + '.JPEG')
                MainFrame.currentImagePath = self.img_path
                MainFrame.currentItemInfo['description'] = itemResults.description()
        # shophq
        if MainFrame.shopHqRadio.GetValue() is True:
            check = Check(None)
            check.storeRadioSelection()
            self.itemNumber = MainFrame.scanNumberText.GetValue().split('-')[0]
            MainFrame.itemNumber = self.itemNumber
            MainFrame.itemFolder = os.path.join('item_number_pages', self.itemNumber)
            # check json updates MainFrame.currentItemInfo
            json_check = Check(MainFrame.currentItemInfo)
            json_results = json_check.loadMainFrameJson()
            if json_results is True:
                self.prev_image_check = Check(MainFrame.currentItemInfo)
                self.prev_image = self.prev_image_check.defaultImageSelections()
                print('\n# PhotoCtrlEventHandler.onScanNumberText(): self.prev_image #')
                print(self.prev_image)
                self.img_path = self.prev_image
                print('. Found Previous Image Selection: '+str(self.img_path))
                if "None" in str(self.img_path):
                    results = getShopHqProductInfo(self.itemNumber)
                    itemResults = Check(results)
                    self.img_name = itemResults.guessImageName(self.itemNumber).split('?')[0]+'.JPEG'
                    self.img_path = os.path.join(MainFrame.itemFolder,self.img_name)
            # if no json, go get it
            else:
                try:
                    results = getShopHqProductInfo(MainFrame.itemNumber)
                except IndexError, e:
                    int_dialog = wx.MessageDialog(MainFrame, 'Page not found for: ' + str(self.itemNumber), 'IndexError', wx.OK)
                    results = int_dialog.ShowModal()
                    int_dialog.Destroy()
                MainFrame.currentItemInfo.update(results)
                self.itemFolder = MainFrame.itemFolder
                try:
                    itemResults = Check(results)
                    images = itemResults.downloadImages()
                    MainFrame.statusbar.SetStatusText('Done Getting images')
                    p = Process(target=images, args=())
                    p.start()
                    p.join()
                except Exception:
                    print(traceback.format_exc())
                self.img_name = itemResults.guessImageName(self.itemNumber).split('?')[0]+'.JPEG'
                self.img_path = os.path.join(self.itemFolder,self.img_name)
                MainFrame.currentImagePath = self.img_path
                # itemResults = Check(results)

                MainFrame.currentItemInfo['description'] = itemResults.description()
        # update variables and mainframe
        self.description = MainFrame.currentItemInfo['description']
        img = wx.Image(self.img_path, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = MainFrame.PhotoMaxSize
            NewH = MainFrame.PhotoMaxSize * H / W
        else:
            NewH = MainFrame.PhotoMaxSize
            NewW = MainFrame.PhotoMaxSize * W / H
        img = img.Scale(NewW, NewH)

        MainFrame.currentImagePath = self.img_path
        MainFrame.descriptionTextField.Clear()

        try:
            MainFrame.descriptionTextField.AppendText(self.description.decode('utf8'))
        except UnicodeEncodeError, e:
            MainFrame.descriptionTextField.AppendText(self.description)
        try:
            MainFrame.ebayCategoryIdLbl.Show()
            MainFrame.ebayCategoryIdText.Show()
            MainFrame.ebayCategoryIdText.SetValue("")
            MainFrame.ebayCategoryIdText.AppendText(MainFrame.currentItemInfo['ebay_category'])
        except Exception, e:
            MainFrame.ebayCategoryIdLbl.Hide()
            MainFrame.ebayCategoryIdText.Hide()
            print(e)
            print(traceback.format_exc())
        MainFrame.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        MainFrame.mainPanel.Refresh()
        MainFrame.statusbar.SetStatusText('Item Loaded:'+ MainFrame.currentItemInfo['itemFolder'])
        return