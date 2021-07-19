# -*-coding:utf-8 -*
import os
import sys
import time

# for file modification
import json   # to parse config file
import shutil  # to move file
import stat   # to change read/write file status

# GUI
import tkinter as tk
from tkinter import Label, Widget, messagebox
from multiprocessing import Process
from tkinter.constants import S
from PIL import Image, ImageTk

# for spotify api
import spotipy  # Spotify API
from spotipy.oauth2 import SpotifyClientCredentials

# formating strings
from slugify import slugify

# Local Libs
import Downloads as dls
import Utilitaries as util
import Tagger




class Application(tk.Frame):
    def __init__(self, master=None, debug=False):
        # Window init
        super().__init__(master) 
        self.master = master
        self.master.geometry('800x500')
        self.master.title("MEProject")
        self.grid()

        # Var init : 
        #local : 
        self.treated_file_nb = 0
        self.remaining_file_nb = 0
        self.total_file_nb = 0
        self.file_nb = 1

        self.not_supported_extension = [".m4a", ".flac", ".mp4", ".wav", ".wma", ".aac"]
        self.supported_extensions = [".mp3"]  # list of all accepted extensions
        
        self.file_extension = [".mp3"]   # will store all file extensions
        self.file_name = ["music.mp3"]   # will store all file names
        self.ignore = ["music.mp3"]

        self.no_playlist = True # for downloading
        self.full_auto = False # unused for now 
        self.logger = self.dl_logger(self)
        
        # Spotify api authorization Secret codes (DO NOT COPY / SHARE)
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fb69ab85a5c749e08713458e85754515",                                                        client_secret= "ebe33b7ed0cd495a8e91bc4032e9edf2")) 
        
        
        # getting info from config file :
        self.params = util.read_config(self)

        self.ADD_SIGN = False # param (maybe changed in config... not sure yet)
        self.DEBUG = debug # param (maybe changed in config... not sure yet)


        if self.ADD_SIGN :
            self.SIGN = "MEP by GM"
        else :
            self.SIGN = "---"

        #temp : 
        #self.dispaly_infos_wnd({'album':{"name":"album name", "release_date": "01-32-50", "total_tracks":"12"}, 'artists':[{"name":"artist name"}], "track_number":"10","name":" track name", "genre":"pop", "lyrics":{"service":"musixmatch"}})
        #self.return_url()
        
        self.tagger = Tagger.Tagger(self.params, self.ADD_SIGN, self.SIGN) 

        self.settings_wnd()
        


    """ Start of GUI """
    def reset_gui(self):
        '''Reset the list of participants'''
        for child in self.winfo_children():
            child.destroy()

    def warn(self, message) :
        if not self.full_auto :
            messagebox.showwarning('Warning', message)
            
    def ask(self,message) :
        if self.full_auto :
            return False 
        else :
            return messagebox.askyesno('Verification',message)

    def global_start_wnd(self):
        self.reset_gui()
        desc = tk.Label(self, text="Select a mode\n")
        desc.grid(row=0,columnspan=4)

        mode_names = ['full auto', 'semi auto','downloads', 'discovery']
        for i in range(0,len(mode_names)):
            button = tk.Button(self, text= mode_names[i], command= lambda x=i: self.mode_selection(x))
            button.grid(row=1, column=i)
        
        button = tk.Button(self, text= "settings", command= self.settings_wnd)
        button.grid(row=2, column=i)    

    def settings_wnd(self) :
        self.reset_gui()
        title = tk.Label(self, text= "Settings").grid(row=0)

        row_nb = 2

        # Checkbox
        self.config = {}
        self.config["get_label"] = tk.BooleanVar(value=self.params["get_label"])
        self.config["get_bpm"] = tk.BooleanVar(value=self.params["get_bpm"])
        self.config["get_lyrics"] = tk.BooleanVar(value=self.params["get_lyrics"])
        self.config["store_image_in_file"] = tk.BooleanVar(value=self.params["store_image_in_file"])

        lst = [["get_label", "search for the artist label"],
               ["get_bpm","search for the bpm"],
               ["get_lyrics","search for the lyrics (can slow the program slightly)"],
               ["store_image_in_file","include image in file (if unchecked image will just be placed within the album folder)"]]
            
        for i in range(len(lst)) :
            tk.Checkbutton(self, anchor="nw", width=70, text=lst[i][1],var= self.config[lst[i][0]]).grid(row = row_nb+i,columnspan=2)
        
        row_nb += i + 2
        tk.Label(self, text="").grid(row=row_nb-1) #spacing
        
        # Entries
        lst = [["folder_name", "folder name (can be a simple name or a path)"],["feat_acronym", "featuring acronym"], ["default_genre", "default genre"]]
        
        for i in range(len(lst)) :
            tk.Label(self, width= 40, anchor="nw", text=" " + lst[i][1]).grid(row=row_nb+i)
            self.config[lst[i][0]] = tk.Entry(self, width = 30)
            self.config[lst[i][0]].insert(0, self.params[lst[i][0]])
            self.config[lst[i][0]].grid(row=row_nb+i,column=1)

        # Button
        tk.Button(self, padx=20, text = "Ok", command= lambda : self.update_config).grid(row=row_nb+i+1, columnspan=2)
    
    #window before download
    def get_URL_wnd(self):
        self.reset_gui()
        self.playlist = tk.BooleanVar()
        self.playlist_cb = tk.Checkbutton(self, text='Whole playlist ?',var= self.playlist)
        self.playlist_cb.grid(row = 0)
        self.input_url = tk.Entry(self,width=60)
        self.input_url.grid(row = 1)
        self.input_url.focus()
        self.download_bt = tk.Button(self, text= "Download", command= self.return_url)
        self.download_bt.grid(row = 2)

    # window during download
    def dl_wnd(self, no_playlist) :
        print("starting window")

        self.reset_gui()
        self.title_lb = tk.Label(self,text=" Downloading screen")
        self.title_lb.grid(row=1)
        self.status_lb = tk.Label(self, text="State : Starting download")
        self.status_lb.grid(row=5)

        if not no_playlist :
            self.playlist_lb = tk.Label(self, text="Playlist : TBD")
            self.playlist_lb.grid(row=3)
            self.current_file_lb = tk.Label(self, text="Current file : TBD")
            self.current_file_lb.grid(row= 4)
            return self.dl_wp
            while self.dl_not_ended :
                self.dl_wp() # used to update page in real time but doesn't work
                #TODO Patch bug !

        else :
            self.current_file_lb = tk.Label(self, text="Current file : TBD")
            self.current_file_lb.grid(row= 3)
            return self.dl_wop
            while self.dl_not_ended :
                self.dl_wop()


    def dl_wp(self) :
        self.playlist_lb.config(text="Playlist : " + self.playlist_title)
        self.current_file_lb.config(text="Current file : " + self.current_dl)
        self.status_lb.config(text="State : " + self.status)

    def dl_wop(self) :
        self.current_file_lb.config(text="Current file : " + self.current_dl)
        self.status_lb.config(text="State : " + self.status)

    def prep_search_wnd(self, artist, title) :
        self.reset_gui()
        self.actual_file  = tk.Label(self, text="file : "+self.current_file_name)
        self.actual_file.grid(columnspan=2)

        self.title_lb = tk.Label(self, text="title : ")
        self.title_lb.grid(row=1)
        self.title_ent = tk.Entry(self, width = 30)
        self.title_ent.insert(0, title)
        self.title_ent.grid(row=1,column=1)
    
        self.artist_lb = tk.Label(self, text="artist : ")
        self.artist_lb.grid(row=2)
        self.artist_ent = tk.Entry(self, width = 30)
        self.artist_ent.insert(0, artist)
        self.artist_ent.grid(row=2,column=1)

        self.go_bt = tk.Button(self, text="Go!",command=lambda: self.make_search())
        self.go_bt.grid(row=3,columnspan=2)
    
    def dispaly_infos_wnd(self,track) :
        self.reset_gui()
        self.actual_file  = tk.Label(self, text="file : "+self.current_file_name+"\n")
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
              ("Track number", str(track['track_number'])+" out of "+str(track['album']['total_tracks']))]

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
        imagedata = Image.open(self.current_image_name)
        imagedata = imagedata.resize((row_nb*39,row_nb*39), Image.ANTIALIAS)
        self.imagedata =  ImageTk.PhotoImage(imagedata)
        artwork = tk.Label(self, image=self.imagedata,relief=tab_relief)
        artwork.grid(row=3,rowspan= row_nb, column=2)


        #different buttons
        button = tk.Button(self, text= "skip", command=lambda: self.skip())
        button.grid(row=4+row_nb,pady=15, column=0)
        
        button = tk.Button(self, text= "retry", command=lambda: self.retry())
        button.grid(row=4+row_nb, column=1)
        
        button = tk.Button(self, text= "ok", command=lambda: self.update_file(track))
        button.grid(row=4+row_nb, column=2)

        button = tk.Button(self, text="next match", command=lambda : self.next_match())
        button.grid(row=5, column=4)

    def ending_wnd(self) : 
        self.reset_gui()
        label = tk.Label(self, text="All done !")
        label.grid(columnspan=2)
        label = tk.Label(self, text="{} files treated out of {} total".format(self.total_file_nb, self.treated_file_nb))
        label.grid(row=2,columnspan=2)

        button = tk.Button(self, text= "End", command=lambda: self.end_all())
        button.grid(row=3,pady=15, column=0)
        
        button = tk.Button(self, text= "Go again", command=lambda: self.reset_all())
        button.grid(row=3, column=1)

    
    """ For youtube-dl infos """
    class dl_logger(object):
        def __init__(self, app):
            self.app = app
            self.video_nb = "video:"
            self.playlist_title = ""

        def debug(self,msg):
            #print(msg)
            if "[download] Downloading playlist" in msg:
                self.app.playlist_title = msg.replace("[download] Downloading playlist: ","").strip()#"playlist: playlist_name"
                
            elif "[download] Downloading" in msg :
                self.video_nb = msg.replace("[download] Downloading ","")+" :" #"video 1 of 12 :""
            elif "[download] Destination:" in msg:
                self.video_title, _ = os.path.splitext(msg.replace("[download] Destination: yt-DL_",""))
                self.app.current_dl = "%s %s"%(self.video_nb, self.video_title)

        def warning(self,msg):
            pass

        def error(self, msg) :
            print(msg)

    def dl_hook(self, d) : 
        if d['status'] == 'finished':
            self.status = "Done downloading, now converting"
    
    def temp(self,url, no_playlist) :
        print("starting dl")
        dls.dl_music(url,no_playlist,self.logger,[self.dl_hook])
        self.status = "All done !"
        time.sleep(0.03)
        self.dl_not_ended = False


    """ Actual prog """ 
    def update_config(self):
        pass

    def mode_selection(self, mode_nb):
        if mode_nb == 0 :
            self.auto_disp()
        elif mode_nb == 1 :
            self.params['all_Auto'] = False
            self.params['Assume_mep_is_right'] = True
            self.params['Open_image_auto'] = False
            self.scan_folder()
        elif mode_nb == 2 : 
            self.get_URL_wnd()
        else :
            self.deprecated()
         
    def manual_tagging(self):
        self.warn("manual tagging not yet implemented")
        self.skip()

    def retry(self) : 
        #TODO add info msg ?
        self.prep_search_wnd()  

    def return_url(self) :
        # getting info
        url=self.input_url.get()
        no_playlist = not self.playlist.get()
        
        """ Testing multithreading to fix issue (not working when tested)
        url = "https://www.youtube.com/watch?v=49FB9hhoO6c"
        no_playlist = True

        #Starting DL (working but window is lagging )
        self.dl_not_ended = True
        self.playlist_title = ""
        self.current_file = ""
        self.status = "Downloading"

        p1 = Process(target=self.dl_wnd(no_playlist))
        p1.start()
        p2 = Process(target=self.temp(url, no_playlist))
        p2.start()
        p1.join()
        p2.join()"""
        renew_window = self.dl_wnd(no_playlist)

        self.temp(url, no_playlist)
        renew_window()
        time.sleep(1)
        
        # Resuming normal process
        self.scan_folder()

    
    def scan_folder(self) :
        # scanning folder
        wrong_format = False
        for temp_file_name in os.listdir():
            _ , temp_file_extension = os.path.splitext(temp_file_name)

            if temp_file_extension in self.supported_extensions and temp_file_name not in self.ignore:
                self.file_name.append(temp_file_name)
                self.file_extension.append(temp_file_extension)
                self.remaining_file_nb += 1

            elif (temp_file_extension in self.not_supported_extension):
                wrong_format = True
                wrong_file_name = temp_file_name

        # saving total number
        self.total_file_nb = self.remaining_file_nb

        if wrong_format:
            self.warn("file " + wrong_file_name +" format unsupported")
            time.sleep(4)
            state = 10

        elif self.total_file_nb <= 0:  # no music file was found
            self.warn("no music file found")
            self.ending_wnd()

        else : 
            self.scan_data()
    
    def scan_data(self):
        # trying to see if there are correct tags
        self.current_file_name = self.file_name[self.file_nb]
        title, artist, encoded_by = self.tagger.read_tags(self.current_file_name)

        if type(title) != type(None):
            title = util.remove_feat(title) 
        else :
            title = ""
        if type(artist) == type(None) or artist == "None":
            artist = ""            
        
        # checks wether program already processed file (TODO delete ?)
        if encoded_by == self.params['signature']:
            if not self.ask(" file : " + self.current_file_name + " has already been treated. Do you want to change something ?") :
                self.move_file()  # just moving the file in correct directory 
        
        self.prep_search_wnd(artist, title)

    def make_search(self):
        
        title = self.title_ent.get()
        artist = self.artist_ent.get()
        
        search = "track:" + title.replace("'", "") + " artist:" + artist
        results = self.sp.search(q= search, type = "track", limit = 4)
        items = results['tracks']['items']
        self.nb_search = 0
        # Can a result be found
        if len(items) > 0:
            for i in range(len(items)) :
                if (items[i]['album']['artists'][0]['name'] == 'Various Artists') :
                    items.pop(i) # removing because it was a playlist TODO maybe add better checks
                    i -= 1
                else :

                    items[i]['name'] = util.remove_feat(items[i]['name'])  # in case of featuring
                    items[i]['album']['artwork'] = items[i]['album']['images'][0]['url']
                    items[i]['lyrics'] = {}
            self.all_tracks = items
            self.get_genre(items[0]) 
        #TODO all_auto
        else :
            # trying without the artist only if user can verify
            search = "track:" + title.replace("'", "")
            results = self.sp.search(q=search, type = "track", limit = 5)
            items = results['tracks']['items']
            if len(items) > 0:
                for i in range(len(items)) :
                    items[i]['name'] = util.remove_feat(items[i]['name'])  # in case of featuring
                    items[i]['album']['artwork'] = items[i]['album']['images'][0]['url']
                    items[i]['lyrics'] = {}
                self.all_tracks = items
                self.get_genre(items[0])

            else :
                if self.ask("No match found. Retry with different spelling ?"):
                    self.prep_search_wnd(artist, title)
                else :
                    self.skip()
        
    def next_match(self) :
        os.remove(self.current_image_name)
        self.nb_search += 1
        if self.nb_search < len(self.all_tracks):
            self.get_genre(self.all_tracks[self.nb_search])
        else :
            self.warn("no more results")
            self.nb_search = 0
            self.get_genre(self.all_tracks[0])

    #track = {'album':{"name":"OK Computer", "release_date": "1997-05-28", "total_tracks":"12"}, 'artists':[{"name":artist}], "track_number":"4","name":title, "genre":"alternative rock", "lyrics":{"service":"musixmatch"}}
    def get_genre(self, track):

        # getting genre
        results = self.sp.artist(track['artists'][0]['id'])
        if len(results['genres']) > 0:
            track['genre'] = results['genres'][0]
        else:
            track['genre'] = self.params['default_genre']

        # getting label and copyright
        if self.params['get_label']:
            results = self.sp.album(track['album']['id'])
            if len(results) > 0:
                track['album']['copyright'] = results['copyrights'][0]['text']
                track['album']['label'] = results['label']
            else:
                # default
                track['album']['copyright'] = ""
                track['album']['label'] = ""

        # getting BPM
        if self.params['get_bpm']:
            results = self.sp.audio_analysis(track['id'])
            if len(results) > 0:
                track['bpm'] = int(results['track']['tempo'])
            else:
                track['bpm'] = 0  # default

        #getting lyrics 
        if self.params['get_lyrics']: 
            (track['lyrics']['text'], track['lyrics']['service']) = util.get_lyrics(track['artists'][0]['name'], track['name'])
        else :
            track['lyrics']['service'] = "ignored"
            track['lyrics']['text'] =  ""

        # downloading image 
        tmp = slugify(track['album']['name']+"_artwork")+".jpg"
        self.current_image_name = dls.dl_image(track['album']['artwork'], tmp, self)
        
        self.dispaly_infos_wnd(track)

    def update_file(self, track) :
        try :
            # making sure the file is writable :
            os.chmod(self.current_file_name, stat.S_IRWXU)

            # preparing new file name and directory path 
            if track['track_number'] != None :
                if track['track_number'] < 10 :
                    new_file_name = "0" + str(track['track_number']) + "-" + slugify(track['name'],separator='_') 
                else :
                    new_file_name = str(track['track_number']) + "-" + slugify(track['name'],separator='_')
            else :
                new_file_name = slugify(track['name'],separator='_')
            new_file_name = new_file_name + self.file_extension[self.file_nb]  #adding extension

            # changing name of the file
            os.path.realpath(self.current_file_name)
            os.rename(self.current_file_name, new_file_name)
            self.current_file_name = new_file_name  

            # adding featured artist to title 
            nb_artist = len(track['artists'])
            if nb_artist == 2:
                track['name'] = track['name']+" ("+self.params['feat_acronym']+track['artists'][1]['name']+")"  # correct title
            elif nb_artist > 2:
                track['name'] = track['name']+" ("+self.params['feat_acronym']+track['artists'][1]['name']+ \
                                                " & "+track['artists'][2]['name']+")"  # correct title
            
            # modifying the tags
            ret = self.tagger.update_tags(self.current_file_name, self.current_image_name, track)
            
        except FileNotFoundError :
            self.warn("File was moved. Skipping file")            
            self.skip()  # skipping file          
        except Exception as e :
            print(e.args)
            self.warn("File couldn't be edited. Skipping file") 
            self.skip()  # skipping file 
        
        if ret > 0 :
            self.warn("error during tagging. Skipping file")
            self.skip()
        else :
            self.move_file(self.params['folder_name']+os.path.sep+util.slugify(track['artists'][0]['name'], separator=" ",lowercase=False)+os.path.sep+util.slugify(track['album']['name'], separator=" ",lowercase=False))
            

    def move_file(self, direction) :
        try :
            if os.path.exists(direction+os.path.sep+self.current_file_name) :
                self.warn("file already exists in folder \nkeeping this file in main folder")
                self.ignore.append(self.current_file_name)
            else :
                if not os.path.exists(direction):
                    os.makedirs(direction) #creating folder

                shutil.move(self.current_file_name, direction) # place music file in correct folder
                if not self.params['store_image_in_file'] :
                    if not os.path.exists(direction+os.path.sep+self.current_image_name) :
                        shutil.move(self.current_image_name,direction) #place album cover in correct folder
                    else :
                        os.remove(self.current_image_name) #removing if already present

                self.treated_file_nb += 1  # file correctly treated

        except Exception as e:
            self.warn("Unexpected error:" + sys.exc_info()[0] + "\nkeeping this file in main folder")
            
        if self.remaining_file_nb > 1:
            self.file_nb += 1  # file being treated = next in the list
            self.remaining_file_nb -= 1  # one file done
            self.scan_data() 
        else:
            self.ending_wnd()  # Ending program (or restarting)

    def skip(self) :
        
        if self.ask("Do you want to fill tags manually ?") :
            self.manual_tagging()
        else :
            self.ignore.append(self.current_file_name)
            if self.remaining_file_nb > 1:
                self.file_nb += 1  # file being treated = next in the list
                self.remaining_file_nb -= 1  # one file done
                self.current_file_name = self.file_name[self.file_nb]
                self.scan_data() 
            else:
                self.ending_wnd() # Ending program (or restarting)

    def reset_all(self) :
            # reseting variables
            self.file_extension = [".mp3"]
            self.file_name = ["music.mp3"]
            self.file_nb = 1
            self.remaining_file_nb = 0
            self.total_file_nb = 0
            self.treated_file_nb = 0
            self.global_start_wnd()
            
    def end_all(self) :
        sys.exit("")

    def deprecated(self) :
        pass

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root,debug=True)
    app.mainloop()


