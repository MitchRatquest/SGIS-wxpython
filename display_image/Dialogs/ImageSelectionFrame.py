import wx
import os
from display_image.Check import Check
from PIL import Image
from PIL import ImageEnhance
from logs.logger_example import log_this
import sys
import traceback
from display_image.SaveJsonStateFile import Save

class ImageSelectionFrame(wx.Frame):
    '''
    This class creates a frame to select images when a jnumber is loaded.
    It also prepares downloaded images for buttonizing them pressed/selected
    by adjusting the contrast of them.
    '''
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.panel = wx.ScrolledWindow(self, -1)
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        fontsz = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPixelSize()
        self.panel.SetScrollRate(fontsz.x, fontsz.y)
        self.panel.EnableScrolling(True, True)

    def setMainFrame(self,MainFrame):
        self.MainFrame = MainFrame
        self.logger = log_this(__name__,self.MainFrame)
        self.prepareImageButtons()
        
    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return

    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+" "+this_function_name,debug_info)
        return


    def prepareImageButtons(self):
        '''
        Prepares image buttons for ImageSelectionFrame
        '''
        self.infoLogger('\n# ImageSelectionFrame.prepareImageButtons #')
        check = Check(self.MainFrame)
        check.storeRadioSelection()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        button_id = 900
        for name in self.MainFrame.currentItemInfo['image_list']:
            try:
                name = name.split('?')[0] + '.JPEG'
                if len(self.MainFrame.jNumber) is 0:
                    self.MainFrame.jNumber = self.MainFrame.defaultJNumber
                #self.infoLogger('. Creating Button For: ' + self.MainFrame.jNumber)
                defaultJPagesFolder = self.MainFrame.defaultJPagesFolder
                jNumberFolderPath = os.path.join(str(defaultJPagesFolder),str(self.MainFrame.jNumber))
                self.fp = os.path.join(jNumberFolderPath,str(name))
                if os.path.exists(self.fp):
                    self.infoLogger("File Exists: "+self.fp)
                    pass
                else:
                    self.infoLogger("Doesnt exist: "+self.fp)
                    break
                #self.debugLogger("prepareImageButtons:",name,defaultJPagesFolder,jNumberFolderPath,self.fp)
                try:
                    self.infoLogger("Trying self.createButtonImage")
                    button_names = self.createButtonImage(name, defaultJPagesFolder, jNumberFolderPath, self.fp)
                    self.infoLogger(str(button_names)+" "+str(traceback.format_exc()))
                    #self.debugLogger("button_names: ",button_names)
                    if isinstance(button_names,Exception):
                        raise(button_names)
                except Exception,e:
                    self.infoLogger('we had a problem '+str(e))
                    break

                pressed = button_names[0]
                disabled = button_names[1]
                button_name = str('button'+str(button_id))
                print(type(pressed))
                if isinstance(pressed,int):
                    exit()
                #self.debugLogger("Button Names: ", pressed, disabled, button_name)
                try:
                    self.button_name = ShapedButton(self.panel,
                                        wx.Bitmap(self.fp),
                                        wx.Bitmap(pressed),
                                        wx.Bitmap(disabled),
                                        title=self.fp,
                                        id=button_id,
                                        )
                    # button_name is ShapedButton instance and for the logger
                    # pass MainFrame to instance
                    self.button_name.setMainFrame(self.MainFrame)
                except Exception,e:
                    self.infoLogger(str(e)+" "+str(traceback.format_exc()))
                    continue
                self.button_name.Bind(wx.EVT_BUTTON, self.on_button)
                self.sizer.AddStretchSpacer(1)
                self.sizer.Add(self.button_name, 0, wx.ALIGN_CENTER)
                self.sizer.AddStretchSpacer(1)
                button_id += 1
            except Exception,e:
                self.debugLogger("picture missing? or Not Found? ",e)
                continue
        self.panel.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.panel.Layout()

    def on_button(self, event):
        '''
        When a button is clicked it prints the event objects title.
        button_name = str('button'+str(button_id)) button_id is an iterated
        number.
        '''
        #import pdb; pdb.set_trace()
        self.infoLogger('. Button was clicked.' + event.GetEventObject().title)

    def createButtonImage(self, name, defaultJPagesFolder, jNumberFolderPath, fp):
        '''Creates the images for image selection buttons
            pressed, disabled by changing the contrast with PIL
        '''
        try:
            self.infoLogger('\n# ImageSelectionFrame.createButtonImage(): #')
            self.debugLogger("fp:",fp)
            self.infoLogger(type(fp))
            fp = "./"+fp
            self.infoLogger('Trying to open fp: '+str(fp)+" Type:"+str(type(fp)))
            im = Image.open(fp)
            brightness = ImageEnhance.Brightness(im)
            darker_brightness = brightness.enhance(.5)
            name_edit_list = name.split('.JPEG')
            self.infoLogger(str(name_edit_list))
            self.infoLogger("jNumberFolderPath: "+str(jNumberFolderPath))
            
            pressed_image_name = os.path.join(jNumberFolderPath,
                                                ''.join([name_edit_list[0],
                                                '_pressed', '.JPEG']))
            self.infoLogger(pressed_image_name)
            darker_brightness.save(pressed_image_name)
            contrast = ImageEnhance.Contrast(im)
            lower_contrast = contrast.enhance(.5)
            disabled_image_name = os.path.join(jNumberFolderPath,
                                                ''.join([name_edit_list[0],
                                                '_disabled', '.JPEG']))
            self.infoLogger(disabled_image_name)
            lower_contrast.save(disabled_image_name)
            self.infoLogger('. Completed Creating Button Images')
        except Exception,e:
                return e
        return pressed_image_name, disabled_image_name


