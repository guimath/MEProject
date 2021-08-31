# -*-coding:utf-8 -*
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in corect dir

import time 
from Test import * 

import logging
import tkinter as tk
from mep import Interface

def main() :
    headp("Testing Interface")
    mep = Mep()
    root = tk.Tk()
    interface = Interface.Application(logger,mep,root)
    
    tested = "waiting_wnd" # window to be tested
    
    if tested == "global_start_wnd":
        interface.global_start_wnd()

    elif tested == "settings_wnd":
        interface.settings_wnd()
    
    elif tested == "get_URL_wnd":
        interface.get_URL_wnd()

    elif tested == "prep_search_wnd":
        interface.prep_search_wnd(mep.artist,mep.title)

    elif tested == "dispaly_infos_wnd":
        interface.dispaly_infos_wnd(mep.track)

    elif tested == "verifications_wnd":
        interface.verifications_wnd()

    elif tested == "ending_wnd":
        interface.ending_wnd()

    elif tested == "dl_wnd_0": #DL WINDOW w/ NO PLAYLIST
        interface.dl_wnd(True)
        interface.dl_status.set("Downloading...\n84%")
        interface.current_dl_name.set("Karma Police")

    elif tested =="dl_wnd_1": #DL WINDOW w/ PLAYLIST
        interface.dl_wnd(False) 
        interface.dl_status.set("Downloading...\n84%")
        interface.current_dl_name.set("1 of 5 : Karma Police")
        interface.playlist_name.set("Ok Computer")

    elif tested == "waiting_wnd" :
        interface.waiting_wnd()
        interface.tmp_cf.set("Karma_police.mp3")
        interface.progress_auto.set("file n°1 out of 3")
    
    #interface.warn("warning")
    #interface.ask("asking")
    

    interface.mainloop()
   

class Mep :
    def __init__(self) :
        self.auto = False
        self.params = {'feat_acronym': 'feat.', 'default_genre': 'Other', 'folder_name': 'music', 'get_label': True, 'get_bpm': True, 'get_lyrics': True, 'store_image_in_file': True}
        self.treated_file_nb = 0
        self.remaining_file_nb = 2
        self.total_file_nb = 3
        
        self.current_info_nb = 0
        self.total_info_nb = 1
        self.current_image_name = "z_tags_tester.jpg"
        self.current_file_name = "karma_police.mp3"
        
        self.artist = "Radiohead"
        self.title = "Karma Police"

        self.a_good_file = [{"entry_title":"karma police", "entry_artist":"radiohead", "":"", "title":"Karma Police", "artist":"Radiohead", "album":"OK Computer"}]

        self.a_maybe_file = [{"entry_title":"could it be magic", "entry_artist":"Barry", "":"", "title":"Could it be magic", "artist":"Barry Manilow", "album":"Barry Manilow I"}]

        self.a_nothing_file = [{"entry_title":"voodoo", "entry_artist":"THe Jimi Hendrix Experience", "":"", "title":"", "artist":"", "album":""}]

        self.track = track = {
                            'name': 'Karma Police',
                            'track_number': 6,
                            'disc_number': 1,

                            'genre': 'Rock',
                            'bpm': 98,
                            'lyrics': {'text':'Karma Police lyrics', 'service':"Genius"},

                            'album' : {
                                'name': 'OK Computer',
                                'release_date': '1997-05-28',
                                'total_tracks': 12,

                                'label':'Radiohead Label',
                                'copyright':'Radiohead copyright'},
                        
                            'artists': [{
                                'name': "Radiohead"}]
                            }
    def update_config(self):
        sys.exit("")
    
    def download(self):
        sys.exit("")

    def make_search(self):
        sys.exit("")
    
    def skip(self):
        sys.exit("")

    def retry(self):
        sys.exit("")

    def update_file(self):
        sys.exit("")

    def prep_reset(self):
        sys.exit("")

    def end_all(self):
        sys.exit("")

    def reset_all(self):
        sys.exit("") 
        


if __name__ == '__main__':
    log_lvl = logging.DEBUG
    logger = logging.getLogger("MEP")
    logger.setLevel(log_lvl)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(log_lvl)
    ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(ch)
    main()
