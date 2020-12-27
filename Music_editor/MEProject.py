# -*-coding:utf-8 -*

import os
import sys   # to get the name of the prog file
import time  # for sleep function
from pathlib import Path  # to get path to directory

# for file modification
import eyed3  # to parse mp3 files
import json   # to parse config file
import shutil  # to move file
import stat   # to change read/write file status

# to 'slugify' string
import re
import unicodedata

# for image
import requests   # to get image from the web
import webbrowser  # to open url in browser

# for spotify api
import spotipy  # Spotify API
from spotipy.oauth2 import SpotifyClientCredentials



# for debug only
# import pprint

# modifiable variables in config file TO UPDATE !!!!!!!!!!!!!!!!!!!!!!
'''
folder_name             : Name of the folder where all the music will be droped
prefered_feat_acronyme  : Used when a track has multiple artist. The title will look like : *title_of_track* (*prefered_feat_acronyme* *other artist*)
default_genre           : If MEP doesn't find a genre this is what will be written in the file
mode                    : 1 is full auto, 2 is semi auto and 3 is discovery
'''

# global variables
treated_file_nb = 0
remaining_file_nb = 0
file_nb = 1
state = 0
All_Auto = bool

class MEP:
    def __init__(self, interface, debug):
        self.debug     = debug
        self.interface = interface

    # Removes the "'feat." type from the title
    # @returns corrected title
    def remove_feat(self, title):
        if "(Ft" in title or "(ft" in title or "(Feat" in title or "(feat" in title:
            # complicated in case there is anothere paranthesis in the title
            b = []
            b = title.split("(")
            title = b[0]
            for i in range(1, len(b)-1):
                title = title + "(" + b[i]
        return title.strip()


    # removes unwanted characteres to make the name file friendly
    # @return value the correcter string
    def slugify(self, value):
        value = unicodedata.normalize('NFKC', value)
        value = re.sub(r'[^\w\s-]', '', value).strip().lower()
        value = re.sub(r'[-\s]+', '-', value)

        return value

    # Downloading picture from specified url as specified filename to specified path
    # @returns the complete path of the new downloaded file if worked correctly, else returns 0
    def get_file(self, file_url, filename, path):
        path = path + filename
        # Open the url image, set stream to True, this will return the stream content.
        try:
            r = requests.get(file_url, stream=True)

            # Check if the image was retrieved successfully
            if r.status_code == 200:
                # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                r.raw.decode_content = True

                # Open a local file with wb ( write binary ) permission.
                with open(path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)

                return path
            else:
                self.interface.warning("image url can't be reached", "not adding image to file")
                return ""

        except:
            self.interface.warning("image downloading failed", "not adding image to file")
            return ""
        


