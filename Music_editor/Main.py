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
        logging.debug("in func : " + inspect.currentframe().f_code.co_name)

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

        self.AUTO = False # unused for now 
        self.logger = self.dl_logger(self)        
        
        # getting info from config file :
        self.params = util.read_config(self)

        self.ADD_SIGN = False # param (maybe changed in config... not sure yet)

        if self.ADD_SIGN :
            self.SIGN = "MEP by GM"
        else :
            self.SIGN = "---"

        #temp : 
        #self.dispaly_infos_wnd({'album':{"name":"album name", "release_date": "01-32-50", "total_tracks":"12"}, 'artists':[{"name":"artist name"}], "track_number":"10","name":" track name", "genre":"pop", "lyrics":{"service":"musixmatch"}})
        #self.return_url()
        
        self.web = Info_search(self.params) 
        self.tagger = Tagger(self.params, self.ADD_SIGN, self.SIGN) 

        self.global_start_wnd()
        


    """ Start of GUI """
    def reset_gui(self):
        '''Reset the list of participants'''
        for child in self.winfo_children():
            child.destroy()

    def warn(self, message) :
        if not self.AUTO :
            messagebox.showwarning('Warning', message)
            
    def ask(self,message) :
        if self.AUTO :
            return False 
        else :
            return messagebox.askyesno('Verification',message)

    def global_start_wnd(self):
        self.reset_gui()
        #TODO Re do 
        tk.Label(self, text="Select a mode\n").grid(row=0,columnspan=4)

        mode_names = ['Automatically go through a\nlarge music library', 'fill music tags for a few\nfiles','download music\nfrom youtube URL']
        for i in range(0,len(mode_names)):
            tk.Button(self, text= mode_names[i], command= lambda x=i: self.mode_selection(x)).grid(row=1, column=i)
        
        tk.Label(self).grid(row=2)
        tk.Button(self, text= "settings", command= self.settings_wnd).grid(row=3, column=1)    

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
    
    #window before download
    def get_URL_wnd(self):
        self.reset_gui()

        self.playlist = tk.BooleanVar()
        tk.Checkbutton(self, text='Whole playlist ?',var= self.playlist).grid(row = 0)
        
        self.input_url = tk.Entry(self,width=60)
        self.input_url.grid(row = 1)
        self.input_url.focus()
        
        tk.Button(self, text= "Download", command= self.download).grid(row = 2)

    # window during download
    def dl_wnd(self, no_playlist) :
        logging.debug("starting window")
        self.reset_gui()

        # create variables that will change during download
        self.dl_status = tk.StringVar(value="State : Starting process")  
        self.current_dl_name = tk.StringVar(value="Current file : TBD")
        self.playlist_name = tk.StringVar(value="Playlist : TBD")

        # Common to both 
        tk.Label(self,text=" Downloading screen").grid(row=1)
        tk.Label(self, textvariable=self.dl_status).grid(row=5)

        #specific
        if no_playlist :
            tk.Label(self, textvariable=self.current_dl_name).grid(row= 3)

        else :
            tk.Label(self, textvariable=self.playlist_name).grid(row=3)
            tk.Label(self, textvariable=self.current_dl_name).grid(row= 4)

        self.update()

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
    
    def dispaly_infos_wnd(self,track) :
        self.reset_gui()
        tab_relief = "solid"

        tk.Label(self, text="file : "+self.current_file_name+"\n").grid(columnspan=3)

        #list to help with the rest
        lst = [("album",track['album']['name']),
              ("Genre", track['genre']),
              ("release date", track['album']['release_date']),
              ("Track number", str(track['track_number'])+" out of "+str(track['album']['total_tracks'])),
              ("lyrics", track['lyrics']['service'])]

        row_nb = len(lst)
        max_len = 0
        
        # Line title
        for i in range(row_nb):
            tk.Label(self, text=lst[i][0],anchor=tk.constants.W, relief=tab_relief, height=2, width=13).grid(row= i+3,column=0)
            #calculating max length 
            temp_len = len(lst[i][1])
            if temp_len > max_len :
                max_len = temp_len

        # Line info
        for i in range(row_nb):
            self.track_infos = tk.Label(self, text=lst[i][1],anchor=tk.constants.W, relief=tab_relief, height=2, width=max_len)
            self.track_infos.grid(row= i+3,column=1)
        
        # Table title
        nb_artist = len(track['artists'])
        if nb_artist == 1:  # no feat
            title = "%s by %s" %(track['name'], track['artists'][0]['name'])
        elif nb_artist == 2:
            title = "%s by %s featuring %s" %(track['name'], track['artists'][0]['name'], track['artists'][1]['name'])
        else:
            title = "%s by %s featuring %s & %s" %(track['name'], track['artists'][0]['name'], track['artists'][1]['name'], track['artists'][2]['name'])
        tk.Label(self, text=title, relief=tab_relief, width= 14+max_len+row_nb*5).grid(row=2,columnspan=3)

        # Album artwork
        imagedata = Image.open(self.current_image_name)
        imagedata = imagedata.resize((row_nb*39,row_nb*39), Image.ANTIALIAS)
        self.imagedata =  ImageTk.PhotoImage(imagedata)
        tk.Label(self, image=self.imagedata,relief=tab_relief)\
            .grid(row=3,rowspan= row_nb, column=2)

        #different buttons
        tk.Button(self, text= "skip", command=lambda: self.skip())\
            .grid(row=4+row_nb, column=0, pady=15)
        
        tk.Button(self, text= "retry", command=lambda: self.retry())\
            .grid(row=4+row_nb, column=1)
        
        tk.Button(self, text= "ok", command=lambda: self.update_file(track))\
            .grid(row=4+row_nb, column=2)

        button = tk.Button(self, text="next match\n(%d left)"%(self.total_info_nb-self.current_info_nb-1), command=lambda : self.next_match())
        button.grid(row=5, column=4)

        if self.total_info_nb == 1:
            button['state'] = "disabled"

    def ending_wnd(self) : 
        self.reset_gui()

        tk.Label(self, text="All done !").grid(columnspan=2)
        tk.Label(self, text="{} files treated out of {} total".format(self.total_file_nb, self.treated_file_nb))\
            .grid(row=2,columnspan=2)

        tk.Button(self, text= "End", command=lambda: self.end_all()).grid(row=3, column=0, pady=15)
        tk.Button(self, text= "Go again", command=lambda: self.reset_all()).grid(row=3, column=1)

    
    """ For youtube-dl infos """
    class dl_logger(object):
        def __init__(self, app):
            self.app = app
            self.video_nb = "video:"
            self.playlist_title = ""

        def debug(self,msg):
            logging.debug(msg)
            if "[download] Downloading playlist" in msg:
                self.app.playlist_name.set("playlist : " + msg.replace("[download] Downloading playlist: ","").strip())#"playlist: playlist_name"
                self.app.update()
            elif "[download] Downloading" in msg :
                self.video_nb = msg.replace("[download] Downloading ","")+" :" #"video 1 of 12 :""
            elif "[download] Destination:" in msg:
                self.video_title, _ = os.path.splitext(msg.replace("[download] Destination: yt-DL_",""))
                self.app.current_dl_name.set("Current file : %s %s"%(self.video_nb, self.video_title))
                self.app.update()

        def warning(self,msg):
            pass

        def error(self, msg) :
            logging.error(msg)

    def dl_hook(self, d) : 
        if d['status'] == 'finished':
            self.dl_status.set("Status : Done downloading, now converting")
            self.update()


    """ Actual prog """ 
    def mode_selection(self, mode_nb):
        logging.debug("in func : " + inspect.currentframe().f_code.co_name)

        if mode_nb == 0 :
            self.warn("This mode is still a work in progress\nBugs are to be expected")
            self.ending_wnd()
        elif mode_nb == 1 :
            self.AUTO = False
            self.scan_folder()
        elif mode_nb == 2 : 
            self.get_URL_wnd()
        else :
            self.deprecated()

    def update_config(self):
        logging.debug("in func : " + inspect.currentframe().f_code.co_name)
        for key in self.params.keys() :
            self.params[key] = self.config[key].get()
                    
        util.update_config(self.params, self)
        self.global_start_wnd()

    def manual_tagging(self):
        self.warn("manual tagging not yet implemented")
        self.skip()

    def retry(self) : 
        util.rm_file(self.current_image_name)
        self.prep_search_wnd(self.a_t[0], self.a_t[1])

    def download(self) :
        logging.debug("in func : " + inspect.currentframe().f_code.co_name)
        # getting info
        url=self.input_url.get()
        no_playlist = not self.playlist.get()
        
        self.dl_wnd(no_playlist) # making window

        dls.dl_music(url,no_playlist,self.logger,[self.dl_hook])# launching download
        self.dl_status.set("Status : All done") 
        self.update()
        time.sleep(1)
        
        # Resuming normal process
        self.scan_folder()

    
    def scan_folder(self) :
        logging.debug("in func : " + inspect.currentframe().f_code.co_name)
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
        logging.debug("in func : " + inspect.currentframe().f_code.co_name)
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
        if encoded_by == self.SIGN:
            if not self.ask(" file : " + self.current_file_name + " has already been treated. Do you want to change something ?") :
                self.move_file()  # just moving the file in correct directory 
        
        self.prep_search_wnd(artist, title)

    def make_search(self):
        logging.debug("in func : " + inspect.currentframe().f_code.co_name)
        #read entries
        title = self.title_ent.get()
        artist = self.artist_ent.get()
        self.a_t = (artist, title)

        #Search
        items = self.web.get_basic_info(artist, title)
        
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
        
    def next_match(self) :
        util.rm_file(self.current_image_name)
        self.current_info_nb += 1
        if self.current_info_nb < self.total_info_nb:
            self.prepare_display(self.all_infos[self.current_info_nb])
        else :
            self.warn("no more results")
            self.current_info_nb = 0
            self.prepare_display(self.all_infos[0])

    #track = {'album':{"name":"OK Computer", "release_date": "1997-05-28", "total_tracks":"12"}, 'artists':[{"name":artist}], "track_number":"4","name":title, "genre":"alternative rock", "lyrics":{"service":"musixmatch"}}
    def prepare_display(self, track):
        logging.debug("in func : " + inspect.currentframe().f_code.co_name)
        track = self.web.get_advanced_info(track)

        # downloading image 
        tmp = slugify(track['album']['name']+"_artwork")+".jpg"
        self.current_image_name = dls.dl_image(track['album']['artwork'], tmp, self)
        
        self.dispaly_infos_wnd(track)

    def update_file(self, track) :
        logging.debug("in func : " + inspect.currentframe().f_code.co_name)
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
            logging.error(e.args)
            self.warn("File couldn't be edited. Skipping file") 
            self.skip()  # skipping file 
        
        if ret > 0 :
            self.warn("error during tagging. Skipping file")
            self.skip()
        else :
            self.move_file(self.params['folder_name']+os.path.sep+slugify(track['artists'][0]['name'], separator=" ",lowercase=False)+os.path.sep+slugify(track['album']['name'], separator=" ",lowercase=False))
            

    def move_file(self, direction) :
        logging.debug("in func : " + inspect.currentframe().f_code.co_name)
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
            logging.error("Unexpected error:" + sys.exc_info()[0])
            self.warn("Unexpected error:" + sys.exc_info()[0] + "\nkeeping this file in main folder")
            
        if self.remaining_file_nb > 1:
            self.file_nb += 1  # file being treated = next in the list
            self.remaining_file_nb -= 1  # one file done
            self.scan_data() 
        else:
            self.ending_wnd()  # Ending program (or restarting)

    def skip(self) :
        util.rm_file(self.current_image_name)

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
        self.warn("This functionality is not supported anymore")
        self.end_all
        pass

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


