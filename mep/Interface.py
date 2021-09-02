import os 

# GUI
import tkinter as tk
from tkinter import messagebox
from tkinter import font
from PIL import Image, ImageTk

class Application(tk.Frame):
    def __init__(self, logger, mep, master=None):
        self.logger = logger
        self.mep = mep

        # Window init
        super().__init__(master) 
        self.master = master
        self.master.geometry('800x500')
        self.master.title("MEProject")
        self.grid()

        self.FONT_NAME = "helvetica"
        self.TITLE_FONT = self.FONT_NAME + " 14" 
        self.BASIC_FONT = self.FONT_NAME + " 12"
        self.BOLD_FONT = self.BASIC_FONT + " bold"

    def reset_gui(self):
        for child in self.winfo_children():
            child.destroy()

    def warn(self, message) :
        if not self.mep.auto :
            messagebox.showwarning('Warning', message)
            
    def ask(self,message) :
        if self.mep.auto :
            return False 
        else :
            return messagebox.askyesno('Verification',message)

    # Start screen (User picks a mode)
    def global_start_wnd(self):
        self.reset_gui()

        text = [
            # Title 
            'Welcome to MEP',
            # Sub title
            'Select a mode',
            # Buttons / modes 
            'Automatically go through a large music library',
            'Fill music tags for a few files',
            'Download music from youtube URL',
            'Settings',]

        # Title 
        tk.Label(self, text=text[0], pady=10, font=self.TITLE_FONT).grid(row=0,column=3)
        # Sub title
        tk.Label(self, text=text[1],pady=10,font=self.BASIC_FONT).grid(row=1,column=3)
        
        for i in range(0,3):
            tk.Label(self, padx=5).grid(row=2,column=2*i)

            # Modes
            tk.Button(self, width= 20, wraplength=180, text= text[i+2], command= lambda x=i: self.mep.mode_selection(x),font=self.BASIC_FONT)\
                .grid(row=2, column=2*i+1)
        
        # Settings button
        tk.Label(self,pady=30).grid(row=3)
        tk.Button(self, text= text[i+3], command= self.settings_wnd,font=self.BASIC_FONT).grid(row=4, column=3)    


    # User can see/modify settings
    def settings_wnd(self) :
        self.reset_gui()

        text = [
            # Title
            'Settings', 
            # Checkboxes desc
            'search for the artist label', # 
            'search for the bpm',
            'search for the lyrics (can slow the program slightly)',
            'include image in file (if unchecked image will just be placed within the album folder)',
            # Entries desc
            'folder name (can be a simple name or a path)',
            'featuring acronym',
            'default genre',
            # Button
            'Save']
        
        # Title
        tk.Label(self, text= text[0],pady=10,font=self.TITLE_FONT).grid(row=0,columnspan=2)
        
        row_nb = 2

        # Checkbox
        var_name = ["get_label", "get_bpm","get_lyrics", "store_image_in_file"]
        self.config = {}
        for key in var_name :
            self.config[key] = tk.BooleanVar(value=self.mep.params[key])

        for i in range(len(var_name)) :
            tk.Checkbutton(self, anchor="nw", width=70, text=text[i+1],var= self.config[var_name[i]],font=self.BASIC_FONT)\
                .grid(row = row_nb,columnspan=2)
            row_nb +=1
        
        # Spacing
        row_nb += 2
        tk.Label(self, text="").grid(row=row_nb-1)
        
        # Entries
        var_name = ["folder_name", "feat_acronym", "default_genre"]
        for i in range(len(var_name)) :
            tk.Label(self, width= 40, anchor="nw", text= text[i+3], pady=2,font=self.BASIC_FONT).grid(row=row_nb+i)
            self.config[var_name[i]] = tk.Entry(self, width = 30, relief='flat', font=self.BASIC_FONT)
            self.config[var_name[i]].insert(0, self.mep.params[var_name[i]])
            self.config[var_name[i]].grid(row=row_nb+i,column=1)

        # Button
        tk.Label(self).grid(row=row_nb+i+1)
        tk.Button(self, padx=20, text = text[8], command= self.mep.update_config, font=self.BASIC_FONT)\
            .grid(row=row_nb+i+2, columnspan=2)
    
    # DL : user picks URL
    def get_URL_wnd(self):
        self.reset_gui()

        text = [
            # Title 
            'Enter URL',
            # Checkbox desc
            'Whole playlist ?',
            # Button
            'Download']

        # Title 
        tk.Label(self, text= text[0], pady= 10,font=self.TITLE_FONT).grid()

        # Checkbox
        self.playlist = tk.BooleanVar()
        tk.Checkbutton(self, text=text[1],var= self.playlist, font=self.BASIC_FONT).grid(row = 1)
        
        # Entry
        self.input_url = tk.Entry(self,width=60, font=self.BASIC_FONT)
        self.input_url.grid(row = 2)
        self.input_url.focus()
        
        # Button
        tk.Button(self, text= text[2], command= self.mep.download, font=self.BASIC_FONT).grid(row = 3)

    # DL : keeps user informed about the download process
    def dl_wnd(self, no_playlist) :
        self.reset_gui()

        text = [
            # Title
            'Downloading screen',
            # Label desc
            'Playlist :',
            'Current file :',
            'State :']
        
        place_holders = ['TBD', 'TBD','Starting Process']

        # Title 
        tk.Label(self,text=text[0],pady = 10,font=self.TITLE_FONT).grid(row=1, columnspan=2)

        # create variables that will change during download
        self.playlist_name = tk.StringVar(value=place_holders[0])
        self.current_dl_name = tk.StringVar(value=place_holders[1])
        self.dl_status = tk.StringVar(value=place_holders[2])  

        
        if no_playlist :
            # current file
            tk.Label(self, text=text[2], width=10, height=2, padx=3, anchor='e', font=self.BOLD_FONT).grid(row=3)
            tk.Label(self, width=30, anchor="w", textvariable=self.current_dl_name, font=self.BASIC_FONT).grid(row= 3, column=1)

        else :
            # playlist
            tk.Label(self, text=text[1], width=10, height=2, padx=3, anchor='e', font=self.BOLD_FONT).grid(row=3)
            tk.Label(self, width=30, wraplength= 200, anchor="w", textvariable=self.playlist_name, padx = 3, font=self.BASIC_FONT).grid(row=3, column=1)
            # current file
            tk.Label(self, text=text[2], width=10, height=2, padx=3, anchor='e', font=self.BOLD_FONT).grid(row=4)
            tk.Label(self, width=30, anchor="w", textvariable=self.current_dl_name, padx = 3, font=self.BASIC_FONT).grid(row= 4, column=1)
        
        # state
        tk.Label(self, text=text[3], width=10, height=2, padx=3, anchor='e', font=self.BOLD_FONT).grid(row=5)
        tk.Label(self, textvariable=self.dl_status, width=30,anchor="w", padx = 3, font = self.BASIC_FONT).grid(row=5, column=1)
        
        self.update()

    # NOT AUTO : user picks artist and title to make search
    def prep_search_wnd(self, artist, title) :
        self.reset_gui()

        text = [
            # Title
            'File : ' + self.mep.current_file_name,
            # Entries desc
            'title :',
            'artist :',
            #Button
            'Go !']       

        # Title 
        tk.Label(self, text=text[0], pady=10, wraplength=400, font=self.BASIC_FONT).grid(columnspan=3)

        # entry title
        tk.Label(self, text=text[1],width= 6, font=self.BOLD_FONT).grid(row=1)
        self.title_ent = tk.Entry(self, width = 50, relief='flat', font=self.BASIC_FONT)
        self.title_ent.insert(0, title)
        self.title_ent.grid(row=1,column=1)

        # entry artist
        tk.Label(self, text=text[2],width= 6, pady = 5, font=self.BOLD_FONT).grid(row=2)
        self.artist_ent = tk.Entry(self, width = 50, relief='flat', font=self.BASIC_FONT)
        self.artist_ent.insert(0, artist)
        self.artist_ent.grid(row=2,column=1)

        # Go button
        tk.Button(self, text=text[3],command=lambda: self.mep.make_search(), font=self.BASIC_FONT)\
            .grid(row=3,columnspan=2)
    
    # NOT AUTO : displays infos for one track
    def dispaly_infos_wnd(self,track) :
        self.reset_gui()

        text = [
            # Title
            'File : ' + self.mep.current_file_name,
            # table title
            '',
            # desc
            'Album',
            'Genre',
            'Release date',
            'Track number',
            'Lyrics',
            # Buttons
            'Skip',
            'Retry',
            'ok',
            f'previous match\n({self.mep.current_info_nb} left)',
            f'next match\n({self.mep.total_info_nb-self.mep.current_info_nb-1} left)',
            ]       

        # formating table title
        nb_artist = len(track["artists"])
        if nb_artist == 1:  # no feat
            text[1] = f'{track["name"]} by {track["artists"][0]["name"]}'
        elif nb_artist == 2:
            text[1] = f'{track["name"]} by {track["artists"][0]["name"]} featuring {track["artists"][1]["name"]}'
        else:
            text[1] = f'{track["name"]} by {track["artists"][0]["name"]} featuring {track["artists"][1]["name"]} & {track["artists"][2]["name"]}'
        
        row_nb = 5
        tab_relief = "solid"
        desc_len = 13
        info_len = 30

        # Title
        tk.Label(self, text=text[0], pady=10, wraplength=400, font=self.BASIC_FONT).grid(columnspan=3)

        # Table title 
        tk.Label(self, relief=tab_relief, wraplength=450, text=text[1], height=2, font=self.BOLD_FONT)\
            .grid(row=2,columnspan=3,sticky='nesw')
        
        # infos
        var = [track['album']['name'], track['genre'], track['album']['release_date'], str(track['track_number'])+" out of "+str(track['album']['total_tracks']), track['lyrics']['service']]

        for i in range(row_nb):
            # Line title
            tk.Label(self, anchor="w", relief=tab_relief, height=2, width=desc_len, padx=4, text=text[i+2], font=self.BOLD_FONT)\
                .grid(row= i+3,column=0)

            # Line info
            tk.Label(self, anchor="w", relief=tab_relief, width=info_len, padx=4, wraplength=275, text=var[i], font= self.BASIC_FONT)\
                .grid(row= i+3,column=1, sticky='ns')

        # Album artwork
        imagedata = Image.open(self.mep.current_image_name)
        imagedata = imagedata.resize((row_nb*37+2,row_nb*37+2), Image.ANTIALIAS)
        self.imagedata =  ImageTk.PhotoImage(imagedata)
        tk.Label(self, image=self.imagedata,relief=tab_relief)\
            .grid(row=3,rowspan= row_nb, column=2)

        # Different buttons
        tk.Button(self, width=8, text= text[7], command=lambda: self.mep.skip(), font=self.BASIC_FONT)\
            .grid(row=4+row_nb, column=0, pady=15)
        
        tk.Button(self, width=8, text= text[8], command=lambda: self.mep.retry(), font=self.BASIC_FONT)\
            .grid(row=4+row_nb, column=1)
        
        tk.Button(self, width=8, text= text[9], command=lambda: self.mep.update_file(track), font=self.BASIC_FONT)\
            .grid(row=4+row_nb, column=2)

        # Prev and next match
        self.prev_match_button = tk.Button(self, width=15, text=text[10], command=lambda : self.mep.prev_match(), font=self.BASIC_FONT)
        self.prev_match_button.grid(row = 4, column=4, rowspan=2)
        self.next_match_button = tk.Button(self, width=15, text=text[11], command=lambda : self.mep.next_match(), font=self.BASIC_FONT)
        self.next_match_button.grid(row=6, column=4, rowspan=2)

        self._update_buttons()

    # De activates buttons if no more matches available
    def _update_buttons(self) :
        if self.mep.current_info_nb == 0 :
            self.prev_match_button['state'] = "disabled"
        if self.mep.current_info_nb+1 == self.mep.total_info_nb :
            self.next_match_button['state'] = "disabled"

    # AUTO : keeps user waiting while searching infos
    def waiting_wnd(self):
        self.reset_gui()

        text = [
            # Title
            'Going through your files...',
            # Label
            'Progress :',
            'File name :',
            ]       

        # Title 
        tk.Label(self, text=text[0], pady=10, font=self.TITLE_FONT).grid(columnspan=2)

        self.current_file = tk.StringVar(value="")
        self.progress = tk.StringVar(value="")

        # Progress
        tk.Label(self, text=text[1], width=10,wraplength=100, anchor='e',font=self.BOLD_FONT).grid(row = 1)
        tk.Label(self, textvariable=self.progress, width=40,anchor="w", font=self.BASIC_FONT).grid(row=1,column=1)

        # File name
        tk.Label(self, text=text[2], width=10,height=2, anchor='e',font=self.BOLD_FONT).grid(row = 2)
        tk.Label(self, textvariable=self.current_file, width= 40, anchor="w", font=self.BASIC_FONT).grid(row = 2, column=1) #

    # AUTO : user checks the infos
    def verifications_wnd(self) :
        self.reset_gui()
        self.master.geometry('1000x500')

        # making window scrollable :
        def onFrameConfigure(canvas):
            #Reset the scroll region to encompass the inner frame
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas = tk.Canvas(self, width=950, height=500, borderwidth=0)
        frame = tk.Frame(canvas, width=950, height=500)
        vsb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.grid(row=0, column=1, sticky = "ns")
        canvas.grid(row=0, column=0)
        canvas.create_window((4,4), window=frame, anchor="nw")

        frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))


        g_nb = len(self.mep.a_good_file)
        m_nb = len(self.mep.a_maybe_file)
        n_nb = len(self.mep.a_nothing_file)
        self.retry_bt = []
        self.tmp_file = []

        # getting all files in one lst
        for i in range(g_nb):
            self.tmp_file.append(self.mep.a_good_file[i])
            self.retry_bt.append(tk.BooleanVar(value=False))

        for i in range(m_nb) :
            self.tmp_file.append(self.mep.a_maybe_file[i])
            self.retry_bt.append(tk.BooleanVar(value=True))

        for i in range(n_nb) :
            self.tmp_file.append(self.mep.a_nothing_file[i])
            self.retry_bt.append(tk.BooleanVar(value=True)) 

        text = [
            # Title
            f'{g_nb} file with certain match\n{m_nb} file with a potential match\n{n_nb} file with no match\n',
            # column titles    
            'Retry?',
            'Origin title',
            'Origin artist',
            '',
            'Title',
            'Artist',
            'Album',
            #Button
            'Validate'] 

        # Title 
        tk.Label(frame, text=text[0], pady=10, font=self.TITLE_FONT).grid(columnspan=7)

        # Column Titles
        for j in range(7) :
            if j == 3 :
                tk.Label(frame, text='',bg='red').grid(row=2,column=j,sticky='ns') 
            else :
                tk.Label(frame, text=text[j+1], height=2, padx=5, font=self.BOLD_FONT).grid(row=2,column=j, sticky='ew')

        # Body
        var_name = ['entry_title', 'entry_artist', '', 'title', 'artist', 'album']
        for i in range(self.mep.total_file_nb) :
            tk.Checkbutton(frame, variable=self.retry_bt[i]).grid(row=3+i,column=0)
            for j in range(6):
                if j == 2 : 
                    tk.Label(frame, text='', bg='red').grid(row=3+i,column=j+1,sticky='ns')
                else :
                    tk.Label(frame, wraplength=150, padx=5, text= self.tmp_file[i][var_name[j]], font=self.BASIC_FONT).grid(row=3+i, column=j+1)
        
        tk.Label(frame).grid(row=self.mep.total_file_nb +9)
        tk.Button(frame,text=text[8],command=self.mep.prep_reset, font=self.BASIC_FONT).grid(row=self.mep.total_file_nb +10, columnspan=7)

    # displays ending stats
    def ending_wnd(self) : 
        self.reset_gui()

        text = [
            # Title
            'All done !',
            # Overview
            f'{self.mep.treated_file_nb} files treated out of {self.mep.total_file_nb} total',
            # Buttons    
            'End',
            'Go again']       

        # Title 
        tk.Label(self, text=text[0], width= 75, pady=75, font=self.TITLE_FONT).grid(columnspan=4)
        tk.Label(self, text="",width= 25).grid(row=2,column=0)
        tk.Label(self, text="",width= 25).grid(row=2,column=3)

        # Overview
        tk.Label(self, text=text[1],width= 25, pady=25, font=self.BASIC_FONT)\
            .grid(row=2,column=1,columnspan=2)

        # Buttons
        tk.Button(self, text= text[2], width= 8, command=lambda: self.mep.end_all(), font=self.BASIC_FONT).grid(row=3, column=1)
        tk.Button(self, text= text[3], width= 8,  command=lambda: self.mep.reset_all(), font=self.BASIC_FONT).grid(row=3, column=2)
        

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
            self.app.logger.debug(msg)
            if "[download] Downloading playlist" in msg:
                self.app.playlist_name.set(msg.replace("[download] Downloading playlist: ","").strip())#"playlist_name"
                self.app.update()
            elif "[download] Downloading" in msg :
                # [download] Downloading video 1 of 1 :
                self.video_nb = " " + msg.replace("[download] Downloading ","")+" :" #"video 1 of 12 :""
                if self.video_nb == " video 1 of 1 :" :
                    self.video_nb = ""
            elif "[download] Destination:" in msg:
                #[download] Destination: yt-DL_The Beatles - Hey Jude.m4a                
                self.video_title, _ = os.path.splitext(msg.replace("[download] Destination: yt-DL_",""))#video title
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
            self.app.logger.error(msg)

    def dl_hook(self, d) : 
        if d['status'] == 'finished':
            self.dl_status.set("Converting")
            self.update()


    