class Interface:
    """ Everything that has to do with the visual interface is done here"""

    def __init__(self, accepted_extensions, debug):
        # storing a few parameters
        self._ignore = ["MEProject.exe"]
        self._param_accepted_extension = accepted_extensions
        self._params = {}
        self._params["debug"] = debug
        self._params["all auto"] = False
        # will inherit from pyglet ?
        
    """ Asking user a yes no question 
        @param message the string to be displayed as a question
        @return True or False (depending on user response) """
    def ask(self, message, reason = ""):
        if self._params["all auto"]:
            return False
        if (reason != ""):
            print(reason)
        ans = input("-> " + message + " (y/n) : ")
        if ans == 'y' or ans == 'Y':
            return True
        else:
            return False

    """ Welcoming user and getting mode
        @return mode_nb the mode number (between 1 and 3) chosen by user """
    def global_start(self):
        mode_name = ['full auto', 'semi auto', 'discovery']
        print("")
        print("         Welcome to MEProject")
        print("")
        print("-------------------------------------")
        print("|           mode selection          |")
        print("+-----------------------------------+")
        print("|     1     |     2     |     3     |")
        print("+-----------+-----------+-----------+")
        print("| full auto | semi auto | discovery |")
        print("-------------------------------------")
        print("")
        mode_nb = int(input("mode : "))
        
        if mode_nb >= 3:
            mode_nb = 3
        elif mode_nb <= 1:
            mode_nb = 1
            self._params["all auto"] = True

        print("Now entering mode {}".format(mode_name[mode_nb-1]))
        print("\n")
        return mode_nb

    """ error message for when user dropped a file in wrong format
        Displays the name of file in wrong format and a list of accepted formats"""
    def wrong_format(self, wrong_file_name):
        if (wrong_file_name not in self._ignore):
            print("the file '{}' is not in supported format" .format(wrong_file_name))
            print("the supported formats are : ")
            for i in range(0, len(self._param_accepted_extension)):
                print(self._param_accepted_extension[i])
            self._ignore.append(wrong_file_name)

    """ Beginning of the process for a new file
        Displays  what file is being treated"""
    def start_process(self, file_nb, total_file_nb, file_name):
        print("-------------------------------------------------------\n")
        print("file {} out of {} : '{}'".format(
            file_nb, total_file_nb, file_name))

    """ Showing artist and title (reduced version of track_info)"""
    def artist_and_title(self, artist, title):
        print("artist : {}".format(artist))
        print("title  : {}".format(title))

    """ error message : file already went through the system
        is linked to an ask
        """
    def already_treated(self):
        print("file has already been treated with MEP")

    """ Getting title and artist from user
        @return (artist, title) the info given by user 
        """
    def get_title_manu(self, reason= ""):
        if reason != "" :
            print(reason)

        print("Let's do it manually then !")
        print("")
        artist = input("artist name : ")
        title = input("track name  : ")
        return (artist, title)



    def manual_tagging(self, artist, title):
        print("ok let's go !")
        self.artist_and_title(artist, title)
        # will need to be expanded

    """ Displaying info on the track
        Visual might change depending on information"""
    def track_infos(self, Is_Sure, title, artists, album, genre, release_date, track_nb, total_track_nb):
        if Is_Sure:
            print("")
            print("We have a match !")
            print("")
        else:
            print("")
            print("exact track not found")
            print("")
            print("Potential track :")
        nb_artist = len(artists)

        # Basic infos :
        if nb_artist == 1:  # no feat
            print("{} by {} :".format(title, artists[0]['name']))

        elif nb_artist == 2:
            print("{} by {} featuring {}".format(
                title, artists[0]['name'], artists[1]['name']))

        else:
            print("{} by {} featuring {} & {}".format(
                title, artists[0]['name'], artists[1]['name'], artists[2]['name']))

        # In depth infos :
        print("album        : {}\nGenre        : {}\nrelease date : {}\nTrack number : {} out of {}\n".format(
            album, genre, release_date, track_nb, total_track_nb))
        # there would also be a picture display if all was great...

    """ error message for when a file is skiped 
        Displays error number and explication"""
    def error(self, error_nb):
        print(    "---------------------------------")
        print(    "| file was skipped | error n°{}  |".format(error_nb)) 
        print(    "---------------------------------")
        if error_nb == 1:
            print("|    file couldn't be edited    |")
        elif error_nb == 2:
            print("| file was moved during process |")
        elif error_nb == 3:
            print("|  file already in the folder   |")
        elif error_nb == 4:
            print("| file didn't have usable tags  |")
        elif error_nb == 5:
            print("|  No matching track was found  |")
        print(    "---------------------------------\n")

    def warning(self, problem, solution):
        print("[WARNING] " + problem + " -> " + solution )
    
    """ Closing program when in full auto mode 
        Gives litle summary of actions (nb of files processed out of total)"""
    def end_full_auto(self, total_file_nb, treated_file_nb) :
        """ Closing program when in full auto mode 
            Gives litle summary of actions (nb of files processed out of total)"""

        if not self._params["debug"]: 
            if total_file_nb == 0:
                input("No file found")
            else:
                input("{} files correctly processed out of {}".format(
                    treated_file_nb, total_file_nb))
        else:
            print("{} files correctly processed out of {}".format(
                treated_file_nb, total_file_nb))


