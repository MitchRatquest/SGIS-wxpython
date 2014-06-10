import wx
from logs.logger_example import log_this
import sys

class ReturnCorrectTitleDialog(wx.Dialog):

    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title)
        self.panel = wx.ScrolledWindow(self, -1)
        #self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        fontsz = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPixelSize()
        self.panel.SetScrollRate(fontsz.x, fontsz.y)
        self.panel.EnableScrolling(True, True)
        self.title_and_row_index = ''

    def setMainFrame(self,MainFrame):
        self.MainFrame = MainFrame
        self.logger = log_this(__name__,self.MainFrame)
        self.prepareTitleButtons()
        return

    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return
    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+this_function_name,debug_info)
        return

    def prepareTitleButtons(self):
        '''
        Prepares title buttons for SelectCorrectWatchTitle
        # currentTitleList = [title, str, row_index]
        '''
        self.debugLogger('\n# SelectCorrectWatchTitle.prepareTitleButtons #')
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        button_id = 1000

        for title_list in self.MainFrame.currentTitleList:
            # currentTitleList = [title, str, row_index]
            title = title_list[0]
            row_index = title_list[2]
            tmp_title = str('row_index:' + str(row_index) + ':' + title)
            self.debugLogger(str(tmp_title))
            title = str(tmp_title)
            self.button_name = str('button'+str(button_id))
            self.button_name = wx.Button(self.panel, label=title)
            self.button_name.Bind(wx.EVT_BUTTON,self.on_button)
            self.sizer.Add(self.button_name, 0, wx.ALIGN_CENTER)
            button_id += 1
        self.panel.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.panel.Layout()
        self.panel.Centre()
        self.panel.Show(True)

    def on_button(self, event):
        ''' Returns title when clicked'''
        self.debugLogger('. Button was clicked.' + event.GetEventObject().GetLabel())
        self.title_and_row_index = event.GetEventObject().GetLabel()
        self.Close()
