import logging
import logging.handlers
import traceback
import os
import inspect





class log_this(object):
    def __init__(self,module_name, MainFrame):
        super(log_this, self).__init__()
        self.MainFrame = MainFrame
        self.module_name = module_name
        LOG_FILENAME = os.path.join('logs','mainframe.log')
        LOG_LEVEL = logging.DEBUG
        logging.getLogger(self.module_name)
        logging.basicConfig(level=LOG_LEVEL,
                            format='\n--%(asctime)s %(funcName)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M:%S',
                            filename=LOG_FILENAME,
                            filemode='w')
        #console = logging.StreamHandler()
        # self.handler = logging.handlers.RotatingFileHandler(
              # LOG_FILENAME, maxBytes=2000000, backupCount=5)
        #console.setLevel(logging.INFO)
        self.count = 0


    def log_info(self,name,msg):
        
        
        try:
            log_name = logging.getLogger(".".join([self.module_name,name]))
            #print('In: log_info',self.module_name,name)
            # log_name.addHandler(self.handler)
            if self.MainFrame.threading is False:
                log_name.info("\n%s" % (msg))
            
        except Exception, e:
            print(traceback.format_exc())
            print(e)
            exit()
        return


    def log_debug(self,func_name,msg,debug_info):
        try:
            log_name = logging.getLogger(".".join([self.module_name,func_name]))
            #print('In: log_debug',self.module_name,func_name)
            # log_name.addHandler(self.handler)
            #called_frame_trace = "\n    ".join(traceback.format_stack()).replace("\n\n","\n")
            outer_frames = inspect.getouterframes(inspect.currentframe().f_back.f_back)
            call_fn = outer_frames[2][1]
            call_ln = outer_frames[2][2]
            call_func = outer_frames[2][3]
            caller = outer_frames[2][4]
            # a string with args and kwargs from log_debug
            args_kwargs_str = "\n"+str(debug_info).replace(", '","\n, '")
            if self.MainFrame.threading is False:
                results = log_name.debug("%s\nARGS_KWARGS_STR:%s\ncall_fn: %s\ncall_ln: %i\ncall_func: %s\ncaller: %s\nException:" % (
                                            msg,
                                            args_kwargs_str,
                                            call_fn,
                                            call_ln,
                                            call_func,
                                            caller
                                            ),exc_info=1)
            
        except Exception, e:
            print(traceback.format_exc())
            print(e)
            exit()
        return


