# -*- coding: utf8 -*-
# James Munsch
# http://jamesmunsch.com/
# james.a.munsch@gmail.com
import os
import json
import traceback
from logs.logger_example import log_this
import sys
import wx

class ManifestReader(object):
    '''
    File must be Comma Delimited
    List of headers:
    '''
    def __init__(self, filepath, MainFrame):
        super(ManifestReader, self).__init__()
        self.filepath = filepath
        self.returnCsvFile()
        self.MainFrame = MainFrame
        self.logger = log_this(__name__, self.MainFrame)
    def infoLogger(self,msg=None):
        try:
            this_function_name = sys._getframe().f_back.f_code.co_name
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
            self.logger.log_debug(this_function_name,str(msg)+this_function_name,debug_info)
            return
        except Exception, e:
            print(e)
            print(traceback.format_exc())
            exit()
    def returnCsvFile(self):
        '''
        returns filepath.read()
        '''
        with open(self.filepath,'r') as f:
            results = f.read()
        self.orig = results
        return results

    def returnTitleHeaders(self):
        '''
        Returns a title_row_list
        '''
        self.orig = self.returnCsvFile()
        self.tmp = self.orig.replace('\r','')
        lines = self.tmp.split('\n')
        return lines[0].split(',')

    def returnRow(self, row_index):
        '''
        returns a row based on row_index
        '''
        self.tmp = self.orig.replace('\r','')
        lines = self.tmp.split('\n')
        return lines[row_index]
    def returnColumn(self, column_index):
        '''returns a column given an index starts at 0'''
        self.orig = self.returnCsvFile()
        self.tmp = self.orig.replace('\r','')
        lines = self.tmp.split('\n')
        column_list = []
        for row in lines:
            row = row.split(',')
            try:
                column_list.append(row[column_index])
            except Exception,e:
                self.infoLogger('\n# sky_manifest.ManifestReader.returnColumn: ERROR appending')
                self.infoLogger(e)
                pass
        return column_list

    def getJnumbers(self):
        '''
        Returns a list of Jnumbers/offer_ids from spreadsheet
        '''
        self.infoLogger('\n# sky_manifest.ManifestReader.getJnumbers(): ')
        self.infoLogger('Determining Which Retailer')
        results = []
        self.headers = self.returnTitleHeaders()
        retailer = self.headers[0].split(':')[1]
        column_index = self.headers.index('jnumber')
        jnumbers = self.returnColumn(column_index)
        results.append(retailer)
        results.append(set(jnumbers))
        return results

    def returnRowBySku(self, sku):
        '''
        returns a row list by sku number
        '''
        self.tmp = self.orig.replace('\r','')
        lines = self.tmp.split('\n')
        self.headers = self.returnTitleHeaders()
        sku_column_index = self.headers.index('sku')
        row_index = 0
        for line in lines:
            line = line.split(',')
            try:
                if sku in line[sku_column_index]:
                    return [self.headers,line]
            except IndexError, e:
                self.infoLogger(e)
                self.infoLogger(line)
                self.infoLogger(traceback.format_exc())
                pass
            row_index += 1

    def returnItemSpecifics(self, jnumber):
        '''
        Given the jnumber find the item specifics in unique_category_4numbeer_sku.csv
        If unable to find jnumber
        return 'ValueError:'+str(e)
        else return [item_category, [item_specifics]]
        '''
        import csv
        import StringIO

        headers = self.returnTitleHeaders()
        StatusIndex = headers.index('Status')

        ErrorMessageIndex = headers.index('ErrorMessage')
        EbayCategoryIndex = headers.index('*Category')
        # 4number/jnumber
        CustomLabelIndex = headers.index('CustomLabel')
        CustomLabelColumn = self.returnColumn(CustomLabelIndex)
        try:
            EbayCategoryRowNumber = CustomLabelColumn.index(jnumber)
        # will return to caller if a column label is missing
        except ValueError, e:
            self.debugLogger("Missing Column:",e)
            return str('ValueError:'+str(e))

        self.tmp = csv.reader(StringIO.StringIO(self.returnRow(EbayCategoryRowNumber)))
        for line in self.tmp:
            item_row = line
        if 'Failure' not in item_row[StatusIndex]:
            return 'ValueError: Item may not have item specifics or has not been listed before.'
        else:

            try:
                # Split the ErrorMessage column in the unique_category_4number_sku.csv and return category number on jnumber
                # or return False when not found
                item_category = item_row[EbayCategoryIndex]
                # unable to figure out commas in csv :( replacing commas with '#comma#' and splitting
                # replacing all quotes with #quote#
                item_specifics = item_row[ErrorMessageIndex].split('Please provide the required item specifics.|')[-1].split('|')[0].split('#comma# ')
            except Exception, e:
                self.infoLogger(traceback.format_exc())
            except ValueError, e:
                self.infoLogger(traceback.format_exc())
                print e
                return 'Item may not have item specifics or has not been listed before.'
        return item_category, item_specifics


    def checkRetailerAndJnumber(self, scanNumber, retailerCodeHeader):
        '''
        Checks if retailer code matches jnumber
        '''
        retailer_code = retailerCodeHeader.split(':')[-1]
        print(retailer_code)
        print(scanNumber)
        if 'J' in scanNumber[0]:
            if '1' in retailer_code:
                return [True, retailer_code]
        if '4' in scanNumber[0]:
            if '0' in retailer_code:
                return [True, retailer_code]
        return [False, retailer_code]


    def checkIfManifested(self, jnumber, currentPalletNumber):
        '''
        checks if item is manifested
        '''
        self.infoLogger('\n# sky_manifest.ManifestReader.checkIfManifested(jnumber) #')
        self.infoLogger('. jnumber:' + jnumber)
        self.headers = self.returnTitleHeaders()

        result = self.checkRetailerAndJnumber(jnumber, self.headers[0])
        try:
            if result[0] is True:
                retailer_code = result[1]
            else:
                self.debugLogger("retailer_code doesnt match ",result)
                raise Exception("retailer_code is incorrect ")
            jnumber_column_index = self.headers.index('jnumber')
            jnumber_column = self.returnColumn(jnumber_column_index)
            manifested_column_index = self.headers.index('manifested')
            manifested_column = self.returnColumn(manifested_column_index)
            title_column_index = self.headers.index('title')
            title_column = self.returnColumn(title_column_index)
            sku_column_index = self.headers.index('sku')
            sku_column = self.returnColumn(sku_column_index)
            upc_column_index = self.headers.index('upc')
            try:
                pallet_number_index = self.headers.index('pallet_number')
                pallet_number_column = self.returnColumn(pallet_number_index)
            except AttributeError, e:
                pallet_number_index = None
                pallet_number_column = None
        except Exception, e:
            self.debugLogger('\n# sky_manifest.ManifestReader.checkIfManifested(jnumber) #', e)
            return e
        self.infoLogger('. '+str('jc_len:'+str(len(jnumber_column))+' mc_len:'+str(len(manifested_column))+' sc_len:'+str(len(sku_column))))
        row_index = 0
        row_index_matches = []

        for line in jnumber_column:
            if jnumber in line:
                self.infoLogger('. Found Match on row_index:' + str(row_index))
                row_index_matches.append(row_index)
            row_index += 1
        manifested_count = 0
        line_list = self.orig.replace('\r','').split('\n')
        for row_index in row_index_matches:
            line_match = line_list[row_index].split(',')
            try:
                linePalletNumber = line_match[pallet_number_index]
            except IndexError,e:
                self.debugLogger("linePalletNumber",e,pallet_number_index,len(line_match))
                pass
            if linePalletNumber in currentPalletNumber:
                self.infoLogger('. Line Number: ' + str(row_index + 1))
                self.infoLogger('. Found sku Number: ' + str(sku_column[row_index]))
                self.infoLogger('. Manifested: ' + str(manifested_column[row_index]))
                if 'X' in manifested_column[row_index]:
                    manifested_count += 1

        results_dict = {'sku_column_index': sku_column_index,
                        'jnumber_column_index': jnumber_column_index,
                        'manifested_column_index': manifested_column_index,
                        'manifested_column': manifested_column,
                        'row_index_matches': row_index_matches,
                        'manifested_count': manifested_count,
                        'title_column': title_column,
                        'title_column_index': title_column_index,
                        'upc_column_index': upc_column_index,
                        'pallet_number_index': pallet_number_index,
                        'pallet_number_column': pallet_number_column,
                        'currentSku': '',
                        'titleModelSelection': '',
                        'jnumber': jnumber,
                        'retailer_code': retailer_code
                        }
        return results_dict





