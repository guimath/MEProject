# -*-coding:utf-8 -*
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in corect dir

import Interface
import tkinter as tk
import logging 

from mep import Downloads as dls
from mep import Utilitaries as util
from mep.Tagger import Tagger
from mep.Info_search import Info_search

class Mep :
    def __init__(self) :
        # Working dir 
        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            ABSOLUTE_PATH = os.path.dirname(sys.executable)
        elif __file__:
            ABSOLUTE_PATH = os.path.dirname(__file__)
        os.chdir(ABSOLUTE_PATH)

        # Var init : 
        #local : 
        self.treated_file_nb = 0
        self.remaining_file_nb = 0
        self.total_file_nb = 0
        self.file_nb = 1
        
        self.file_extension = [".mp3"]   # will store all file extensions
        self.file_name = ["music.mp3"]   # will store all file names
        self.ignore = ["music.mp3"]

        self.current_file_name = ""
        self.current_image_name = ""

        self.a_good_file = []
        self.a_maybe_file = []
        self.a_nothing_file = []
        self.finished = True    
        
         # CONSTANTS params 
        self.NOT_SUPPORTED_EXTENSIONS = [".m4a", ".flac", ".mp4", ".wav", ".wma", ".aac"]
        self.SUPPORTED_EXTENSIONS = [".mp3"]  # list of all accepted extensions

        self.ADD_SIGN = False 

        if self.ADD_SIGN :
            self.SIGN = "MEP by GM"
        else :
            self.SIGN = "---"

        self.FONT_NAME = "helvetica"
        self.FONT_SIZE = "14"
        self.FONT = self.FONT_NAME+" " + self.FONT_SIZE
        #tk.font.Font(self, font= self.FONT, name="normal", exists=True) # doesn't work...
        
        # creating interface        
        root = tk.Tk()
        self.app = Interface.Application(logger = logger, mep= self, master=root)
        

    def start(self):
        self.app.global_start_wnd()

        # getting info from config file :
        self.params = util.read_config(self.app)
        self.yt_logger = self.app.dl_logger(self.app)        
        self.web = Info_search(self.params) 
        self.tagger = Tagger(self.params, self.ADD_SIGN, self.SIGN) 
        self.app.mainloop()

        

def main() :
    mep = Mep()
    mep.start()

    

if __name__ == '__main__':
    log_lvl = logging.INFO
    logger = logging.getLogger("MEP")
    logger.setLevel(log_lvl)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(log_lvl)
    ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(ch)
    main()
