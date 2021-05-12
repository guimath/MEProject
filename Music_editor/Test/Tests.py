"""from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
import unicodedata

from slugify import slugify

import youtube_dl
import pprint
import json
import os
import shutil
import string"""

import os
import time
import tkinter as tk
from tkinter import Label, messagebox
import threading
from Downloads import *
from PIL import Image, ImageTk

class Application(tk.Frame):
    def __init__(self, master=None, debug=False):
        super().__init__(master)
        self.master = master
        self.master.geometry('800x500')
        self.master.title("MEProject")
        self.grid()
        self.debug = debug
        self.full_auto = False

        self.filename = "music.mp3"
        #self.dispaly_infos({'album':{"name":"album name", "release_date": "01-32-50", "total_tracks":"12"}, 'artists':[{"name":"artist name"}], "track_number":"10","name":" track name", "genre":"pop", "lyrics":{"service":"musixmatch"}})
        self.global_start()

    def reset(self):
        '''Reset the list of participants'''
        for child in self.winfo_children():
            child.destroy()

    def ask(self,message) :
        if self.full_auto :
            return False 
        else :
            return messagebox.askyesno('Warning',message)

    def global_start(self):
        self.desc = tk.Label(self, text="Select a mode\n")
        self.desc.grid(row=0,columnspan=4)
        self.mode_bt = []
        mode_names = ['full auto', 'semi auto','downloads', 'discovery']
        for i in range(0,len(mode_names)):
            self.mode_bt.append(tk.Button(self, text= mode_names[i], command= lambda x=i: self.mode_selection(x)))
            self.mode_bt[i].grid(row=1, column=i)
    
    def mode_selection(self, mode_nb):
        if mode_nb == 0 :
            self.auto_disp()
        elif mode_nb == 1 :
            self.title = "Exit Music (For A Film)"
            self.artist = "Radiohead"

            self.prep_search()
        elif mode_nb == 2 : 
            self.get_URL()
        else :
            self.deprecated()

    def prep_search(self) :
        self.reset()
        self.actual_file  = tk.Label(self, text="file : "+self.filename)
        self.actual_file.grid(columnspan=2)

        self.title_lb = tk.Label(self, text="title : ")
        self.title_lb.grid(row=1)
        self.title_ent = tk.Entry(self, width = 30)
        self.title_ent.insert(0,self.title)
        self.title_ent.grid(row=1,column=1)
    
        self.artist_lb = tk.Label(self, text="artist : ")
        self.artist_lb.grid(row=2)
        self.artist_ent = tk.Entry(self, width = 30)
        self.artist_ent.insert(0,self.artist)
        self.artist_ent.grid(row=2,column=1)

        self.go_bt = tk.Button(self, text="Go!",command=lambda: self.make_search())
        self.go_bt.grid(row=3,columnspan=2)
    
    def dispaly_infos(self,track) :
        self.reset()
        self.actual_file  = tk.Label(self, text="file : "+self.filename+"\n")
        self.actual_file.grid(columnspan=3)

        #formating title
        nb_artist = len(track['artists'])
        if nb_artist == 1:  # no feat
            title = "%s by %s" %(track['name'], track['artists'][0]['name'])

        elif nb_artist == 2:
            title = "%s by %s featuring %s" %(track['name'], track['artists'][0]['name'], track['artists'][1]['name'])

        else:
            title = "%s by %s featuring %s & %s" %(track['name'], track['artists'][0]['name'], track['artists'][1]['name'], track['artists'][2]['name'])


        #creating list of info to simplify display
        ls = [("album",track['album']['name']),
              ("Genre", track['genre']),
              ("release date", track['album']['release_date']),
              ("Track number", track['track_number']+" out of "+track['album']['total_tracks'])]

        lyrics = track['lyrics']['service']
        if lyrics != "ignored" :
            ls.append(("lyrics", lyrics))
    
        row_nb = len(ls)
        max_len = 0
        tab_relief = "solid"
        
        for i in range(row_nb):
            # line title
            self.track_infos = tk.Label(self, text=ls[i][0],anchor=tk.constants.W, relief=tab_relief, height=2, width=13)
            self.track_infos.grid(row= i+3,column=0)
            #calculating max length 
            temp_len = len(ls[i][1])
            if temp_len > max_len :
                max_len = temp_len
        # info
        for i in range(row_nb):
            self.track_infos = tk.Label(self, text=ls[i][1],anchor=tk.constants.W, relief=tab_relief, height=2, width=max_len)
            self.track_infos.grid(row= i+3,column=1)

        #table title
        self.t_and_a_lb = tk.Label(self, text=title, relief=tab_relief, width= 14+max_len+row_nb*5)
        self.t_and_a_lb.grid(row=2,columnspan=3)

        #album artwork
        imagedata = Image.open("image.png")
        imagedata = imagedata.resize((row_nb*39,row_nb*39), Image.ANTIALIAS)
        self.imagedata =  ImageTk.PhotoImage(imagedata)
        self.artwork = tk.Label(self, image=self.imagedata,relief=tab_relief)
        self.artwork.grid(row=3,rowspan= row_nb, column=2)


        #different buttons
        self.button = tk.Button(self, text= "skip", command=lambda: self.skip())
        self.button.grid(row=4+row_nb,pady=15, column=0)
        
        self.button = tk.Button(self, text= "retry", command=lambda: self.retry())
        self.button.grid(row=4+row_nb, column=1)

        self.button = tk.Button(self, text= "ok", command=lambda: self.update_file())
        self.button.grid(row=4+row_nb, column=2)

    def make_search(self):
        
        self.title = self.title_ent.get()
        self.artist = self.artist_ent.get()
        # spotify search TODO
        track = {'album':{"name":"OK Computer", "release_date": "1997-05-28", "total_tracks":"12"}, 'artists':[{"name":self.artist}], "track_number":"4","name":self.title, "genre":"alternative rock", "lyrics":{"service":"musixmatch"}}
        self.dispaly_infos(track) 
         
    def manual_tagging(self):
        print("manual tagging not yet implemented")
        self.skip()

    def skip(self) :
        
        if self.ask("fill manually ?") :
            self.manual_tagging()
        else :
            #TODO skipping
            self.prep_search()  

    def retry(self) : 
        #TODO add info msg ?
        self.prep_search()  

    def update_file(self) : 
        #TODO update 
        print("file correctly proccessed")
        self.prep_search()

    def get_URL(self):
        self.reset()
        self.playlist = tk.BooleanVar()
        self.playlist_cb = tk.Checkbutton(self, text='Whole playlist ?',var= self.playlist)
        self.playlist_cb.grid(row = 0)
        self.input_url = tk.Entry(self,width=60)
        self.input_url.grid(row = 1)
        self.input_url.focus()
        self.download_bt = tk.Button(self, text= "Download", command= self.return_url)
        self.download_bt.grid(row = 2)

    def return_url(self) :

        url=self.input_url.get()
        no_playlist = not self.playlist.get()
        self.reset()
        self.label = tk.Label(self, text="")
        self.label.grid(row=1)
        self.current_file = tk.Label(self, text="")
        self.current_file.grid(row= 2)
        dl_music(url,no_playlist,self.dl_logger(self),[self.dl_hook])
        self.dl_window_state("All done !")
        time.sleep(0.5)
        self.scan_folder()

    def dl_window_playlist(self, playlist_title) :
        self.playlist_title = tk.Label(self, text="playlist : "+playlist_title).grid()

    def dl_window_video_info(self, txt) :
        print(txt)
        self.label.config(text=txt)

    def dl_window_state(self, txt):
        print("STATE : " + txt)
        self.current_file.config(text=txt)

    """For youtube-dl infos """
    class dl_logger(object):
        def __init__(self, app):
            self.app = app
            self.video_nb = "video:"
            self.playlist_title = ""

        def debug(self,msg):
            print(msg)
            if "[download] Downloading playlist" in msg:
                playlist_title = msg.replace("[download] Downloading playlist: ","").strip()#"playlist: playlist_name"
                self.app.dl_window_playlist(playlist_title)
                
            elif "[download] Downloading" in msg :
                self.video_nb = msg.replace("[download] Downloading ","")+" :" #"video 1 of 12 :""
            elif "[download] Destination:" in msg:
                self.video_title, _ = os.path.splitext(msg.replace("[download] Destination: yt-DL_",""))
                self.app.dl_window_video_info("%s %s"%(self.video_nb, self.video_title))

        def warning(self,msg):
            pass

        def error(self, msg) :
            print(msg)

    def dl_hook(self, d) : 
        if d['status'] == 'finished':
            self.dl_window_state("Done downloading, now converting")
            

    def deprecated(self) :
        pass

