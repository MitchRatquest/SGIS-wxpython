import os
import shutil
import time
import json
import traceback

wwwDirPath = '/var/www'
verificationRequestsDirPath = '/home/sgdevbox/verificationRequestsQueue'

def checkIsFile(fp):
    '''
    Checks if is file.

    '''
    if os.path.isfile(fp):
        return True
    else:
        return False

def ifVerifyExists(fp):
    '''
    Checks verification file returns True or False
    '''
    if 'verify_' in fp:
        return checkIsFile(fp)
    else:
        return False

def IfListedExists(fp):
    '''
    Checks if item has been listed.
    '''
    if 'listed_' in fp:
        return checkIsFile(fp)
    else:
        return False

def processSalesReport(reportPath):
    '''
    Processes sales reports from ebay. Updates status of items.
    Statuses:
        Sold
        Unsold
        Paid and Shipped
        ???
    '''

def grabVerifyRequests():
    '''
    Walks wwwDirPath, reading and appending Verification Requests
    to verify_line_dict.
    returns verify_line_dict
    '''
#    import pdb;pdb.set_trace()
    verify_line_dict = {}
    for directory in os.walk(wwwDirPath):
        folderSku = directory[0]
        subDirs = directory[1]
        fileNames = directory[2]
        for fn in fileNames:
            fp = os.path.join(folderSku,fn)
            if '~' in fp:
                continue
            if 'orig.' in fp:
                continue
            if IfListedExists(fp) is True:
                continue
            if ifVerifyExists(fp) is True:
                print(fp)
                with open(fp,'r') as f:
                    lines = f.readlines()
                    try:
                        line = lines[0]
                    except IndexError, e:
                        print(e)
                        print(lines)
                verify_line_dict[fp] = line
    print(verify_line_dict.keys())
    return verify_line_dict

def updateVerificationRequestsQueueCsv():
    '''
    Update year_month_day_VerificationRequests.csv
    Copy verify_XXX to orig.verify_XXX
    Renames verify_sku_load_shelf_initials.csv to
    verifying_sku_load_shelf_initials.csv
    '''


    verify_line_requests = grabVerifyRequests() # returns dict {fp:fileContents[0]}
    if len(verify_line_requests) is 0:
        print('No verify_XXX.csv files found.\nExiting.')
        exit()
    # count verify files with current data, iterate a new file
    # X_name.csv
    year = str(time.localtime()[0])
    month = str(time.localtime()[1])
    day = str(time.localtime()[2])
    count = len([name for name in os.listdir(verificationRequestsDirPath) if '_'.join([year,month,day,'verificationRequestsQueue.csv']) in name])
    csv_fn = '_'.join([year,month,day,'verificationRequestsQueue.csv'])
    csv_fn = str(count)+'_'+csv_fn
    print('Found/Creating: ' + csv_fn)
    verificationRequestCsvName = csv_fn
    verificationRequestsFp = os.path.join(verificationRequestsDirPath, verificationRequestCsvName)
    seleniumJson = str(count)+'_'+'_'.join([year,month,day,'selenium.json'])
    print(seleniumJson)
    seleniumDir = '/var/www/selenium'
    verifySeleniumJson = os.path.join(seleniumDir, seleniumJson)
    # grab headers and append line to top
    ebay_auction_headers_fp = "/home/sgdevbox/ebay_auction_headers.csv"
    with open(ebay_auction_headers_fp, 'r') as f:
        headers = f.read()
    with open(verificationRequestsFp,'a+') as f:
            f.write(headers)


    # write csv lines
    try:
        with open(verificationRequestsFp,'a+') as f:
            # keys are fp, values is csv content
            for key in verify_line_requests.keys():
                f.write(verify_line_requests[key])
                tmp_fp_split = os.path.split(key)
                copy_fp =  os.path.join(tmp_fp_split[0],'orig.'+tmp_fp_split[1])
                shutil.copy(key,copy_fp)
                os.rename(key,key.replace('verify_','verifying_'))
        with open(verificationRequestsFp, 'r') as f:
            lines = f.readlines()
            with open(verifySeleniumJson, 'wb') as f:
                json.dump(lines, f)
        return True, verificationRequestsFp
    except Exception, e:
        print(traceback.format_exc())
        return e


def main():

    # walks directories and appends line to VerificationRequestsQueue.csv
    # renames verify_XXXX.csv to verifying_XXXX.csv
    # returns returns [True, file_path]
    results = updateVerificationRequestsQueueCsv()
    if results[0] is True:
        print('Lines appended to:' + results[1])
    else:
        print(results)


if __name__ == '__main__':
    main()


