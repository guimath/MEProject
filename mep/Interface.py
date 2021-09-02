import os 

# GUI
import tkinter as tk
from tkinter import messagebox
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

        text = ['Welcome to MEP','Select a mode']
        button_names = ['Automatically go through a large music library', 'Fill music tags for a few files','Download music from youtube URL', 'Settings']

        tk.Label(self, text=text[0],font=self.TITLE_FONT).grid(row=0,column=3)

        tk.Label(self, text=text[1],pady=10,font=self.BASIC_FONT).grid(row=1,column=3)
        
        for i in range(0,len(button_names)-1):
            tk.Label(self, padx=5).grid(row=2,column=2*i)

            #button
            tk.Button(self, width= 20, wraplength=180, text= button_names[i], command= lambda x=i: self.mep.mode_selection(x),font=self.BASIC_FONT)\
                .grid(row=2, column=2*i+1)
        
        tk.Label(self,pady=30).grid(row=3)
        tk.Button(self, text= button_names[i+1], command= self.settings_wnd,font=self.BASIC_FONT).grid(row=4, column=3)    

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
        
        tk.Label(self, text= text[0],font=self.TITLE_FONT).grid(row=0,columnspan=2)
        
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
        tk.Button(self, padx=20, text = text[8], command= self.mep.update_config, font=self.BASIC_FONT)\
            .grid(row=row_nb+i+1, columnspan=2)
    
    # DL : user picks URL
    def get_URL_wnd(self):
        self.reset_gui()

        self.playlist = tk.BooleanVar()
        tk.Checkbutton(self, text='Whole playlist ?',var= self.playlist).grid(row = 0)
        
        self.input_url = tk.Entry(self,width=60)
        self.input_url.grid(row = 1)
        self.input_url.focus()
        tk.Button(self, text= "Download", command= self.mep.download).grid(row = 2)

    # DL : keeps user informed about the download process
    def dl_wnd(self, no_playlist) :
        self.reset_gui()

        # create variables that will change during download
        self.dl_status = tk.StringVar(value="Starting process")  
        self.current_dl_name = tk.StringVar(value="TBD")
        self.playlist_name = tk.StringVar(value="TBD")

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
        tk.Label(self, text="file : "+self.mep.current_file_name).grid(columnspan=2)

        tk.Label(self, text="title : ").grid(row=1)
        tk.Label(self, text="artist : ").grid(row=2)

        self.title_ent = tk.Entry(self, width = 30)
        self.title_ent.insert(0, title)
        self.title_ent.grid(row=1,column=1)
    
        self.artist_ent = tk.Entry(self, width = 30)
        self.artist_ent.insert(0, artist)
        self.artist_ent.grid(row=2,column=1)

        tk.Button(self, text="Go!",command=lambda: self.mep.make_search())\
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
        # TODO REMOVE title_len = desc_len + info_len + row_nb*5 - 1

        tk.Label(self, text="file : "+self.mep.current_file_name+"\n").grid(columnspan=3)        
        
        
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
        
        tk.Label(self, relief=tab_relief, wraplength=450, text=title)\
            .grid(row=2,columnspan=3,sticky='nesw')

        # Album artwork
        imagedata = Image.open(self.mep.current_image_name)
        imagedata = imagedata.resize((row_nb*37+2,row_nb*37+2), Image.ANTIALIAS)
        self.imagedata =  ImageTk.PhotoImage(imagedata)
        tk.Label(self, image=self.imagedata,relief=tab_relief)\
            .grid(row=3,rowspan= row_nb, column=2)

        #different buttons
        tk.Button(self, width=8, text= "skip", command=lambda: self.mep.skip())\
            .grid(row=4+row_nb, column=0, pady=15)
        
        tk.Button(self, width=8, text= "retry", command=lambda: self.mep.retry())\
            .grid(row=4+row_nb, column=1)
        
        tk.Button(self, width=8, text= "ok", command=lambda: self.mep.update_file(track))\
            .grid(row=4+row_nb, column=2)

        
        self.prev_match_button = tk.Button(self, width=15, text="previous match\n(%d left)"%(self.mep.current_info_nb), command=lambda : self.mep.prev_match())
        self.prev_match_button.grid(row = 4, column=4, rowspan=2)
        self.next_match_button = tk.Button(self, width=15, text="next match\n(%d left)"%(self.mep.total_info_nb-self.mep.current_info_nb-1), command=lambda : self.mep.next_match())
        self.next_match_button.grid(row=6, column=4, rowspan=2)

        self.update_buttons()

    def update_buttons(self) :
        if self.mep.current_info_nb == 0 :
            self.prev_match_button['state'] = "disabled"
        if self.mep.current_info_nb+1 == self.mep.total_info_nb :
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
        g_nb = len(self.mep.a_good_file)
        m_nb = len(self.mep.a_maybe_file)
        n_nb = len(self.mep.a_nothing_file)
        self.retry_bt = []
        self.tmp_file = []

        for i in range(g_nb):
            self.tmp_file.append(self.mep.a_good_file[i])
            self.retry_bt.append(tk.BooleanVar(value=False))

        for i in range(m_nb) :
            self.tmp_file.append(self.mep.a_maybe_file[i])
            self.retry_bt.append(tk.BooleanVar(value=True))

        for i in range(n_nb) :
            self.tmp_file.append(self.mep.a_nothing_file[i])
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
        for i in range(self.mep.total_file_nb) :
            tk.Checkbutton(frame, variable=self.retry_bt[i]).grid(row=3+i,column=0)
            for j in range(6):
                if j == 2 : 
                    tk.Label(frame, text=" ", bg="red").grid(row=3+i,column=j+1)
                else :
                    tk.Label(frame, wraplength=150, text= self.tmp_file[i][lst[j]]).grid(row=3+i, column=j+1)

        tk.Button(frame,text="Validate",command=self.mep.prep_reset).grid(row=self.mep.total_file_nb +10, columnspan=7)

    # displays ending stats
    def ending_wnd(self) : 
        self.reset_gui()
        if self.mep.auto and self.mep.treated_file_nb < self.mep.total_file_nb:
            self.reset_all() # if there are still files untreated
        else :
            tk.Label(self, text="All done !").grid(columnspan=2)
            tk.Label(self, text="{} files treated out of {} total".format(self.mep.treated_file_nb, self.mep.total_file_nb))\
                .grid(row=2,columnspan=2)

            tk.Button(self, text= "End", command=lambda: self.mep.end_all()).grid(row=3, column=0, pady=15)
            tk.Button(self, text= "Go again", command=lambda: self.mep.reset_all()).grid(row=3, column=1)
        

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


    


