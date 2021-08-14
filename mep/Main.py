# -*-coding:utf-8 -*

import os
import sys
import time

# for file modification
import shutil  # to move file
import stat   # to change read/write file status

# GUI
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

#logging 
import logging 
import inspect

# formating strings
from slugify import slugify

# Local Libs
import Downloads as dls
import Utilitaries as util
from Tagger import Tagger
from Info_search import Info_search

class Application(tk.Frame):
    def __init__(self, master=None):
        #logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)

        # Window init
        super().__init__(master) 
        self.master = master
        self.master.geometry('800x500')
        self.master.title("MEProject")
        self.grid()
        self.auto = False
        self.global_start_wnd()

        
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
       
        # getting info from config file :
        self.params = util.read_config(self)

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

        # CLASS        
        self.logger = self.dl_logger(self)        
        self.web = Info_search(self.params) 
        self.tagger = Tagger(self.params, self.ADD_SIGN, self.SIGN) 
        

    """ -----------------------------------------------
        --------------- Start of GUI  -----------------
        ----------------------------------------------- 
    """
    def reset_gui(self):
        for child in self.winfo_children():
            child.destroy()

    def warn(self, message) :
        if not self.auto :
            messagebox.showwarning('Warning', message)
            
    def ask(self,message) :
        if self.auto :
            return False 
        else :
            return messagebox.askyesno('Verification',message)

    # Start screen (User picks a mode)
    def global_start_wnd(self):
        self.reset_gui()
        #TODO Re do 
        tk.Label(self, text="Select a mode\n").grid(row=0,columnspan=4)

        mode_names = ['Automatically go through a\nlarge music library', 'fill music tags for a few\nfiles','download music\nfrom youtube URL']
        for i in range(0,len(mode_names)):
            tk.Button(self, text= mode_names[i], command= lambda x=i: self.mode_selection(x)).grid(row=1, column=i)
        
        tk.Label(self).grid(row=2)
        tk.Button(self, text= "settings", command= self.settings_wnd).grid(row=3, column=1)    

    # User can see/modify settings
    def settings_wnd(self) :
        self.reset_gui()
        tk.Label(self, text= "Settings").grid(row=0,columnspan=2)
        row_nb = 2

        # Checkbox
        lst = ["get_label", "get_bpm","get_lyrics", "store_image_in_file"]
        self.config = {}
        for key in lst :
            self.config[key] = tk.BooleanVar(value=self.params[key])

        lst = [["get_label", "search for the artist label"],
               ["get_bpm","search for the bpm"],
               ["get_lyrics","search for the lyrics (can slow the program slightly)"],
               ["store_image_in_file","include image in file (if unchecked image will just be placed within the album folder)"]]
        for i in range(len(lst)) :
            tk.Checkbutton(self, anchor="nw", width=70, text=lst[i][1],var= self.config[lst[i][0]]).grid(row = row_nb+i,columnspan=2)
        
        # Spacing
        row_nb += i + 2
        tk.Label(self, text="").grid(row=row_nb-1)
        
        # Entries
        lst = [["folder_name", "folder name (can be a simple name or a path)"],["feat_acronym", "featuring acronym"], ["default_genre", "default genre"]]
        for i in range(len(lst)) :
            tk.Label(self, width= 40, anchor="nw", text=" " + lst[i][1]).grid(row=row_nb+i)
            self.config[lst[i][0]] = tk.Entry(self, width = 30)
            self.config[lst[i][0]].insert(0, self.params[lst[i][0]])
            self.config[lst[i][0]].grid(row=row_nb+i,column=1)

        # Button
        tk.Button(self, padx=20, text = "Save", command= self.update_config).grid(row=row_nb+i+1, columnspan=2)
    
    # DL : user picks URL
    def get_URL_wnd(self):
        self.reset_gui()

        self.playlist = tk.BooleanVar()
        tk.Checkbutton(self, text='Whole playlist ?',var= self.playlist).grid(row = 0)
        
        self.input_url = tk.Entry(self,width=60)
        self.input_url.grid(row = 1)
        self.input_url.focus()
        tk.Button(self, text= "Download", command= self.download).grid(row = 2)

    # DL : keeps user informed about the download process
    def dl_wnd(self, no_playlist) :
        self.reset_gui()

        # create variables that will change during download
        self.dl_status = tk.StringVar(value="Starting process")  
        self.current_dl_name = tk.StringVar(value="Current file : TBD")
        self.playlist_name = tk.StringVar(value="Playlist : TBD")

        # Common to both 
        tk.Label(self,text=" Downloading screen\n").grid(row=1, columnspan=2)
        tk.Label(self, text="State : ", height=2).grid(row=5)
        tk.Label(self, textvariable=self.dl_status, width=20,anchor="nw").grid(row=5, column=1)

        #specific
        if no_playlist :
            tk.Label(self, text="Current file :").grid(row=3)
            tk.Label(self, width=30, anchor="nw", textvariable=self.current_dl_name).grid(row= 3, column=1)

        else :
            tk.Label(self, text="Playlist : ").grid(row=3)
            tk.Label(self, textvariable=self.playlist_name).grid(row=3, column=1)
            tk.Label(self, text="Current file : ").grid(row=4)
            tk.Label(self, width=30, anchor="nw", textvariable=self.current_dl_name).grid(row= 4, column=1)

        self.update()

    # NOT AUTO : user picks artist and title to make search
    def prep_search_wnd(self, artist, title) :
        self.reset_gui()
        tk.Label(self, text="file : "+self.current_file_name).grid(columnspan=2)

        tk.Label(self, text="title : ").grid(row=1)
        tk.Label(self, text="artist : ").grid(row=2)


        self.title_ent = tk.Entry(self, width = 30)
        self.title_ent.insert(0, title)
        self.title_ent.grid(row=1,column=1)
    
        self.artist_ent = tk.Entry(self, width = 30)
        self.artist_ent.insert(0, artist)
        self.artist_ent.grid(row=2,column=1)

        tk.Button(self, text="Go!",command=lambda: self.make_search())\
            .grid(row=3,columnspan=2)
    
    # NOT AUTO : displays infos for one track
    def dispaly_infos_wnd(self,track) :
        self.reset_gui()
        #Params of the tab:
        lst = [("album",track['album']['name']),
              ("Genre", track['genre']),
              ("release date", track['album']['release_date']),
              ("Track number", str(track['track_number'])+" out of "+str(track['album']['total_tracks'])),
              ("lyrics", track['lyrics']['service'])]

        row_nb = len(lst)
        tab_relief = "solid"
        desc_len = 13
        info_len = 25
        title_len = desc_len + info_len + row_nb*5 - 1

        tk.Label(self, text="file : "+self.current_file_name+"\n").grid(columnspan=3)

        #list to help with the rest
        
        
        
        # Line title
        for i in range(row_nb):
            tk.Label(self, anchor=tk.constants.W, relief=tab_relief, height=2, width=desc_len, text=lst[i][0])\
                .grid(row= i+3,column=0)

        # Line info
        for i in range(row_nb):
            tk.Label(self, anchor=tk.constants.W, relief=tab_relief, height=2, width=info_len, wraplength=250, text=lst[i][1])\
                .grid(row= i+3,column=1)
        
        # Table title
        nb_artist = len(track['artists'])
        if nb_artist == 1:  # no feat
            title = "%s by %s" %(track['name'], track['artists'][0]['name'])
        elif nb_artist == 2:
            title = "%s by %s featuring %s" %(track['name'], track['artists'][0]['name'], track['artists'][1]['name'])
        else:
            title = "%s by %s featuring %s & %s" %(track['name'], track['artists'][0]['name'], track['artists'][1]['name'], track['artists'][2]['name'])
        
        tk.Label(self, relief=tab_relief, width= title_len, wraplength=500, text=title)\
            .grid(row=2,columnspan=3)

        # Album artwork
        imagedata = Image.open(self.current_image_name)
        imagedata = imagedata.resize((row_nb*37+2,row_nb*37+2), Image.ANTIALIAS)
        self.imagedata =  ImageTk.PhotoImage(imagedata)
        tk.Label(self, image=self.imagedata,relief=tab_relief)\
            .grid(row=3,rowspan= row_nb, column=2)

        #different buttons
        tk.Button(self, width=8, text= "skip", command=lambda: self.skip())\
            .grid(row=4+row_nb, column=0, pady=15)
        
        tk.Button(self, width=8, text= "retry", command=lambda: self.retry())\
            .grid(row=4+row_nb, column=1)
        
        tk.Button(self, width=8, text= "ok", command=lambda: self.update_file(track))\
            .grid(row=4+row_nb, column=2)

        
        self.prev_match_button = tk.Button(self, width=15, text="previous match\n(%d left)"%(self.current_info_nb), command=lambda : self.prev_match())
        self.prev_match_button.grid(row = 4, column=4, rowspan=2)
        self.next_match_button = tk.Button(self, width=15, text="next match\n(%d left)"%(self.total_info_nb-self.current_info_nb-1), command=lambda : self.next_match())
        self.next_match_button.grid(row=6, column=4, rowspan=2)

        self.update_buttons()

    def update_buttons(self) :
        if self.current_info_nb == 0 :
            self.prev_match_button['state'] = "disabled"
        if self.current_info_nb+1 == self.total_info_nb :
            self.next_match_button['state'] = "disabled"

    # AUTO : keeps user waiting while searching infos
    def waiting_wnd(self):
        self.reset_gui()
        tk.Label(self, text="Going through your files...").grid(columnspan=2)
        tk.Label(self, text="\nCurrent : \n").grid(row = 1)
        self.tmp_cf = tk.StringVar(value="")
        tk.Label(self, textvariable=self.tmp_cf, width= 40, anchor="nw").grid(row = 1, column=1)
        self.progress_auto = tk.StringVar(value="")
        tk.Label(self, textvariable=self.progress_auto, width=20).grid(row=3,columnspan=2)

    # AUTO : user checks the infos
    def verifications_wnd(self) :
        self.reset_gui()
        self.master.geometry('1000x500')
        # making window scrollable :
        def onFrameConfigure(canvas):
            '''Reset the scroll region to encompass the inner frame'''
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas = tk.Canvas(self, width=950, height=500, borderwidth=0)
        frame = tk.Frame(canvas, width=950, height=500)
        vsb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.grid(row=0, column=1, sticky = "ns")
        canvas.grid(row=0, column=0)
        canvas.create_window((4,4), window=frame, anchor="nw")

        frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

        # preparing disp
        g_nb = len(self.a_good_file)
        m_nb = len(self.a_maybe_file)
        n_nb = len(self.a_nothing_file)
        self.retry_bt = []
        self.tmp_file = []

        for i in range(g_nb):
            self.tmp_file.append(self.a_good_file[i])
            self.retry_bt.append(tk.BooleanVar(value=False))

        for i in range(m_nb) :
            self.tmp_file.append(self.a_maybe_file[i])
            self.retry_bt.append(tk.BooleanVar(value=True))

        for i in range(n_nb) :
            self.tmp_file.append(self.a_nothing_file[i])
            self.retry_bt.append(tk.BooleanVar(value=True)) 

        # Main title 
        tk.Label(frame, text="%s file with certain match\n%s file with a potential match\n%s file with no match\n"%(g_nb,m_nb,n_nb)).grid(columnspan=7)

        #Column titles
        lst = ["retry?", "origin title","origin artist","", "title", "artist", "album" ]
        for j in range(7) :
            if j == 3 :
                tk.Label(frame, text=" ", bg="red").grid(row=2,column=j)
            else :
                tk.Label(frame, text=lst[j]).grid(row=2,column=j)

        # Body
        lst = ["entry_title", "entry_artist", "", "title", "artist", "album"]
        for i in range(self.total_file_nb) :
            tk.Checkbutton(frame, variable=self.retry_bt[i]).grid(row=3+i,column=0)
            for j in range(6):
                if j == 2 : 
                    tk.Label(frame, text=" ", bg="red").grid(row=3+i,column=j+1)
                else :
                    tk.Label(frame, wraplength=150, text= self.tmp_file[i][lst[j]]).grid(row=3+i, column=j+1)

        tk.Button(frame,text="Validate",command=self.prep_reset).grid(row=self.total_file_nb +10, columnspan=7)

    # displays ending stats
    def ending_wnd(self) : 
        self.reset_gui()
        if self.auto and self.treated_file_nb < self.total_file_nb:
            self.reset_all() # if there are still files untreated
        else :
            tk.Label(self, text="All done !").grid(columnspan=2)
            tk.Label(self, text="{} files treated out of {} total".format(self.treated_file_nb, self.total_file_nb))\
                .grid(row=2,columnspan=2)

            tk.Button(self, text= "End", command=lambda: self.end_all()).grid(row=3, column=0, pady=15)
            tk.Button(self, text= "Go again", command=lambda: self.reset_all()).grid(row=3, column=1)
        
    """ -----------------------------------------------
        ------ logger and hook for yt-dl  -------------
        ----------------------------------------------- 
    """    
    class dl_logger(object):
        def __init__(self, app):
            self.app = app
            self.video_nb = ""
            self.playlist_title = ""

        def debug(self,msg):
            logger.debug(msg)
            if "[download] Downloading playlist" in msg:
                self.app.playlist_name.set(msg.replace("[download] Downloading playlist: ","").strip())#"playlist_name"
                self.app.update()
            elif "[download] Downloading" in msg :
                self.video_nb = " " + msg.replace("[download] Downloading ","")+" :" #"video 1 of 12 :""
            elif "[download] Destination:" in msg:
                self.video_title, _ = os.path.splitext(msg.replace("[download] Destination: yt-DL_",""))
                self.app.current_dl_name.set("%s %s"%(self.video_nb, self.video_title))
                self.app.dl_status.set("Downloading : ")
                self.app.update()
            elif "% of " in msg : 
                tmp , _ = msg.replace("[download]", "").split("%") #looks like '\\r\\x1b[K   0.0'
                if "[K" in tmp :
                    _ , tmp = tmp.split("[K")
                self.app.dl_status.set("Downloading : "+ tmp+ "%")
                self.app.update()


        def warning(self,msg):
            pass

        def error(self, msg) :
            logger.error(msg)

    def dl_hook(self, d) : 
        if d['status'] == 'finished':
            self.dl_status.set("Converting")
            self.update()


    """ -----------------------------------------------
        --------------- actual prog  -----------------
        ----------------------------------------------- 
    """    
    def mode_selection(self, mode_nb):
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)

        if mode_nb == 0 :
            self.auto = True
            self.scan_folder()
        elif mode_nb == 1 :
            self.auto = False
            self.scan_folder()
        elif mode_nb == 2 : 
            self.get_URL_wnd()

    def update_config(self):
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        for key in self.params.keys() :
            self.params[key] = self.config[key].get()
                    
        util.update_config(self.params, self)
        self.global_start_wnd()

    def manual_tagging(self):
        self.warn("manual tagging not yet implemented")
        self.skip()

    def retry(self) : 
        util.rm_file(self.current_image_name)
        self.current_image_name = ""
        self.prep_search_wnd(self.a_t[0], self.a_t[1])

    def download(self) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        # getting info
        url=self.input_url.get()
        no_playlist = not self.playlist.get()
        
        self.dl_wnd(no_playlist) # making window
        success = dls.dl_music(url,no_playlist,self.logger,[self.dl_hook])
        if not success : 
            if self.ask("Downloading failed, retry ?") :
                self.get_URL_wnd()
            else : 
                self.ending_wnd()    
        else :
            self.dl_status.set("All done") 
            self.update()
            time.sleep(1)
            
            # If only one file was dl semi-auto process else full auto
            if not no_playlist :
                self.auto = True
            
            self.scan_folder()

    
    def scan_folder(self) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        # scanning folder
        wrong_format = False
        for temp_file_name in os.listdir():
            _ , temp_file_extension = os.path.splitext(temp_file_name)

            if temp_file_extension in self.SUPPORTED_EXTENSIONS and temp_file_name not in self.ignore:
                self.file_name.append(temp_file_name)
                self.file_extension.append(temp_file_extension)
                self.remaining_file_nb += 1

            elif (temp_file_extension in self.NOT_SUPPORTED_EXTENSIONS):
                wrong_format = True
                wrong_file_name = temp_file_name

        # saving total number
        self.total_file_nb = self.remaining_file_nb

        if self.total_file_nb <= 0:  # no music file was found
            self.warn("no music file found")
            self.ending_wnd()

        elif self.auto :
            self.current_file_name = ""
            self.waiting_wnd()
            self.auto_process()

        elif wrong_format:
            self.warn("file " + wrong_file_name +" format unsupported")
            self.scan_data()
            
        else : 
            self.scan_data()

    def auto_process(self) :
        # trying to see if there are correct tags
        self.current_file_name = self.file_name[self.file_nb]
        title, artist, album, encoded_by = self.tagger.read_tags(self.current_file_name)
        
        self.tmp_cf.set(self.current_file_name)
        self.progress_auto.set("file n°"+str(self.file_nb)+" out of "+str(self.total_file_nb))
        self.update()

        if type(title) != type(None):
            title = util.remove_feat(title) 
        else :
            self.skip_auto()
        if type(artist) == type(None) or artist == "None":
            artist = ""      

        # checks wether program already processed file (TODO delete ?)
        if encoded_by == self.SIGN:
            if not self.ask(" file : " + self.current_file_name + " has already been treated. Do you want to change something ?") :
                self.move_file(self.params['folder_name']+os.path.sep+slugify(artist, separator=" ",lowercase=False)+os.path.sep+slugify(album, separator=" ",lowercase=False))  # just moving the file in correct directory

         #Search
        items, certain = self.web.get_basic_info(artist, title)

        if items :         
            track = items[0]
            track = self.web.get_advanced_info(track)
            if certain :
                self.a_good_file.append({"entry_title" : title, "entry_artist": artist, "title" : track['name'], "artist": track['artists'][0]['name'], "album":track['album']['name'],"info" : track, "file_name" : self.current_file_name})
                self.next_auto()
            else :
                self.a_maybe_file.append({"entry_title" : title, "entry_artist": artist, "title" : track['name'], "artist": track['artists'][0]['name'], "album":track['album']['name'],"info" : track, "file_name" : self.current_file_name})
                self.next_auto()
        else :
            self.a_nothing_file.append({"entry_title" : title, "entry_artist": artist, "title" : "", "artist":"","album":""})
            self.next_auto()

        

    def next_auto(self):
        if self.remaining_file_nb > 1:
            self.file_nb += 1  # file being treated = next in the list
            self.remaining_file_nb -= 1  # one file done
            self.auto_process() 
        else:
            self.verifications_wnd() # displaying all files
 
    def prep_reset(self) :
        nb = 0
        for i in range(self.total_file_nb) :
            if self.retry_bt[i].get() :
                self.tmp_file.pop(i-nb)
                nb +=1
                self.finished = False
        self.remaining_file_nb = len(self.tmp_file)
        self.file_nb = 0
        if self.remaining_file_nb == 0 :
            self.reset_all()
        else :
            self.prep_next()

    def prep_next(self) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        self.current_file_name = self.tmp_file[self.file_nb]['file_name']
        track = self.tmp_file[self.file_nb]['info']
        tmp = slugify(track['album']['name']+"_artwork")+".jpg"
        self.current_image_name = dls.dl_image(track['album']['artwork'], tmp, self)
        self.update_file(track)

    def scan_data(self):
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        # trying to see if there are correct tags
        self.current_file_name = self.file_name[self.file_nb]
        title, artist, album, encoded_by = self.tagger.read_tags(self.current_file_name)

        if type(title) != type(None):
            title = util.remove_feat(title) 
        else :
            title = ""
        if type(artist) == type(None) or artist == "None":
            artist = ""            
        
        # checks wether program already processed file (TODO delete ?)
        if encoded_by == self.SIGN:
            if not self.ask(" file : " + self.current_file_name + " has already been treated. Do you want to change something ?") :
                self.move_file(self.params['folder_name']+os.path.sep+slugify(artist, separator=" ",lowercase=False)+os.path.sep+slugify(album, separator=" ",lowercase=False))  # just moving the file in correct directory 
        
        self.prep_search_wnd(artist, title)

    def make_search(self):
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        #read entries
        title = self.title_ent.get()
        artist = self.artist_ent.get()
        self.a_t = (artist, title)

        #Search
        items , certain = self.web.get_basic_info(artist, title)
        
        if items :         
            self.all_infos = items
            self.current_info_nb = 0
            self.total_info_nb = len(items)
            self.prepare_display(items[0])

        else :
            if self.ask("No match found. Retry with different spelling ?"):
                self.prep_search_wnd(artist, title)
            else :
                self.skip()

    def prev_match(self) :
        self.current_info_nb -= 1
        self.prepare_display(self.all_infos[self.current_info_nb])

    def next_match(self) :
        self.current_info_nb += 1
        self.prepare_display(self.all_infos[self.current_info_nb])


    def prepare_display(self, track):
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        
        if not track["info"]["full"] :
            track = self.web.get_advanced_info(track)

        # downloading image 
        tmp = slugify(track['album']['name']+"_artwork")+".jpg"
        if self.current_image_name != tmp :
            util.rm_file(self.current_image_name)
            self.current_image_name = dls.dl_image(track['album']['artwork'], tmp, self)
        
        self.dispaly_infos_wnd(track)


    def update_file(self, track) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
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
                track['name'] = track['name']+" ("+self.params['feat_acronym']+" "+track['artists'][1]['name']+")"  # correct title
            elif nb_artist > 2:
                track['name'] = track['name']+" ("+self.params['feat_acronym']+" "+track['artists'][1]['name']+ \
                                                " & "+track['artists'][2]['name']+")"  # correct title
            
            # modifying the tags
            ret = self.tagger.update_tags(self.current_file_name, self.current_image_name, track)
            
        except FileNotFoundError :
            self.warn("File was moved. Skipping file")            
            self.skip()  # skipping file          
        except Exception as e :
            logger.error(e.args)
            self.warn("File couldn't be edited. Skipping file") 
            self.skip()  # skipping file 
        
        if ret > 0 :
            self.warn("error during tagging. Skipping file")
            self.skip()
        else :
            self.move_file(self.params['folder_name']+os.path.sep+slugify(track['artists'][0]['name'], separator=" ",lowercase=False)+os.path.sep+slugify(track['album']['name'], separator=" ",lowercase=False))
            

    def move_file(self, direction) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
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
                self.current_image_name = ""

        except Exception as e:
            logger.error(e)
            self.warn("Unexpected error:" + e + "\nkeeping this file in main folder")
            
        if self.remaining_file_nb > 1:
            self.file_nb += 1  # file being treated = next in the list
            self.remaining_file_nb -= 1  # one file done
            if not self.auto :
                self.scan_data()
            else :
                self.prep_next() 
        else:
            self.ending_wnd()  # Ending program (or restarting)

    def skip(self) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        util.rm_file(self.current_image_name)
        self.current_image_name = ""
        self.ignore.append(self.current_file_name)
        if self.remaining_file_nb > 1:
            self.file_nb += 1  # file being treated = next in the list
            self.remaining_file_nb -= 1  # one file done
            if not self.auto :
                self.scan_data() 
            else :
                self.prep_next()
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
            self.ignore = [""]
            if self.auto and not self.finished : 
                self.finished = True 
                self.auto = False
                self.scan_folder()
            else :
                self.global_start_wnd()
            
    def end_all(self) :
        sys.exit("")


def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


if __name__ == '__main__':
    #Logger 
    log_lvl = logging.INFO
    logger = logging.getLogger("MEP")
    logger.setLevel(log_lvl)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(log_lvl)
    ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(ch)
    main()

    


