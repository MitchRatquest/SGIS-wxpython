from display_image.MainFrame import MainFrame
import wx
import logging
from logs.logger_example import log_this

def unit_tests():
    ''' Run unit tests for modules '''
    return

def main():
    ''' Run Main Program '''
    global MainFrame
    app = wx.App(False)
    MainFrame = MainFrame(None, 'Sky Group Scanner')
    logger = log_this("run",MainFrame)
    logger.log_info("MainFrame",'# main(): #\n' + 'MainFrame.__dict__:\n' + str(MainFrame.__dict__).replace(", '",",\n '").replace(" {'","\n\n {'"))
    app.MainLoop()
    return

if __name__ == "__main__":
    main()