def main():
    global treated_file_nb, remaining_file_nb, file_nb, All_Auto, state

    # param (maybe changed in config... not sure yet)
    add_signature = False
    signature = "MEP by GM"

    # Variable initialization
    debug = False
    Is_Sure = True  # to check wether a file needs to be checked by user
    accepted_extensions = [".mp3"]  # list of all accepted extensions
    not_supported_extension = [".m4a", ".flac", ".mp4", ".wav", ".wma", ".aac"]
    file_extension = [".mp3"]   # will store all file extensions
    file_name = ["music.mp3"]   # will store all file names
    title = ""  # temporary string to store track title
    artist = ""  # temporary string to store artist name

    eyed3.log.setLevel("ERROR")  # hides errors from eyed3 package
    interface = Interface(accepted_extensions, debug)
    mep = MEP(interface, debug)

    # Getting path (in the directory of the program)
    path = os.path.dirname(os.path.realpath(__file__))
    antislash = "\ "  # adding antislash (not elegant but works)
    antislash = antislash[:1]
    path = path+antislash

    # getting the name of the prog
    prog_name = os.path.abspath(sys.argv[0])
    prog_name = prog_name[len(path):]  # removing path from the file name

    # getting info from config file :
    try:
        with open(path+"config.json", mode="r") as j_object:
            config = json.load(j_object)
        
        prefered_feat_acronyme = str (config["prefered_feat_sign"])
        default_genre = str(config["default_genre"])
        folder_name = str (config["folder_name"])
        get_label = bool (config["get_label"])
        get_bpm = bool (config["get_bpm"])
        store_image_in_file = bool (config["store_image_in_file"])

    except FileNotFoundError:
        interface.warning("No config file found", "using standard setup")  # TODO make ti better
        prefered_feat_acronyme = "feat."
        default_genre = "Other"
        folder_name = "music"
        get_label = True
        get_bpm = True
        store_image_in_file = True

    except json.JSONDecodeError as e:
        interface.warning("At line " + str(e.lineno)+ " of the config file, bad syntax (" + str(e.msg) + ")", "using standard setup") 
        prefered_feat_acronyme = "feat."
        default_genre = "Other"
        folder_name = "music"
        get_label = True
        get_bpm = True
        store_image_in_file = True
    
    except Exception as e :
        interface.warning("unknown error : " + str(e.msg) , "using standard setup")
        prefered_feat_acronyme = "feat."
        default_genre = "Other"
        folder_name = "music"
        get_label = True
        get_bpm = True
        store_image_in_file = True

    mode_nb = interface.global_start()

    if mode_nb == 1:  # full auto
        All_Auto = True
        Assume_mep_is_right = True
        Open_image_auto = False
    elif mode_nb == 2:  # semi auto
        All_Auto = False
        Assume_mep_is_right = True
        Open_image_auto = False
    else:
        mode_nb = 3  # discovery
        All_Auto = False
        Assume_mep_is_right = False
        Open_image_auto = True


    # Spotify api autorisation Secret codes (DO NOT COPY / SHARE)
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fb69ab85a5c749e08713458e85754515",
                                                               client_secret= "ebe33b7ed0cd495a8e91bc4032e9edf2"))


    while True:
        #print("STATE : "+str(state)) #DEBUG
        # ----------------------------------------------------------------------------------------------------------- #
        # STATE 0 : Scanning folder
        if state == 0:
            # scanning folder
            music_file_found = False
            folder_found = False
            wrong_format = False
            for temp_file_name in os.listdir(path):
                temp, temp_file_extension = os.path.splitext(temp_file_name)

                if temp_file_extension in accepted_extensions:
                    file_name.append(temp_file_name)
                    file_extension.append(temp_file_extension)
                    remaining_file_nb += 1
                    music_file_found = True

                elif temp_file_name == folder_name:
                    folder_found = True

                elif (temp_file_extension in not_supported_extension):
                    wrong_format = True
                    wrong_file_name = temp_file_name

            # if there isn't a folder already, creates it
            if not folder_found:
                os.makedirs(path+folder_name)

            # saving total number
            total_file_nb = remaining_file_nb

            if music_file_found:
                state = 1  # get title and artist automatically

            elif wrong_format:
                interface.wrong_format(wrong_file_name)
                time.sleep(4)
                state = 10

            else:  # no file other than program and directory was found
                state = 10

        # ----------------------------------------------------------------------------------------------------------- 1 #
        # STATE 1 : get title and artist automatically
        elif state == 1:
            interface.start_process(file_nb, total_file_nb, file_name[file_nb])
            temp_path = path + file_name[file_nb]

            # trying to see if there are correct tags
            eyed3.load(temp_path)  # creating object
            tag = eyed3.id3.tag.Tag()
            tag.parse(fileobj=temp_path)

            if type(tag.title) != type(None):
                title = mep.remove_feat(tag.title)

                if type(tag.artist) == type(None) or tag.artist == "None":
                    artist = "not found"
                else:
                    artist = tag.artist

                # Displays if at least the title was found
                interface.artist_and_title(artist, title)
                

                if tag.encoded_by == signature:
                    interface.already_treated()
                    if interface.ask("want to modify something ? "):
                        # getting the user to add title and artist
                        (artist, title) = interface.get_title_manu()
                        state = 3  # search info on track (title and artist needed)

                    else:
                        new_file_name = file_name[file_nb]
                        state = 6  # just moving the file in correct directory

                elif interface.ask("Wrong ?"):
                    # getting the user to add title and artist
                    (artist, title) = interface.get_title_manu()
                    state = 3  # search info on track (title and artist needed)

                else:
                    state = 3  # search info on track (title and artist needed)

            else:
                
                if All_Auto:
                    interface.error(4) # no usable tags
                    state = 20  # Skip track
                else:
                    (artist, title) = interface.get_title_manu("no title found")
                    state = 3  # search info on track
            

        # ----------------------------------------------------------------------------------------------------------- 3 #
        # STATE 3 : Search info on track
        elif state == 3:
            # Search for more info on the track using spotify api
            search = "track:" + title.replace("'", "") + " artist:" + artist
            results = sp.search(q= search, type = "track", limit = 1)
            items = results['tracks']['items']
            # pprint.pprint(results) #debug

            # Can a result be found
            if len(items) > 0:
                Is_Sure = True
                track = items[0]
                track['album']['artwork'] = track['album']['images'][0]['url']
                # switch state
                state = 32  # Getting genre (track object and title needed)

            elif not All_Auto:
                # trying without the artist only if user can verify
                search = "track:" + title.replace("'", "")
                results = sp.search(q=search, type = "track", limit = 1)

                items = results['tracks']['items']
                if len(items) > 0:
                    Is_Sure = False
                    track = items[0]
                    track['album']['artwork'] = track['album']['images'][0]['url']
                    state = 32  # Getting genre (track object and title needed)

            # music not found -> switch state
            elif All_Auto:
                state = 20  # skip track

            elif interface.ask(reason = "error 808 : music not found..." , message = "Do you want to retry with another spelling ?"):
                (artist, title) = interface.get_title_manu("")
                state = 3  # search info on track

            elif interface.ask("Fill the data manually ?"):
                state = 31  # manual tagging

            else:
                # nothing could be done / wanted to be done
                state = 20  # skip track

        # ----------------------------------------------------------------------------------------------------------- 31 #
        # STATE 31 : manual tagging
        elif state == 31:
            interface.manual_tagging(artist, title)

            # init variables (if no track object was created before hand)
            track = {}
            track['artists'] = [{}]
            track['album'] = {}

            # user filled data
            track['name'] = title
            track['artists'][0]['name'] = artist
            search = "https://www.google.com/search?q=" + mep.slugify(track['name']) + "+" + mep.slugify(track['artists'][0]['name'])
            webbrowser.open(search) 

            if interface.ask("more than one artist ?"):
                track['artists'].append({'name': input("second artist : ")})
                y = input(
                    "third artist (just press enter if there isn't another): ")
                if y != "":
                    track['artists'].append({'name': y})

            track['album']['name'] = input("album        : ")
            track['album']['release_date'] = input("year         : ")
            track['track_number'] = int(input("track number : "))   # TODO add szecurity (check if its int) error : ValueError:
            track['album']['total_tracks'] = int(input("out of       : "))

            # getting user to pick an artwork
            track['album']['artwork'] = input("image url    : ")

            # TODO default stuff : might try to do other searches (with album for exemple) to complete those
            track['disc_number'] = None
            track['genre'] = default_genre

            if get_label :
                track['album']['copyright'] = None
                track['album']['label'] = None
            if get_bpm : 
                track['bpm'] = None  # default

            state = 4  # user verification

        # ----------------------------------------------------------------------------------------------------------- 32 #
        # STATE 32 : Getting genre + other info auto
        elif state == 32:
            results = sp.artist(track['artists'][0]['id'])
            """pprint.pprint(results)
            for i in range(0,len(results['genres'])) :
                print(results['genres'][i]) #DEBUG"""
            if len(results['genres']) > 0:
                track['genre'] = results['genres'][0]
            else:
                track['genre'] = default_genre

            # getting label and copyright
            if get_label:
                results = sp.album(track['album']['id'])
                if len(results) > 0:
                    track['album']['copyright'] = results['copyrights'][0]['text']
                    track['album']['label'] = results['label']
                else:
                    # default
                    track['album']['copyright'] = ""
                    track['album']['label'] = ""

            # getting BPM
            if get_bpm:
                results = sp.audio_analysis(track['id'])
                if len(results) > 0:
                    track['bpm'] = int(results['track']['tempo'])
                else:
                    track['bpm'] = 0  # default

            state = 4

        # ----------------------------------------------------------------------------------------------------------- 4 #
        # STATE 4 : User verification (track object and title needed)
        elif state == 4:

            track['name'] = mep.remove_feat(track['name'])  # in case of featurings

            interface.track_infos(Is_Sure, title=track['name'],
                                  artists= track['artists'],
                                  album= track['album']['name'],
                                  genre   = track['genre'],
                                  release_date= track['album']['release_date'],
                                  track_nb= track['track_number'],
                                  total_track_nb= track['album']['total_tracks'])

            # displaying image TO CHANGE
            if Open_image_auto:
                webbrowser.open(track['album']['artwork'])

            # switch state
            if Assume_mep_is_right and Is_Sure:
                state = 5  # file update (track object needed)

            elif not interface.ask("wrong song ?"):
                state = 5  # file update (track object needed)

            elif interface.ask("Do you want to retry with another spelling ?"):
                (artist, title) = interface.get_title_manu("")
                state = 3  # search info on track

            elif interface.ask("fill the data manually ?"):
                state = 31
            else:
                interface.error(5) # no matching track found
                state = 20

        # ----------------------------------------------------------------------------------------------------------- 5 #
        # STATE 5 : File update (track object needed)
        elif state == 5:
            
            try :
                # making sure the file is writable : 
                os.chmod(path+file_name[file_nb], stat.S_IRWXU)

                # preparing new file name and directory path TODO check track number make it always 00 and use _ as spaces ?
                if track['track_number'] != None :
                    new_file_name = track['track_number'] + "-" + track['name']
                else :
                    new_file_name = track['name']
                new_file_name = mep.slugify(new_file_name) + file_extension[file_nb]  # removing annoying characters and adding extension

                temp_path = path + file_name[file_nb]
                new_path = path + new_file_name

                # adding featured artist to title 
                nb_artist = len(track['artists'])
                if nb_artist == 2:
                    track['name'] = track['name']+" ("+prefered_feat_acronyme+track['artists'][1]['name']+")"  # correct title
                elif nb_artist > 2:
                    track['name'] = track['name']+" ("+prefered_feat_acronyme+track['artists'][1]['name']+ \
                                                    " & "+track['artists'][2]['name']+")"  # correct title

                # downloading image
                
                image_name = mep.slugify(track['album']['name']+"_artwork")+".jpg"
                image_path = mep.get_file(track['album']['artwork'], image_name, path)
            
                # changing name of the file
                src = os.path.realpath(temp_path)
                os.rename(temp_path, new_path)

                # modifing the tags
                tag = eyed3.id3.tag.Tag()
                if tag.parse(fileobj = new_path):
                    tag.title = track['name']
                    tag.artist = track['artists'][0]['name']
                    tag.genre = track['genre']
                    tag.album = track['album']['name']
                    tag.album_artist = track['artists'][0]['name']
                    tag.track_num = (track['track_number'], track['album']['total_tracks'])
                    tag.disc_num = (track['disc_number'], None)
                    tag.recording_date = eyed3.core.Date.parse(track['album']['release_date'])

                    
                    try : 
                        tag.bpm = track['bpm']
                    except KeyError : # infos not found or not searched
                        pass
                    
                    try :
                        tag.publisher = track['album']['label']
                        tag.copyright = track['album']['copyright']
                    except KeyError : # infos not found or not searched
                        pass

                    if add_signature:
                        tag.encoded_by = signature  # Program signature

                    # works but no way to get info
                    # tag.composer = ""

                    # doesn't work
                    # tag.lyrics = "Escalope pannée" # doenst work + no easy way to get info
                    # tag.artist_origin = "France" # doesent work + no easy way to get info

                    # image
                    if (image_path != "") : 
                        if store_image_in_file :
                            # read image into memory
                            imagedata = open(image_path, "rb").read()

                            # deleting previous artwork if present
                            for i in range(0, len(tag.images)):
                                tag.images.remove(tag.images[i].description)

                            # append image to tags
                            tag.images.set(3, imagedata, "image/jpeg",description=image_name)

                            # removing image from folder
                            os.remove(image_path)

                        else:
                            # moving image in directory (or deleting if already present)
                            if not os.path.exists(path+folder_name+antislash+image_name):
                                shutil.move(image_path, path+folder_name)  # place in first folder
                            else:
                                os.remove(image_path)

                    tag.save(encoding="utf-8")
                    state = 6  # moving file

            except FileNotFoundError :
                interface.error(2)  # file was moved
                state = 20  # skipping file          
            except Exception as e :
                interface.error(1) # file couldn't be edited
                state = 20  # skipping file 

        # ----------------------------------------------------------------------------------------------------------- 6 #
        # STATE 6 : Moving file
        elif state == 6:
            # moving file

            new_path = path + new_file_name

            try :
                if os.path.exists(path+folder_name+antislash+new_file_name):
                    interface.warning("file already exists in folder", "keeping this file in main folder")
                else :
                    treated_file_nb += 1  # file correctly treated
                    shutil.move(new_path, path+folder_name) # place in first folder
                    
            except Exception as e:
                interface.warning("Unexpected error:", sys.exc_info()[0], "keeping this file in main folder")
                

            # changing state
            if remaining_file_nb > 1:
                file_nb += 1  # file being treated = next in the list
                remaining_file_nb -= 1  # one file done
                state = 1  # get title and artist automatically (new song)
            else:
                state = 10  # Ending program (or restarting)

        # ----------------------------------------------------------------------------------------------------------- 20 #
        # STATE 20 : Skipping track (only atteingned from full auto mode)
        elif state == 20:
            if remaining_file_nb > 1:
                file_nb += 1  # file being treated = next in the list
                remaining_file_nb -= 1  # one file done
                state = 1  # Get title and artist auto
            else:
                state = 10  # End prog

        # ----------------------------------------------------------------------------------------------------------- 10 #
        # STATE 10 : Ending program (or restarting)
        elif state == 10:

            if mode_nb == 2:
                # reset variables
                time.sleep(1)
                file_extension = [".mp3"]
                file_name = ["music.mp3"]
                file_nb = 1
                remaining_file_nb = 0
                total_file_nb = 0
                state = 0

            else:
                interface.end_full_auto(total_file_nb, treated_file_nb)

                sys.exit("")


if __name__ == '__main__':
    main()
