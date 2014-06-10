import paramiko
import traceback
import os
import posixpath
from logs.logger_example import log_this
import sys
class Ssh(object):

    def __init__(self, MainFrame):
        super(Ssh, self).__init__()
        self.MainFrame = MainFrame
        self.logger = log_this(__name__,self.MainFrame)
    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return
    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+this_function_name,debug_info)
        return
    def setup(self):
        '''Setup connection'''
        try:
            # DEBUG
            #paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
            #set username & password
            username = self.MainFrame.defaults['username']
            password = self.MainFrame.ssh_pass
            host = self.MainFrame.defaults['serverLocation']
            port = self.MainFrame.defaults['port']
            self.debugLogger('username, host, port',username,host,port)
            self.MainFrame.statusbar.SetStatusText('Trying to connect to server.')
            self.transport = paramiko.Transport((host, port))
            self.transport.connect(username = username, password = password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            print(self.sftp.sock)
        except Exception, e:
            print(traceback.format_exc())
            print(traceback.format_exc())
            self.MainFrame.statusbar.SetStatusText('ERROR: '+str(e))
        return False


    def putFiles(self, sources, listingSku, ebayListingHtml, currentItemInfo):
        '''
        Upload images to server along with all currentItemInfo, plus initials and date
        Basically build the auction and put it into the queue for verification
        '''
        print('\n# Ssh.putFiles() #')
        self.infoLogger('sources: %s listingSku: %s\nebayListingHtml:\n%s\ncurrentItemInfo: \n%s' % (sources, listingSku, ebayListingHtml, currentItemInfo))
        if isinstance(sources, unicode):
            sources = {sources,'True'}
        # check source pictures and put
        try:
            self.setup()
            destination = self.MainFrame.defaults['fileDestination']
            cwd = os.getcwd()
            for source in sources:
                print('\n# Source: '+source)
                if 'True' in source:
                    continue
                else:
                    filename = os.path.split(source)[-1]
                destinationFolder = listingSku
                final_path = posixpath.join(destination,destinationFolder)

                try:
                    self.sftp.mkdir(final_path, mode=755)
                except:
                    #print(traceback.format_exc())
                    pass
                final_destination = posixpath.join(final_path, filename)
                sourceFilePath = os.path.join(cwd,source)
                print('\n# Source Path: {}\n# Destination Path: {}\n\n'.format(sourceFilePath,final_destination))

                self.MainFrame.statusbar.SetStatusText('Trying to transfer: '+final_destination)
                try:
                    self.sftp.put(sourceFilePath, final_destination)
                except Exception, e:
                    print(traceback.format_exc())
                    self.MainFrame.statusbar.SetStatusText('ERROR: '+str(e))

        except Exception, e:
            print(traceback.format_exc())

        # write html file and put
        destination = self.MainFrame.defaults['fileDestination']
        destinationFolder = posixpath.join(destination,listingSku)
        final_destination = posixpath.join(destinationFolder,'index.html')
        source_file = os.path.join(os.path.split(source)[0],'index.html')
        source_path = os.path.join(cwd,source_file)
        with open(source_path, 'wb') as f:
            f.write(ebayListingHtml)
        try:
            self.sftp.put(source_path, final_destination)
        except Exception, e:
            print(e)
            print(traceback.format_exc())
            import pdb;pdb.set_trace()
        # put ebay listing csv
        destination = self.MainFrame.defaults['fileDestination']
        destinationFolder = posixpath.join(destination,listingSku)
        final_destination = posixpath.join(destinationFolder,'verify_'+listingSku+'.csv')
        source_path = os.path.join(cwd,self.MainFrame.ebayCsvFp)
        print('putting: '+str(final_destination))
        try:
            self.sftp.put(source_path, final_destination)
        except Exception, e:
            print(e)
            print(traceback.format_exc())
            import pdb;pdb.set_trace()

        # write jnumber.txt and put used for JSON lookup
        destination = self.MainFrame.defaults['fileDestination']
        destinationFolder = posixpath.join(destination,listingSku)
        final_destination = posixpath.join(destinationFolder,'jnumber.txt')
        source_file = os.path.join(os.path.split(source)[0],'jnumber.txt')
        source_path = os.path.join(cwd,source_file)
        with open(source_path, 'wb') as f:
            f.write(self.MainFrame.currentItemInfo['jNumber'])
        try:
            self.sftp.put(source_path, final_destination)
        except Exception, e:
            print(e)
            print(traceback.format_exc())
            import pdb;pdb.set_trace()

        self.close()
        return True

    def close(self):
        ''' Close the connection '''
        self.sftp.close()
        self.transport.close()
        return

    def resetPass(self, event):
        '''Reset MainFrame.ssh_pass'''
        self.MainFrame.ssh_pass = None
        self.MainFrame.statusbar.SetStatusText('Reset SSH Pass.')
        return
