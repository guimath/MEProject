#!/usr/bin/env python
# coding: utf-8 

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in correct dir

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
    mep.interface = interface
    # global_start_wnd - settings_wnd - prep_search_wnd - get_URL_wnd
    # dispaly_infos_wnd - verifications_wnd - ending_wnd
    # dl_wnd_0 - dl_wnd_1 - waiting_wnd

    mep.tested = "global_start_wnd" # window to be tested
    launch_wnd(mep.tested, interface, mep)

def launch_wnd(tested, interface, mep) :

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

    elif tested == "select_dls_wnd":
        interface.select_dls_wnd(mep.lst, "Playlist name here")
        
    elif tested == "dl_wnd_0": #DL WINDOW w/ NO PLAYLIST
        interface.dl_wnd(True)
        interface.dl_status.set("Downloading...\n84%")
        interface.current_dl_name.set("Karma Police")
        interface.update()
        time.sleep(1)
        interface.dl_status.set("Converting")

    elif tested =="dl_wnd_1": #DL WINDOW w/ PLAYLIST
        interface.dl_wnd(False) 
        interface.dl_status.set("Downloading...\n84%")
        interface.current_dl_name.set("1 of 3 : Karma Police")
        interface.playlist_name.set("Ok Computer")
        interface.update()
        time.sleep(2)
        interface.dl_status.set("Converting")
        interface.current_dl_name.set("2 of 3 : No Surprises")


    elif tested == "waiting_wnd" :
        interface.waiting_wnd()
        interface.current_file.set("Karma_police.mp3")
        interface.progress.set("file n°1 out of 3")
        interface.update()
        time.sleep(2)
        interface.current_file.set("No_surprises.mp3")
        interface.progress.set("file n°2 out of 3")
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
        self.tested = ""
        self.nb = 0

        self.TESTS = ['global_start_wnd', 'settings_wnd', 'prep_search_wnd', 'get_URL_wnd', 'dispaly_infos_wnd', 'verifications_wnd', 'ending_wnd','dl_wnd_0', 'dl_wnd_1', 'waiting_wnd']
        
        self.current_info_nb = 0
        self.total_info_nb = 1
        self.current_image_name = "z_tags_tester.jpg"
        self.current_file_name = "karma_police.mp3"
        
        self.artist = "Radiohead"
        self.title = "Karma Police"

        self.a_good_file = [{"entry_title":"karma police", "entry_artist":"radiohead", "":"", "title":"Karma Police", "artist":"Radiohead", "album":"OK Computer"}]
        #self.a_good_file = [{"entry_title":"karma police o o o o o o o o o p", "entry_artist":"radiohead a b d e ezgeg gh hs q qfsf esf sef\n i \n i \n u \n u \n k \n i \n i \n u \n u \n k \n i \n i \n u \n u \n k \n i \n i \n u \n u \n k \n i \n i \n u \n u \n k \n i \n i \n u \n u \n k \n", "":"", "title":"Karma Police p o i h h h g t f hy j y f k", "artist":"Radiohead pio jh h f d de s  g h f d r  f gf d ", "album":"OK Computer o j u hg g f d d s  s s d d "}]

        self.a_maybe_file = [{"entry_title":"could it be magic", "entry_artist":"Barry", "":"", "title":"Could it be magic", "artist":"Barry Manilow", "album":"Barry Manilow I"}]

        self.a_nothing_file = [{"entry_title":"voodoo", "entry_artist":"THe Jimi Hendrix Experience", "":"", "title":"", "artist":"", "album":""}]

        self.track = track = {
                            'name': 'Karma Police',# Remastered new edition remix updated mixtape 2020 version
                            'track_number': 6,
                            'disc_number': 1,

                            'genre': 'Rock',
                            'bpm': 98,
                            'lyrics': {'text':'Karma Police lyrics', 'service':"Genius"},

                            'album' : {
                                'name': 'OK Computer  ',
                                'release_date': '1997-05-28',
                                'total_tracks': 12,

                                'label':'Radiohead Label',
                                'copyright':'Radiohead copyright'},
                        
                            'artists': [{
                                'name': "Radiohead"}]
                            }
    
        self.lst = [{'title': 'Joji - SLOW DANCING IN THE DARK', 'uploader': '88rising', 'duration': '3min 38s', 'id': 0}, {'title': 'Childish Gambino - Feels Like Summer', 'uploader': 'Donald Glover', 'duration': '4min 46s', 'id': 1}, {'title': 'FKJ & Masego - Tadow', 'uploader': 'Fkj', 'duration': '8min 7s', 'id': 2}, {'title': 'Childish Gambino - Redbone (Official Audio)', 'uploader': 'Donald Glover', 'duration': '5min 27s', 'id': 3}, {'title': 'The Weeknd - Call Out My Name (Official Video)', 'uploader': 'The Weeknd', 'duration': '3min 59s', 'id': 4}, {'title': 'Jorja Smith - Be Honest (feat. Burna Boy)', 'uploader': 'Jorja Smith', 'duration': '4min 21s', 'id': 5}, {'title': 'Daniel Caesar - Get You ft. Kali Uchis [Official Video]', 'uploader': 'Daniel Caesar', 'duration': '4min 31s', 'id': 6}, {'title': 'Giveon - Like I Want You (Official Music Video)', 'uploader': 'Givēon', 'duration': '5min 5s', 'id': 7}, {'title': 'The Weeknd - I Feel It Coming ft. Daft Punk (Official Video)', 'uploader': 'The Weeknd', 'duration': '4min 58s', 'id': 8}, {'title': 'Khalid - Better (Official Video)', 'uploader': 'Khalid', 'duration': '4min 11s', 'id': 9}, {'title': "Alicia Keys & John Mayer - If I ain't got you - Gravity (Better audio quality)", 'uploader': 'didjital vibe', 'duration': '9min 15s', 'id': 10}, {'title': 'Michael Kiwanuka - Cold Little Heart (Official Video)', 'uploader': 'Michael Kiwanuka', 'duration': '6min 20s', 'id': 11}, {'title': 'Amy Winehouse - Back To Black', 'uploader': 'Amy Winehouse', 'duration': '4min 8s', 'id': 12}]
    def next_wnd(self) :
        self.nb +=1
        launch_wnd(self.TESTS[self.nb],self.interface, self)

    def mode_selection(self,x):
        self.next_wnd()
    
    def update_config(self):
        self.next_wnd()
    
    def download(self):
        self.next_wnd()

    def make_search(self):
        self.next_wnd()
    
    def skip(self):
        self.next_wnd()

    def retry(self):
        self.next_wnd()

    def update_file(self, trck):
        self.next_wnd()

    def prep_reset(self):
        self.next_wnd()

    def end_all(self):
        self.next_wnd()

    def reset_all(self):
        self.next_wnd()
        


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