class ManifestWriter(object):
    '''
    Writes a copy of manifested items to folder
    '''
    def __init__(self, filepath,MainFrame):
        super(ManifestWriter, self).__init__()
        self.filepath = filepath
        self.copyfilepath = self.filepath.split('.csv')[0] + '_copy.csv'
        self.orig = None
        self.returnCsvFile()
        self.MainFrame = MainFrame
        self.logger = log_this(__name__, self.MainFrame)

    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return
    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+this_function_name,debug_info)
        return
    def returnCsvFile(self):
        '''
        returns filepath.read()
        '''
        with open(self.filepath, 'r') as f:
            results = f.read()
        self.orig = results
        return self.orig

    def writeCsvFile(self, csv_file):
        '''
        Over writes filepath with new information
        '''
        try:
            with open(self.filepath, 'wb') as f:
                f.write(csv_file)
                return "Success"
        except IOError, error:
            return error


    def appendLine(self, line):
        '''
        returns filepath.read()
        '''

        with open(self.copyfilepath, 'a+') as f:
            f.write(line)

    def returnTitleHeaders(self):
        '''
        Returns a title_row_list
        '''
        self.tmp = self.orig.replace('\r', '')
        lines = self.tmp.split('\n')
        return lines[0].split(',')

    def returnColumn(self, column_index):
        '''returns a column given an index starts at 0'''
        self.tmp = self.orig.replace('\r', '')
        lines = self.tmp.split('\n')
        column_list = []
        for row in lines:
            row = row.split(',')
            try:
                column_list.append(row[column_index])
            except Exception,e:
                self.infoLogger('\n# sky_manifest.ManifestReader.returnColumn: ERROR appending')
                self.infoLogger(e)
                pass
        return column_list

    def returnRow(self, row_index):
        '''returns a row given an index'''
        return


    def writeToCell(self, cell_input, row_index, column_index):
        '''
        Creates a copy of a file and writes to a cell
        '''
        line_list = self.orig.replace('\r','').split('\n')
        self.infoLogger('cell_input: '+cell_input+' row_index: '+str(row_index)+' column_index: '+str(column_index))
        self.infoLogger(type(cell_input),type(row_index),type(column_index))
        row_count = 0

        for line in line_list:
            if row_count != row_index:
                self.appendLine(line+'\n')
            elif row_count == row_index:
                current_row = line.split(',')
                self.infoLogger(current_row)
                current_row[column_index] = cell_input
                self.infoLogger(current_row)
                current_row = ','.join(current_row)+'\n'
                self.appendLine(current_row)
            row_count += 1

        return results

    def returnTitlesForJnumber(self, dictionaryManifestResults):
        '''returns a list of titles for a given dictionaryManifestResults'''
        self.infoLogger('\n# ManifestWriter.returnTitlesForJnumber')
        self.debugLogger("dictionaryManifestResults length:",len(dictionaryManifestResults))
        pallet_number_column = dictionaryManifestResults['pallet_number_column']
        title_column = dictionaryManifestResults['title_column']
        title_column_index = dictionaryManifestResults['title_column_index']
        manifested_column_index = dictionaryManifestResults['manifested_column_index']
        manifested_column = dictionaryManifestResults['manifested_column']
        row_index_matches = dictionaryManifestResults['row_index_matches']
        title_list = []
        if dictionaryManifestResults['palletNumber'] is None:
            for line_number in row_index_matches:
                if 'X' not in manifested_column[line_number]:
                    title_list.append([title_column[line_number],'row_index:',line_number])
        # return title_list based on palletNumber
        elif dictionaryManifestResults['palletNumber'] is not None:
            for line_number in row_index_matches:
                if dictionaryManifestResults['palletNumber'] in pallet_number_column[line_number]:
                    if 'X' not in manifested_column[line_number]:
                        title_list.append([title_column[line_number],'row_index:',line_number])
        if len(title_list) is 0:
            for line_number in row_index_matches:
                title_list.append([title_column[line_number],'row_index:',line_number])
        return title_list


    def writeManifestedRow(self, dictionaryManifestResults,):
        '''
        Takes a dictionary and writes the row
        results_dict = {'sku_column_index': sku_column_index,
                        'jnumber_column_index': jnumber_column_index,
                        'manifested_column_index': manifested_column_index,
                        'manifested_column': manifested_column,
                        'row_index_matches': row_index_matches,
                        'manifested_count': manifested_count,
                        'title_column': title_column,
                        'title_column_index': title_column_index,
                        'upc_column_index': upc_column_index
                        'pallet_number_index': pallet_number_index,
                        'pallet_number_column': pallet_number_column,
                        'currentSku': '',
                        'titleModelSelection': '',
                        'palletNumber':palletNumber # set in display image
                        'upc':upc # set in display image
                        'jnumber': jnumber
                        }
        '''
        self.infoLogger('\n# ManifestWriter.writeManifestedRow(dict): #')
        self.debugLogger("dictionaryManifestResults Length:",len(dictionaryManifestResults))
        self.orig = self.returnCsvFile()
        cell_input = 'X'
        sku_column_index = dictionaryManifestResults['sku_column_index']
        jnumber_column_index = dictionaryManifestResults['jnumber_column_index']
        currentPalletNumber = dictionaryManifestResults['palletNumber']
        pallet_number_index = dictionaryManifestResults['pallet_number_index']
        pallet_number_column = dictionaryManifestResults['pallet_number_column']
        manifested_column_index = dictionaryManifestResults['manifested_column_index']
        upc_column_index = dictionaryManifestResults['upc_column_index']
        upc = dictionaryManifestResults['upc']
        row_index_matches = dictionaryManifestResults['row_index_matches']
        title_column_index = dictionaryManifestResults['title_column_index']
        manifested_count = dictionaryManifestResults['manifested_count']
        currentSku = dictionaryManifestResults['currentSku']
        titleModelSelection = dictionaryManifestResults['titleModelSelection'] # correct title based on variation
        jnumber = dictionaryManifestResults['jnumber']
        self.infoLogger('cell_input: '+cell_input+' row_information: '+str(dictionaryManifestResults))
        line_list = self.orig.replace('\r','').split('\n')
        self.csv_line_list = []
        # update row_index_matches to only include the current pallet
        tmp_row_index_matches = []
        for row_index in row_index_matches:
            line_match = line_list[row_index].split(',')
            try:
                linePalletNumber = line_match[pallet_number_index]
            except IndexError,e:
                self.debugLogger("linePalletNumber",e,len(line_match),pallet_number_index)
                pass
            if linePalletNumber in currentPalletNumber:
                tmp_row_index_matches.append(row_index)
        row_index_matches = tmp_row_index_matches
        # if a title has been selected split 'row_index:###:title'
        if len(titleModelSelection) is not 0:
            row_index = int(titleModelSelection.split(':')[1])
            self.title = titleModelSelection.split(':')[2]
            line_match = line_list[row_index].split(',')
            if len(row_index_matches) > manifested_count:
                self.infoLogger('. Previously Manifested Items: ' + str(manifested_count))
                # if not manifested, mark it as manifested
                if 'X' in line_match[manifested_column_index]:
                    pass
                elif 'X' not in line_match[manifested_column_index]:
                    row_count = 0
                    for line in line_list:
                        # append non matching rows based on row_index
                        if row_count != row_index:
                            self.csv_line_list.append(line)
                        # if matches modify line and append
                        elif row_count == row_index:
                            current_row = line_match
                            current_row[sku_column_index] = currentSku
                            current_row[upc_column_index] = upc
                            current_row[manifested_column_index] = 'X'
                            current_row = ','.join(current_row)
                            self.csv_line_list.append(current_row)
                        row_count += 1
                else:
                    self.debugLogger(". sky_manifest.ManifestWriter.writeManifestedRow(): 'X' not found in manifested Column")
                    import pdb; pdb.set_trace()
            # manifested_count > row_index_matches
            # when items from other pallet are counted
            elif len(row_index_matches) <= manifested_count:
                self.infoLogger('. This item is an extra, and will be manifested as such.')
                for line in line_list:
                    self.csv_line_list.append(line)
                if len(row_index_matches) is not 0:
                    extra_line = line_list[row_index_matches[0]].split(',')
                else:
                    self.headers = self.returnTitleHeaders()
                    extra_line = self.headers

                if '#TITLE HERE#' in self.title:
                    extra_line[manifested_column_index] = 'EXTRA no model in current manifest'
                else:
                    extra_line[manifested_column_index] = 'EXTRA'
                extra_line[title_column_index] = self.title
                extra_line[sku_column_index] = currentSku
                extra_line[jnumber_column_index] = jnumber
                extra_line = ','.join(extra_line)
                self.csv_line_list.append(extra_line)
                int_dialog = wx.MessageDialog(self.MainFrame, 'Looks like this item is an extra?', 'Appending to end of CSV', wx.OK)
                results = int_dialog.ShowModal()
                int_dialog.Destroy()
        else:
            self.infoLogger('No Title was selected')
            results = 'No Title was selected'
            return results

        csv_file = '\n'.join(self.csv_line_list)
        self.debugLogger("csv_file length:",len(csv_file))
        # ... Really got hosed on not having this here
        STOP = 0
        if len(csv_file) is 0:
            STOP = 1
            self.copyCsvFile()
            import time
            int_dialog = wx.MessageDialog(self.MainFrame, 'STOP! STOawegt WE GOT A PROBLEM!!!!!!!!!', 'IMPORTANT READ THIS', wx.OK)
            results = int_dialog.ShowModal()
            int_dialog.Destroy()
            time.sleep(2)
            int_dialog = wx.MessageDialog(self.MainFrame, 'STOP!!! A PROBLEM!!!!!!!!!', 'IMPORTANT READ THIS', wx.OK)
            results = int_dialog.ShowModal()
            int_dialog.Destroy()
            time.sleep(2)
            int_dialog = wx.MessageDialog(self.MainFrame, 'STOP CLICK(ING!~!!!!!!!!!', 'IMPORTANT READ THIS', wx.OK)
            results = int_dialog.ShowModal()
            int_dialog.Destroy()
            time.sleep(2)
            int_dialog = wx.MessageDialog(self.MainFrame, str('CSV is being copied.\n\n'+str(self.filepath)+"\nCOPIED TO: "+str(self.filepath)+'.ORIG'), 'IMPORTANT READ THIS', wx.OK)
            results = int_dialog.ShowModal()
            int_dialog.Destroy()
            print('WE GOT A PROBLEM CAPTAIN COPYING FILE NOW\n'+str(self.filepath)+" COPIED TO: "+str(self.filepath+'.ORIG'))* 100
            import pdb;pdb.set_trace()
        if STOP is 1:
            exit()
        results = self.writeCsvFile(csv_file)
        return results

    def copyCsvFile(self):
        '''
        COPY FILE TO .ORIG
        '''
        import shutil
        shutil.copy(self.filepath,self.filepath+'.ORIG')

def main():
    '''
    Main define
    '''
    self.infoLogger('Done.')
    exit()

if __name__ == '__main__':
    main()
