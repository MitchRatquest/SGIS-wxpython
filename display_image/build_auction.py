import os
import posixpath
import csv
from logs.logger_example import log_this
import sys

class BuildAuction(object):

    def __init__(self, currentItemInfo, listingSku, currentItemSpecificsDict, ebayAuctionHeaders, listingPreferences, MainFrame):
        super(BuildAuction, self).__init__()
        self.currentItemInfo = currentItemInfo
        self.listingSku = listingSku
        self.MainFrame = MainFrame
        self.currentItemSpecificsDict = currentItemSpecificsDict
        self.ebayAuctionHeaders = ebayAuctionHeaders
        self.listingPreferences = listingPreferences
        self.itemModifiedListingPreferencesDict = {}
        self.final_destination = None
        self.logger = log_this(__name__,self.MainFrame)

    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return
    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+" "+this_function_name,debug_info)
        return
    def returnHtmlStringForListing(self):
        '''
        Returns the listing html for an item
        Requires:
            title
            msrp
            image_list
        Quotes need to be returned as "" and not "
        Remove extraneous characters that may break the csv file? Commas quotes

        '''
        self.infoLogger("Inside: ")
        self.infoLogger("self.itemCurrentInfo: "+str(self.currentItemInfo))

        header_tags = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\" /></head><body style=\"font-family: Arial, Helvetica, sans-serif;\"><div align=\"center\"><img src=\"http://jamesmunsch.com/skygroup_test/p1p_1_88776_853759.jpg\"></img></div><div align=\"center\"><b>Point One Premiums is Committed to Providing a Positive Experiencefor our Customers<br>______________________________________________________________________<br></b><b></b></div><div align=\"center\"><b><br></b></div><div align=\"center\"><b>Business Hours: M-F 9am - 5pm CST</b></div><p align=\"center\">(Shipments &amp; Questions processed during Business Hours Only. Thanks.)</p><div align=\"center\"><b>____________________________________________________________________________</b></div>"
        title_tags = "<center><h1>"+self.currentItemInfo['title']+"</h1></center>"
        images_tags = ""
        images_tags += "<div align=\"center\"><br>"
        #import pdb;pdb.set_trace()
        for image in self.currentItemInfo['image_sources']:
            if 'True' in image: # images were selected
                continue
            else:
                filename = os.path.split(image)[-1]
            destinationFolder = self.listingSku
            destination = "http://"+self.MainFrame.defaults['extIP']
            final_path = posixpath.join(destination,destinationFolder)
            self.final_destination = posixpath.join(final_path, filename)
            images_tags += "<a href=\""+self.final_destination+"\"><img src=\""+self.final_destination+"\" height=\"400\" width=\"400\" ></a></br>"
        msrp_tags = "<div align=\"left\"><h4>Item normally retails for: "+self.currentItemInfo['msrp']+"</h4></div>"
        self.currentItemInfo['description'] = self.currentItemInfo['description'].split('<div class=\"panelDetail\" id=\"prod_description\">')[-1].split('<strong>Warranty:')[0].split('<p><strong>Additional Features:')[0].split('<!--googleoff: all-->')[0].split('<li><strong>Additional Information:')[0].split('</table>')[-1]

        description_tags = '<div align=\"left\"<p>'+self.currentItemInfo['description'].replace('"','').replace('\t','').replace(',','').replace('\r','').replace('\n','').encode("ascii", 'ignore')+'</p></div>'
        
        
        
        
        try:
            self.infoLogger('inside trying auction includes attempt list whatever pizza bab')
            auction_includes_tags = '<div align=\"left\"><p><b><u>Auction Includes:</b></u><br><br><ul> '
            auction_includes_list = self.MainFrame.currentItemInfo['auction_includes'].split('|')
            for item in auction_includes_list:
                auction_includes_tags += str('<li>' + item + '</li>')
            auction_includes_tags += '</ul></p></div>'
            self.debugLogger('auction_includes_tags:', auction_includes_tags, auction_includes_list)
        except Exception, e:
            self.infoLogger('try in auction_includes_list' + str(e))
            print(e)
            pass
        
        
        
        
        
        
        
        
        
        
        listing_sku_tags = '<p><span style="color:#a9a9a9;">SKU: '+ self.listingSku + '</span></p>'
        footer_tags = "<div align=\"center\"><br>_________________________________________________________________________________<br></div><div align=\"left\"><b><u><br><br><br>SHIPPING :</u></b><ul><li>Items are shipped out Monday - Friday excluding Holidays.&nbsp; <br></li><li>Please expect up to 1 business day processing time for item to ship out.</li><li><b>Combined Shipping: </b>Please contact us before checkout for a revised invoice.</li><li>We DO NOT ship on the weekends.</li><li>We DO NOT ship outside of the US. and its territories</li></ul><b><u>CONTACT :</u></b>Point One Premiums welcomes you to contact us with any questions or concerns during our business hours.<br>(M-F 9am - 5pm CST) Any messages received outside of business hours will be processed the following business day.<br><br>Please use eBay's message system.<b><u><br></u></b><br><u><b>Return policy. </b></u><br><br>We offer a 14 day return policy. &nbsp;If you have any problems with the product please contact us right away to work out an exchange or refund.<br><br><b><u>Warranty Policy :</u></b><i><b><u><br><br></u></b></i><i style=\"font-weight: bold;\"></i>While some of our items are in New or Manufacturer Refurbished condition, <u>None</u> are implied to include a warranty. &nbsp;Some include a Manufacturer Warranty Card and it is between you and Manufacturer if that warranty is still valid. &nbsp;PointOnePremiums offers no warranties or&nbsp;guarantees&nbsp;of a warranty.<br><br><u><b>CANCELING TRANSACTIONS :</b></u><br><br>Due to a large number of bidders not following through on auctions we no longer cancel transactions.<br>All cancelled transactions charged a 15% restocking fee. <br><br><u><b>Unpaid Bidder Policy :</b></u><br><br>A case is opened for all auctions with unpaid bidders.<br>If you do not see something in the photos or detailed in the description as being included, do not assume it is included.&nbsp; <br><u><b><br>AS-IS and FOR PARTS/REPAIR :</b></u><br><br>Items listed AS-IS or FOR PARTS/REPAIR are non returnable and are not covered by our return policy.<br>We encourage buyers to contact us with any issues before opening a case with eBay.&nbsp; We will be happy to work with you to come to a satisfactory resolution.<br></div>    <div><br>    </div>    <div><br>    </div><br><div align=\"center\">___________________________________________________________________________<br></div></body></html>"
        html_for_listing = str(header_tags+title_tags+images_tags+msrp_tags+description_tags+auction_includes_tags+listing_sku_tags+footer_tags)
        return html_for_listing

    def returnEbayAuctionHeaderColumnIndex(self,header_str):
        '''
        returns an index of a header_column
        '''
        if isinstance(header_str, unicode):
            header_str = str(header_str)
        index = self.ebayAuctionHeaders.index(header_str)
        return index

        
    def returnCategory2(self):
        '''
        only relevant for broken watches
        returns second category for broken watches
        '''
        if '2' not in self.Mainframe.currentItemInfo['condition']:
            self.infoLogger('category2 in build auction')
            return '165144'
        else:
            self.infoLogger('Category2 not seen, returning empty string')
            return ''
        
        
    def returnConditionDescription(self):
        '''
        gather the description
        '''
        #make sure the spreadsheet makes sense, these could change column names or something
        #i am a scrub
        
        introduction = 'Works like new. '
        try:
            introduction += self.MainFrame.currentItemInfo['condition_notes'].lower().capitalize() 
            introduction += '. '
        except Exception, e:
            self.infoLogger(e)
            pass
        try:
            if len(self.MainFrame.currentItemInfo['band_size']) != 0:
                introduction += 'Watch fits a '
                introduction += self.MainFrame.currentItemInfo['band_size'] 
                introduction += 'inch wrist'
        except Exception, e:
            self.infoLogger(e)
            pass
            
        return introduction
        
        
        
    def generateEbayListingCsvLine(self):
        '''
        Generates a dictionary with ebayAuctionHeaders as keys and based on
        MainFrame.listingPreferences adjusts values accordingly.
        For example:
            Format (Auction, FixedPrice)
            BuyItNowPrice (Based on ???)
            ReservePrice (if msrp > 300:ReservePrice = msrp*.21*1.2)
            *Duration = (3,5,7,10,30)
            *StartPrice = (.99, int*msrp)
            ShippingService-1:Option = (FedExHomeDelivery, USPS?)
            C:XXXXXX = for item_specific in currentItemSpecifics:
            '''
        #-------------------------------------------------------
        # listingDict  returns modified dictionary
        # from currentItemInfo
        #-------------------------------------------------------
        listingDict = self.processListingPreferences()
        line = []
        for header in self.ebayAuctionHeaders:
            line.append('')

        defaults = {'*Action(SiteID=US|Country=US|Currency=USD|Version=745)':'VerifyAdd',
                    'ConditionDescription':self.returnConditionDescription(),
                    '*Quantity':'1',
                    'ImmediatePayRequired':'0',
                    '*Location':'55406',
                    'GalleryType':'Gallery',
                    'PayPalAccepted':'1',
                    'PayPalEmailAddress':'sales@skygroupcloseouts.com',
                    'PaymentInstructions':'If you need a revised invoice for combined shipping, please contact us before paying so we can adjust the shipping costs.',
                    'Category2':self.returnCategory2(),
                    'StoreCategory':'',
                    'ShippingDiscountProfileID':'',
                    'DomesticRateTable':'',
                    'ShippingType':'Flat',
                    'SalesTaxPercent':'6.875',
                    'SalesTaxState':'MN',
                    'ShippingInTax':'1',
                    'UseTaxTable':'0',
                    'PostalCode':'55406',
                    'ReturnsAcceptedOption':'ReturnsAccepted',
                    'RefundOption':'MoneyBackOrExchange',
                    'ReturnsWithinOption':'Days_14',
                    'ShippingCostPaidByOption':'Buyer',
                    'AdditionalDetails':'Please contact us before returning any item. Items listed AS-IS or For Parts/Repair are not covered by our return policy.  We offer 14 days to return item after receiving it. If item is defective we will supply return shipping label. Item must be returned in original packaging with all accessories included. We also charge a 15% restocking fee for cancelled transactions that are not shipped, or we let it go to eBay as an unpaid bidder case.  Do Not Bid If You Do Not Intend To Follow Through!',
                    'ShippingProfileName':'',
                    'ReturnProfileName':'',
                    'PaymentProfileName':'',
                    'SiteID':'US',
                    'BoldTitle':'0',
                    'Featured':'0',
                    'Highlight':'0',
                    'Border':'0',
                    'HomePageFeatured':'0',
                    'LinkedPayPalAccount':'1',
                    'MaximumItemCount':'100',
                    'MaxItemMinFeedback':'5',
                    'MaxUnpaidItemsCount':'2',
                    'MaxUnpaidItemsPeriod':'Days_30',
                    'MaxViolationCount':'4',
                    'MaxViolationPeriod':'1',
                    'MinimumFeebackScore':'-1',
                    'ShiptoRegCountry':'1',
                    'BuyItNowPrice':'',
                    'ReservePrice':'',
                    'ShippingService-1:Option':'FedExHomeDelivery',
                    'ShippingService-1:Cost':listingDict['ShippingService-1:Cost'],
                    'ShippingService-1:Priority':'1',
                    'ShippingService-1:ShippingSurcharge':'10.00',
                    'DispatchTimeMax':'1',
                    '*Title':self.currentItemInfo['title'],
                    '*Category':self.currentItemInfo['*Category'],
                    '*Duration':listingDict['*Duration'],
                    '*StartPrice':listingDict['*StartPrice'],
                    '*PicURL':self.final_destination,
                    '*ConditionID':self.currentItemInfo['*ConditionID'],
                    'Subtitle':'',
                    '*Description':self.returnHtmlStringForListing(),
                    '*Format':listingDict['*Format'],
                    '*CustomLabel':self.listingSku
                    }
        #-------------------------------------------------------
        # iterate defaults and fill line[index]
        #-------------------------------------------------------
        for key in defaults.keys():
            index = self.returnEbayAuctionHeaderColumnIndex(key)
            line[index] = defaults[key]
        #-------------------------------------------------------
        # Fill item specs
        # [ item_category, ['item_specs', 'item_specs']]
        #-------------------------------------------------------
        for key in self.currentItemSpecificsDict:
            if key is '':
                continue
            else:
                index = self.returnEbayAuctionHeaderColumnIndex(key)
                line[index] = self.currentItemSpecificsDict[key]

        fp = os.path.join(self.currentItemInfo['jNumberFolderPath'],self.listingSku+'.csv')
        self.line = line
        try:
            with open(fp,'wb') as f:
                writer = csv.writer(f)
                writer.writerow(line)
        except IOError, e:
            return e
        return fp


    def returnEbayCsvFilePath(self):
        '''
        returns file path for generated csv line
        '''
        return

    def processListingPreferences(self):
        '''
        given listingPreferences returns a dictionary with modified info based on
        currentItemInfo
        '''
        self.infoLogger('###############Applying listing Preferences###################')
        for key in self.listingPreferences.keys():
            self.infoLogger('\n#'+': '.join([key,str(self.listingPreferences[key])])+'\n#')
        
        
        msrp = self.currentItemInfo['msrp']
        # strip $ character from msrp
        if '$' in msrp:
            msrp = msrp.split('$')[-1]
        self.itemModifiedListingPreferencesDict['msrp'] = msrp
        self.itemModifiedListingPreferencesDict['ShippingService-1:Option'] = ""
        self.itemModifiedListingPreferencesDict['ShippingService-1:Cost'] = ""
        self.itemModifiedListingPreferencesDict['*StartPrice'] = ""
        self.itemModifiedListingPreferencesDict['*Duration'] = ""
        self.itemModifiedListingPreferencesDict['*Format'] = ""
        self.itemModifiedListingPreferencesDict['ReservePrice'] = ""
        self.itemModifiedListingPreferencesDict['BuyItNowPrice'] = ""
        # self.settings_dict = {'*Format':{'Auction':False, 'FixedPrice':False},
        #            '*Duration':{'3':False,'5':False,'7':False,'10':False,'30':False,'GTC':False},
        #            '*StartPrice':{'.99':False, 'percent of MSRP':False},
        #            'BuyItNowPrice':{'percent of MSRP':False},
        #            'ReservePrice': {'percent of MSRP':False},
        #            'ShippingService-1:Option':{'FedExHomeDelivery':False, 'USPSPriority':False},
        #            'ShippingService-1:Cost':{'Amount':False},
        #            }
        #-------------------------------------------------------
        # the format of listingPreferences
        # percent of MSRP  swaps with textctrl value  and ShippingCost/Amount
        self.infoLogger('listingPreferences: '+str(self.listingPreferences)+'\nType: '+str(type(self.listingPreferences)))
        float_check_list = ['percent of MSRP', 'Amount']
        # import pdb;pdb.set_trace()
        for header_key in self.listingPreferences:
            for setting_dict_key in self.listingPreferences[header_key]:
                self.infoLogger(' : '.join(['header',header_key,'setting_dict_key',setting_dict_key,'s_value',str(self.listingPreferences[header_key][setting_dict_key])]))
                if 'False' not in str(self.listingPreferences[header_key][setting_dict_key]): # tests for integers or True
                    if setting_dict_key in float_check_list:
                        setting_dict_key = self.listingPreferences[header_key][setting_dict_key]
                    self.itemModifiedListingPreferencesDict[header_key] = setting_dict_key
        self.infoLogger(str(self.itemModifiedListingPreferencesDict.keys()))
        #----------------------------------------------
        # update *StartPrice, ReservePrice, BuyItNowPrice
        #----------------------------------------------
        float_check_list = ['BuyItNowPrice', 'ReservePrice', '*StartPrice']
        self.infoLogger(self.listingPreferences)
        for key in float_check_list:
            for modifier_key in self.listingPreferences[key]:
                modifier_value = str(self.listingPreferences[key][modifier_key])
                self.infoLogger('Checking floats: '+
                ' '.join([key,str(self.listingPreferences[key]),
                '\nself.itemModifiedListingPreferencesDict[key]: '+
                str(self.itemModifiedListingPreferencesDict[key]),
                '\nmodifer_key: ',str(modifier_key),
                '\nmodifer_value: ',modifier_value]))
                
                if 'False' not in modifier_value:
                    if '.99' in modifier_key: # if *StartPrice .99 has been selected
                        self.itemModifiedListingPreferencesDict[key] = ".99"
                        self.infoLogger('self.itemModifiedListingPreferencesDict[key] Modified: '+str(self.itemModifiedListingPreferencesDict[key]))
                    else:
                        modifier = float(modifier_value)
                        self.infoLogger('modifier: '+str(modifier))
                        # Change floats have 2 decimal places
                        if modifier != 0.0:
                            self.itemModifiedListingPreferencesDict[key] = "%.2f" % round(float(msrp)*float(modifier),2)
                            self.infoLogger('self.itemModifiedListingPreferencesDict[key] Modified: '+str(self.itemModifiedListingPreferencesDict[key]))
                        else:
                            self.itemModifiedListingPreferencesDict[key] = ''
        # self.itemModifiedListingPreferencesDict['*StartPrice'] = 
        self.infoLogger('###############Applied listing Preferences###################')
        for key in self.listingPreferences.keys():
            self.infoLogger('\n#'+': '.join([key,str(self.itemModifiedListingPreferencesDict[key])])+'\n#')
        self.infoLogger('########## Returning self.itemModifiedListingPreferencesDict ######')
        return self.itemModifiedListingPreferencesDict