class ShapedButton(wx.PyControl):
    '''
    http://stackoverflow.com/questions/6449709/wxpython-changing-the-shape-of-bitmap-button
    This class creates a selectable button
    It also updates self.MainFrame.currentItemInfo['itemSelectedImages'] on left_up
    {'path/to/img/jnumber/pic_name.JPEG':'True', 'path/to/img/jnumber/pic_name.JPEG':'False'}
    It also Updates self.MainFrame.currentImagePath, and self.MainFrame.image
    '''
    def __init__(self, parent, normal, pressed=None, disabled=None, title=None, id=None,MainFrame=None):
        super(ShapedButton, self).__init__(parent, id, style=wx.BORDER_NONE)
        self.normal = normal
        self.pressed = pressed
        self.disabled = disabled
        self.title = title
        self.id = id
        self.region = wx.RegionFromBitmapColour(normal, wx.Colour(0, 0, 0, 0))
        self._clicked = False
        self._selected = False
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_dclick)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

    def setMainFrame(self,MainFrame):
        self.MainFrame = MainFrame
        self.logger = log_this(__name__,self.MainFrame)
        self.infoLogger(('. id: ' + str(self.id)))        
    def infoLogger(self,msg=None):
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_info(this_function_name,str(msg)+" "+this_function_name)
        return

    def debugLogger(self,msg=None,*args,**kwargs):
        debug_info = {'ARGS':args, 'KWARGS':kwargs}
        this_function_name = sys._getframe().f_back.f_code.co_name
        self.logger.log_debug(this_function_name,str(msg)+" "+this_function_name,debug_info)
        return

    def DoGetBestSize(self):
        return self.normal.GetSize()

    def Enable(self, *args, **kwargs):
        super(ShapedButton, self).Enable(*args, **kwargs)
        self.Refresh()

    def Disable(self, *args, **kwargs):
        super(ShapedButton, self).Disable(*args, **kwargs)
        self.Refresh()

    def post_event(self):
        event = wx.CommandEvent()
        event.SetEventObject(self)
        event.SetEventType(wx.EVT_BUTTON.typeId)
        wx.PostEvent(self, event)

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()
        bitmap = self.normal
        if self.clicked:
            bitmap = self.pressed or bitmap
        if not self.IsEnabled():
            bitmap = self.disabled or bitmap
        if self._selected is True:
            bitmap = self.disabled or bitmap
        dc.DrawBitmap(bitmap, 0, 0)

    def set_clicked(self, clicked):
        if clicked != self._clicked:
            self._clicked = clicked
            self.Refresh()

    def get_clicked(self):
        return self._clicked
    clicked = property(get_clicked, set_clicked)

    def on_left_down(self, event):
        x, y = event.GetPosition()
        if self.region.Contains(x, y):
            self.clicked = True

    def on_left_dclick(self, event):
        self.on_left_down(event)

    def on_left_up(self, event):
        if self.clicked:
            x, y = event.GetPosition()
            if self.region.Contains(x, y):
                self.post_event()
                if self._selected is False:
                    self._selected = True
                    self.MainFrame.currentItemInfo['itemSelectedImages'].update({self.title:'True'})
                else:
                    self.MainFrame.currentItemInfo['itemSelectedImages'].update({self.title:'False'})
                    self._selected = False
        self.infoLogger('\n# ShapedButtons.on_left_up(): #\n' + str(self.MainFrame.currentItemInfo['itemSelectedImages']))
        self.infoLogger('. ' + str(self._selected))
        self.MainFrame.imageCountLbl.SetLabel('Images Selected: '+str(len(self.MainFrame.currentItemInfo['itemSelectedImages'])))
        Save(self.MainFrame)
        self.clicked = False
        self.updateMainFrameImage()

    def updateMainFrameImage(self):
        if len(self.MainFrame.currentItemInfo['itemSelectedImages']) is 0:
            self.debugLogger("no itemSelectedIMages: ",self.MainFrame.currentItemInfo)
        for key in self.MainFrame.currentItemInfo['itemSelectedImages']:
            if 'True' in self.MainFrame.currentItemInfo['itemSelectedImages'][key]:
                self.MainFrame.currentImagePath = key
                img = wx.Image(key, wx.BITMAP_TYPE_ANY)
                # scale the image, preserving the aspect ratio
                W = img.GetWidth()
                H = img.GetHeight()
                if W > H:
                    NewW = self.MainFrame.PhotoMaxSize
                    NewH = self.MainFrame.PhotoMaxSize * H / W
                else:
                    NewH = self.MainFrame.PhotoMaxSize
                    NewW = self.MainFrame.PhotoMaxSize * W / H
                img = img.Scale(NewW, NewH)
                self.MainFrame.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
                self.MainFrame.mainPanel.Refresh()

    def on_motion(self, event):
        if self.clicked:
            x, y = event.GetPosition()
            if not self.region.Contains(x, y):
                self.clicked = False

    def on_leave_window(self, event):
        self.clicked = False

