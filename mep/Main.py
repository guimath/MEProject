# -*-coding:utf-8 -*
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports

# gui
import tkinter as tk

#logging
import logging, inspect

# formating strings
from slugify import slugify

# moving files 
import shutil #only uses shutil.move 

# local
import Interface
import Downloads as dls
import Utilitaries as util
from Tagger import Tagger
from Info_search import Info_search

class Mep :
    def __init__(self) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)

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
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)

        self.app.global_start_wnd()

        # getting info from config file :
        self.params = util.read_config(self.app)
        self.web = Info_search(self.params) 
        self.tagger = Tagger(self.params, self.ADD_SIGN, self.SIGN) 
        self.app.mainloop()

    def mode_selection(self, mode_nb):
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)

        if mode_nb == 0 :
            self.auto = True
            self.scan_folder()
        elif mode_nb == 1 :
            self.auto = False
            self.scan_folder()
        elif mode_nb == 2 : 
            self.app.get_URL_wnd()

    def update_config(self):
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        for key in self.params.keys() :
            self.params[key] = self.app.config[key].get()
                    
        util.update_config(self.params, self)
        self.app.global_start_wnd()

    def manual_tagging(self):
        self.warn("manual tagging not yet implemented")
        self.skip()

    def retry(self) : 
        util.rm_file(self.current_image_name)
        self.current_image_name = ""
        self.app.prep_search_wnd(self.a_t[0], self.a_t[1])

    def download(self) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        # getting info
        url=self.app.input_url.get()
        no_playlist = not self.app.playlist.get()
        
        self.app.dl_wnd(no_playlist) # making window
        self.yt_logger = self.app.dl_logger(self.app)        
        success = dls.dl_music(url,no_playlist,self.yt_logger,[self.app.dl_hook])
        if not success : 
            if self.ask("Downloading failed, retry ?") :
                self.app.get_URL_wnd()
            else : 
                self.app.ending_wnd()    
        else :
            self.app.dl_status.set("All done") 
            self.app.update()
            
            # If only one file was dl semi-auto process else full auto
            self.auto = not no_playlist 
            
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
            self.app.warn("no music file found")
            self.app.ending_wnd()

        elif self.auto :
            self.current_file_name = ""
            self.app.waiting_wnd()
            self.auto_process()

        elif wrong_format:
            self.app.warn("file " + wrong_file_name +" format unsupported")
            self.scan_data()
            
        else : 
            self.scan_data()

    def auto_process(self) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)

        # trying to see if there are correct tags
        self.current_file_name = self.file_name[self.file_nb]
        title, artist, album, encoded_by = self.tagger.read_tags(self.current_file_name)
        
        #updating progress 
        self.app.tmp_cf.set(self.current_file_name)
        self.app.progress_auto.set("file n°"+str(self.file_nb)+" out of "+str(self.total_file_nb))
        self.app.update()

        #preparing search
        if type(title) != type(None):
            title = util.remove_feat(title) 
        else :
            self.skip_auto()
        if type(artist) == type(None) or artist == "None":
            artist = ""      

        if encoded_by == self.SIGN: # TODO useless for auto ?
            if not self.ask(" file : " + self.current_file_name + " has already been treated. Do you want to change something ?") :
                self.move_file(self.params['folder_name']+os.path.sep+slugify(artist, separator=" ",lowercase=False)+os.path.sep+slugify(album, separator=" ",lowercase=False))  # just moving the file in correct directory

        # searching and processing
        items, certain = self.web.get_basic_info(artist, title)

        if items :         
            track = items[0]
            track = self.web.get_advanced_info(track)
            if certain and util.similar(artist,track['artists'][0]['name']):
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
            self.app.verifications_wnd() # displaying all files
 
    def prep_reset(self) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)

        # removing all checked songs from lst
        nb = 0
        for i in range(self.total_file_nb) :
            if self.app.retry_bt[i].get() :
                self.app.tmp_file.pop(i-nb)
                nb +=1
                self.finished = False
        
        # treating files / reset if none are correct
        self.remaining_file_nb = len(self.app.tmp_file)
        self.file_nb = 0
        if self.remaining_file_nb == 0 :
            self.reset_all()
        else :
            self.prep_next()

    def prep_next(self) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        # preparing for next processing 
        self.current_file_name = self.app.tmp_file[self.file_nb]['file_name']
        track = self.app.tmp_file[self.file_nb]['info']
        tmp = slugify(track['album']['name']+"_artwork")+".jpg"
        self.current_image_name = dls.dl_image(track['album']['artwork'], tmp, self)
        self.update_file(track)

    def scan_data(self):
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        # trying to see if there are correct tags
        self.current_file_name = self.file_name[self.file_nb]
        title, artist, album, encoded_by = self.tagger.read_tags(self.current_file_name)

        # preparing search
        if type(title) != type(None):
            title = util.remove_feat(title) 
        else :
            title = ""
        if type(artist) == type(None) or artist == "None":
            artist = ""            
        
        # checks wether program already processed file 
        if encoded_by == self.SIGN:
            if not self.ask(" file : " + self.current_file_name + " has already been treated. Do you want to change something ?") :
                self.move_file(self.params['folder_name']+os.path.sep+slugify(artist, separator=" ",lowercase=False)+os.path.sep+slugify(album, separator=" ",lowercase=False))  # just moving the file in correct directory 
        
        self.app.prep_search_wnd(artist, title)

    def make_search(self):
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        #read entries
        title = self.app.title_ent.get()
        artist = self.app.artist_ent.get()
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
        if self.current_image_name != tmp : #checking wether it is same as previous TODO maybe compare urls instead ?
            util.rm_file(self.current_image_name)
            self.current_image_name = dls.dl_image(track['album']['artwork'], tmp, self)
        
        self.app.dispaly_infos_wnd(track)


    def update_file(self, track) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        
        # preparing new file name and directory path 
        if track['track_number'] != None :
            if track['track_number'] < 10 :
                new_file_name = "0" + str(track['track_number']) + "-" + slugify(track['name'],separator='_') 
            else :
                new_file_name = str(track['track_number']) + "-" + slugify(track['name'],separator='_')
        else :
            new_file_name = slugify(track['name'],separator='_')
        new_file_name = new_file_name + self.file_extension[self.file_nb]  #adding extension
        
        try :
            # making sure the file is writable :
            os.chmod(self.current_file_name, 448)

            # changing name of the file
            os.path.realpath(self.current_file_name)
            os.rename(self.current_file_name, new_file_name)
            self.current_file_name = new_file_name  
        
        except FileNotFoundError :
            self.app.warn("File was moved. Skipping file")            
            self.skip()  # skipping file 

        except Exception as e :
            logger.error(e.args)
            self.app.warn("File couldn't be edited. Skipping file") 
            self.skip()  # skipping file 
            
        # adding featured artist to title 
        nb_artist = len(track['artists'])
        if nb_artist == 2:
            track['name'] = track['name']+" ("+self.params['feat_acronym']+" "+track['artists'][1]['name']+")"  # correct title
        elif nb_artist > 2:
            track['name'] = track['name']+" ("+self.params['feat_acronym']+" "+track['artists'][1]['name']+ \
                                            " & "+track['artists'][2]['name']+")"  # correct title
        
        # modifying the tags
        ret = self.tagger.update_tags(self.current_file_name, self.current_image_name, track)
            
        if ret > 0 :
            self.app.warn("error during tagging. Skipping file")
            self.skip()
        else :
            self.move_file(self.params['folder_name']+os.path.sep+slugify(track['artists'][0]['name'], separator=" ",lowercase=False)+os.path.sep+slugify(track['album']['name'], separator=" ",lowercase=False))
            

    def move_file(self, direction) :
        logger.debug("in func : " + inspect.currentframe().f_code.co_name)
        try :
            if os.path.exists(direction+os.path.sep+self.current_file_name) :
                self.app.warn("file already exists in folder \nkeeping this file in main folder")
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
            self.app.warn("Unexpected error:" + e + "\nkeeping this file in main folder")
            
        if self.remaining_file_nb > 1:
            self.file_nb += 1  # file being treated = next in the list
            self.remaining_file_nb -= 1  # one file done
            if not self.auto :
                self.scan_data()
            else :
                self.prep_next() 
        else:
            self.app.ending_wnd()  # Ending program (or restarting)

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
            self.app.ending_wnd() # Ending program (or restarting)
    
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
                self.app.global_start_wnd()
            
    def end_all(self) :
        sys.exit("")

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
