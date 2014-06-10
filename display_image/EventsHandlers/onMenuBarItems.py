    def onPdbSetTrace(self, event):
        '''
        Help Menu pdb set trace for variable debugging
        '''
        import pdb;pdb.set_trace()
        return
        

    def onPrefetch(self, event):
        '''
        Start Prefetch thread
        '''
        filenames = self.csvFileBrowse()
        prefetcher = PreFetcher(filenames)
        for status in prefetcher.run():
            wx.Yield()
            MainFrame.statusbar.SetStatusText(status)
            
    def onListingPreferencesMenu(self, event):
        '''
        Starts ListingPreferencesDialog
        '''
        results = ListingPreferencesDialog(None, -1,title='Listing Preferences')
        if results.ShowModal() == wx.ID_OK:
            MainFrame.settingsDict = results.settings_dict
            results.Destroy()
        print MainFrame.settingsDict
        return
        
    def onLoadManifest(self, event):
        '''
        onLoadManifest() Loads manifest into seperate window to begin manifesting?
        '''
        print('\n# PhotoCtrlEventsHandler.onLoadManifest(): #')
        print('Loading Manifest')
        # sky_manifest.ManifestReader(filename)
        return