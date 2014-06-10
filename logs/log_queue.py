from Queue import Queue
import inspect
import traceback
import logging

#https://docs.python.org/3.5/howto/logging-cookbook.html
#QueueHandler is new to 3.2, so logging.handlers has been 'patched' and included
# in the dependecies folder just in case

class logQueue(object):
    '''
    Class to handle threaded logging ... for example with onPrefetch/wx.Yield
    '''
    def __init__(self, MainFrame):
        super(logQueue, self).__init__()
        self.MainFrame = MainFrame
        self.q = Queue(-1) # no limit on size
        #self.q_handler = QueueHandler(self.q)
        self.run()


    def enqueue(self,task):
        self.q.put(task)
        self.run()
        return

    def run(self):
        print('entering logging q')
        while not self.q.empty():
            try:
                task = self.q.get()
                #print(task)
                task_type = task[0]
                if task_type is 0:
                    try:
                        logger = logging.getLogger(task[1])
                        HANDLER = task[2]
                        msg = task[3]
                        logger.addHandler(HANDLER)
                        if self.MainFrame.threading is False:
                            logger.info("\n%s" % (msg))
                    except Exception, e:
                        print(e)
                        print(traceback.format_exc())
                        exit()
                if task_type is 1:
                    try:
                        logger = logging.getLogger(task[1])
                        HANDLER = task[2]
                        func_name = task[3]
                        msg = task[4]
                        debug_info = task[5]
                        logger.addHandler(HANDLER)
                        #called_frame_trace = "\n    ".join(traceback.format_stack()).replace("\n\n","\n")
                        outer_frames = inspect.getouterframes(inspect.currentframe().f_back.f_back)
                        call_fn = outer_frames[3][1]
                        call_ln = outer_frames[3][2]
                        call_func = outer_frames[3][3]
                        caller = outer_frames[3][4]
                        # a string with args and kwargs from log_debug
                        args_kwargs_str = "\n"+str(debug_info).replace(", '","\n, '")
                        if self.MainFrame.threading is False:
                            results = logger.debug("%s\nARGS_KWARGS_STR:%s\ncall_fn: %s\ncall_ln: %i\ncall_func: %s\ncaller: %s\nException:" % (
                                                        msg,
                                                        args_kwargs_str,
                                                        call_fn,
                                                        call_ln,
                                                        call_func,
                                                        caller
                                                        ),exc_info=1)
                        return
                    except Exception, e:
                        print(e)
                        print(traceback.format_exc())
                        return

            except Exception,e:
                import traceback
                print(e)
                print(traceback.format_exc())
                exit()