def unit_test():
    import wx
    app = wx.App(False)
    app.MainLoop()
    cwd = os.getcwd()
    l = [cwd,'display_image/jPages','QZ468','4QZ4680000010_VA_999']
    item_folder = os.path.join('display_image/jPages','QZ468')
    item_path = os.path.join(*l)
    self.infoLogger(item_path)
    image_sources = {item_path:'True'}
    currentItemInfo = {'description':'This is a description',
                        'title':'Title Here',
                        '*Category':'123456',
                        'image_sources':image_sources,
                        'msrp':'$429.99',
                        'itemFolder':item_folder,
                        '*ConditionID':'1000'
                        }
    listingSku = '1000-load-H11-JM'
    currentItemSpecificsDict = {'C:Brand':'Brand Here','C:Style':'Regular'}
    import sky_manifest
    from ListingPreferencesDialog import ListingPreferencesDialog
    from ListingPreferencesDialog import CheckListingPreferences as CheckListingPreferences
    results = ListingPreferencesDialog(None, -1,title='Listing Preferences')
    listingPreferences = CheckListingPreferences()
    listingPreferences = listingPreferences.check()
    self.infoLogger(listingPreferences)
    ebayAuctionHeaders = sky_manifest.ManifestReader(os.path.join('dependencies','ebay_auction_headers.csv')).returnTitleHeaders()
    results = BuildAuction(currentItemInfo, listingSku, currentItemSpecificsDict, ebayAuctionHeaders, listingPreferences)
    line_list_fp = results.generateEbayListingCsvLine()
    results.processListingPreferences()
    self.infoLogger(line_list_fp)
    import csv
    with open('tmp/line_test.csv','wb') as f:
        writer = csv.writer(f)
        writer.writerow(results.line)

if __name__ == '__main__':
    unit_test()
