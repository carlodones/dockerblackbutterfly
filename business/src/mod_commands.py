import os
import threading
import time
import mod_log
import mod_thread

# Threads management class
class CommandsManager(object):

    def __init__(self, log_mgr, thread_list, delay, expire_timeout, expire_count, commands_path, evn_restart, evn_stop):

        self.log_mgr = log_mgr              # Log manager
        self.thread_list = thread_list      # List of configured threads
        self.delay = delay                  # Thread stop timeout 
        self.expire_timeout = expire_timeout # Thread stop timeout 
        self.expire_count = expire_count    # Thread stop timeout 
        self.commands_path = commands_path  # Command file path
        
        self.exit_flag = False              # Threads termination flag
        self.evn_restart = evn_restart      # Service restart event signal
        self.evn_stop = evn_stop            # Service stop event signal

        self.commands_list = { \
            "RESTART": False, \
            "STOP": True }

        self.log_mgr.warning(self.__class__.__name__, "Managed threads list:", 3)
        if(len(self.thread_list) == 0):
            self.log_mgr.warning(self.__class__.__name__, " --> Empty thread list!", 3)

        for th in self.thread_list:
            self.log_mgr.info(self.__class__.__name__, " --> thread:<" + str(th.get_id()) + ">", 3)

        self.log_mgr.info(self.__class__.__name__, "Initialized", 2)

    # Start commands management thread
    def start_commands_mgmt(self):
        self.cmd_thread = threading.Thread(target = self.commands_mgmt_thread)
        self.cmd_thread.start()
        self.cmd_thread.join()

    # Commands manager thread
    def commands_mgmt_thread(self):

        flag_restart = False
        self.log_mgr.info(self.__class__.__name__, "Started", 2)

        while (self.exit_flag == False):

            # Check if a command was received
            for cmd in self.commands_list.keys():
                if (os.path.exists(str(self.commands_path) + "/" + str(cmd))):
                    self.log_mgr.info(self.__class__.__name__, "Received command: <" + str(cmd) + ">", 2)
                    self.exit_flag = True
                    os.remove(str(self.commands_path) + "/" + str(cmd))
                    flag_restart = self.commands_list.get(cmd)

            time.sleep(self.delay)

        self.stop_threads()
        self.log_mgr.info(self.__class__.__name__, "Stopped", 2)

        # Set the restart event:
        if flag_restart:
            self.evn_restart.set()
        else:
            self.evn_stop.set()

    def stop_threads (self):
        self.log_mgr.info(self.__class__.__name__, "Stopping threads")

        if(len(self.thread_list) == 0):
            self.log_mgr.warning(self.__class__.__name__, "Empty thread list!", 1)
            return

        # Provinding all threads the stop command
        self.log_mgr.info(self.__class__.__name__, "Giving threads stop command", 3)
        try:
            for th in self.thread_list:
                self.log_mgr.info(self.__class__.__name__, "Stopping thread:<" + str(th.get_id()) + ">", 3)
                th.stop_thread()
        except Exception as ex:
            self.log_mgr.fatal(self.__class__.__name__, "Error Giving threads stop command; message:<" + str(ex.message) + ">", 1)

        # Waiting for all threads to stop
        self.log_mgr.info(self.__class__.__name__, "Waiting for threads to stop", 3)
        try:
            expire_count = self.expire_count
            while (expire_count > 0):
                all_threads_stopped = True
                for th in self.thread_list:
                    if (th.stopped_thread() == False):
                        all_threads_stopped = False 
                    else:
                        self.log_mgr.info(self.__class__.__name__, "Stopped thread:<" + str(th.get_id()) + ">", 3)
                        self.thread_list.remove(th)

                if(all_threads_stopped == False):
                    expire_count = expire_count - 1
                    time.sleep(self.expire_timeout)
                else:
                    expire_count = 0

        except Exception as ex:
            self.log_mgr.fatal(self.__class__.__name__, "Error waiting for threads to stop; message:<" + str(ex.message) + ">", 1)

        # Waiting for all threads to stop
        self.log_mgr.info(self.__class__.__name__, "Closing thread objects", 3)
        try:
            while (expire_count > 0):
                all_threads_stopped = True
                for th in self.thread_list:
                    if (th.stopped_thread() == False):
                        all_threads_stopped = False 
                    else:
                        th.close()
                        self.thread_list.remove(th)
                        self.log_mgr.info(self.__class__.__name__, "Stopped thread:<" + str(th.get_id()) + ">", 3)

                if(all_threads_stopped == False):
                    expire_count = expire_count - 1
                    time.sleep(self.expire_timeout)
                else:
                    expire_count = 0

        except Exception as ex:
            self.log_mgr.fatal(self.__class__.__name__, "Error closing thread objects; message:<" + str(ex.message) + ">", 1)

        self.log_mgr.info(self.__class__.__name__, "Threads stopped", 1)