root = tk.Tk()

app = Application(master=root,debug=True)
app.mainloop()



"""
title = "Morose"
artist = "Damso"
search = ("Genius %s by %s" %(title, artist)).replace(" ", "+")

url_search = "https://www.google.com/search?client=opera&q=%s&sourceid=opera&ie=UTF-8&oe=UTF-8" %(search)
header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"}
resp = requests.get(url_search,headers = header)
"""

'''
class GeniusCrawler(Crawler):
    def __init__(self):
        super().__init__('Genius Lyric')

    def search_for_lyrics(self, artist, song):
        try:
            _artist = str(artist).strip().replace(' ', '-').replace("'", '')
            _name_song = song.strip().replace(' ', '-').replace("'", '')
            song_url = '{}-{}-lyrics'.format(_artist, _name_song)
            request = requests.get("https://genius.com/{}".format(song_url))

            html_code = BeautifulSoup(request.text, features="html.parser")
            lyric = html_code.find("div", {"class": "lyrics"}).get_text()

            return self.format_lyrics(lyric)

        except Exception as e:
            self.raise_not_found()

    
    def format_lyrics(self, lyric):
        lines = map(
            lambda line: line if ']' not in line and '[' not in line else None,
            lyric.split('\n')
        )
        lines = filter(
            lambda line: line is not None,
            list(lines)
        )
        return list(lines) 

def split_to_word(string):
    return string.replace("\n", " ").replace("\r", " ").split(" ")'''


