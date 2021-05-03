# -*-coding:utf-8 -*
import os

import sys   # to get the name of the prog file
import time  # for sleep function

# for file modification
import json   # to parse config file
import shutil  # to move file
import stat   # to change read/write file status

# to 'slugify' string
from slugify import slugify 

# to display image(not great) and make user search manually
import webbrowser  # to open url in browser

# for spotify api
import spotipy  # Spotify API
from spotipy.oauth2 import SpotifyClientCredentials

#Local libs
import MEPInterface 
import Tagger
from Downloads import dl_image
from Downloads import dl_music
from Utilitaries import *


# for debug only
#import pprint

def main():
    # Variable initialization
    # local
    treated_file_nb = 0
    remaining_file_nb = 0
    file_nb = 1
    state = 0
    not_supported_extension = [".m4a", ".flac", ".mp4", ".wav", ".wma", ".aac"]
    file_extension = [".mp3"]   # will store all file extensions
    file_name = ["music.mp3"]   # will store all file names
    ignore = ["music.mp3"]
    title = ""  # temporary string to store track title
    artist = ""  # temporary string to store artist name
    Is_Sure = True  # to check wether a file needs to be checked by user
    no_playlist = True # for downloading

    # Getting path (in the directory of the program)
    #path = ""#os.path.dirname(os.path.realpath(__file__)) + os.path.sep
    # global (to be shared with other libraries)
    params = {} 
    params['add_signature'] = False # param (maybe changed in config... not sure yet)
    params['debug'] = False # param (maybe changed in config... not sure yet)
    params['accepted_extensions'] = {}
    params['accepted_extensions'] = [".mp3"]  # list of all accepted extensions

    if params['add_signature'] :
        params['signature'] = "MEP by GM"
    else : 
        params['signature'] = "-+-"   

    # to display info etc
    interface = MEPInterface.Interface(params)

    # getting info from config file :
    config = {}
    try:
        with open("config.json", mode="r") as j_object:
            config = json.load(j_object)

    except FileNotFoundError:
        interface.warning("No config file found", "using standard setup")

    except json.JSONDecodeError as e:
        interface.warning("At line " + str(e.lineno)+ " of the config file, bad syntax (" + str(e.msg) + ")", "using standard setup") 
    
    except Exception as e :
        interface.warning("unknown error : " + str(e) , "using standard setup")

    params['prefered_feat_acronyme'] = str (config.get("prefered_feat_sign", "feat."))
    params['default_genre'] = str(config.get("default_genre","Other"))
    params['folder_name'] = str (config.get("folder_name","music"))
    params['get_label'] = bool (config.get("get_label",True))
    params['get_bpm'] = bool (config.get("get_bpm",True))
    params['get_lyrics'] = bool (config.get("get_lyrics",True))
    params['store_image_in_file'] = bool (config.get("store_image_in_file",True))

    #selecting mode
    mode_nb = interface.global_start()

    if mode_nb == 1:  # full auto
        params['all_Auto'] = True
        params['Assume_mep_is_right'] = True
        params['Open_image_auto'] = False

    elif mode_nb == 2:  # semi auto
        params['all_Auto'] = False
        params['Assume_mep_is_right'] = True
        params['Open_image_auto'] = False

    elif mode_nb == 3 : # start by downloading from yt
        params['all_Auto'] = False
        params['Assume_mep_is_right'] = True
        params['Open_image_auto'] = False
        no_playlist = not interface.ask("download playlists ?")
        state = 2 #special start (skipping scan and )
    

    else :
        mode_nb = 4  # discovery
        params['all_Auto'] = False
        params['Assume_mep_is_right'] = False
        params['Open_image_auto'] = True

    
    #initialising libs
    tagger = Tagger.Tagger(params)

    # Spotify api autorisation Secret codes (DO NOT COPY / SHARE)
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fb69ab85a5c749e08713458e85754515",
                                                               client_secret= "ebe33b7ed0cd495a8e91bc4032e9edf2"))        
    
    #adding folder if not existing
    if params['folder_name'] not in os.listdir():
        os.makedirs(params['folder_name'])

    # switch case equivalent
    while True:
        #print("STATE : "+str(state)) #DEBUG
        # ----------------------------------------------------------------------------------------------------------- 0 #
        # STATE 0 : Scanning folder
        if state == 0:
            state = 1 # Default = get title and artist automatically

            # scanning folder
            wrong_format = False
            for temp_file_name in os.listdir():
                _ , temp_file_extension = os.path.splitext(temp_file_name)

                if temp_file_extension in params['accepted_extensions'] and temp_file_name not in ignore:
                    file_name.append(temp_file_name)
                    file_extension.append(temp_file_extension)
                    remaining_file_nb += 1

                elif (temp_file_extension in not_supported_extension):
                    wrong_format = True
                    wrong_file_name = temp_file_name

            # saving total number
            total_file_nb = remaining_file_nb

            if wrong_format:
                interface.wrong_format(wrong_file_name)
                time.sleep(4)
                state = 10

            elif total_file_nb <= 0:  # no music file was found
                state = 10

        # ----------------------------------------------------------------------------------------------------------- 1 #
        # STATE 1 : get title and artist automatically
        elif state == 1:
            state = 3  # Default = search info on track 
            interface.start_process(file_nb, total_file_nb, file_name[file_nb])

            # trying to see if there are correct tags
            title, artist, encoded_by = tagger.read_tags(file_name[file_nb])

            if type(title) != type(None):
                title = remove_feat(title)
                if type(artist) == type(None) or artist == "None":
                    artist = "not found"

                # Displays if at least the title was found
                interface.artist_and_title(artist, title)
                
                # checks wether program already processed file (TODO delete ?)
                if encoded_by == params['signature']:
                    interface.already_treated()
                    if interface.ask("want to modify something ? "):
                        # getting the user to add title and artist
                        (artist, title) = interface.get_title_manu()

                    else:
                        new_file_name = file_name[file_nb]
                        state = 6  # just moving the file in correct directory

                elif mode_nb == 3 : 
                    pass #assuming tags are ok
                elif interface.ask("Wrong ?"):
                    # getting the user to add title and artist
                    (artist, title) = interface.get_title_manu()

            else:
                if params['all_Auto']:
                    interface.error(4) # no usable tags
                    state = 20  # Skip track
                else:
                    (artist, title) = interface.get_title_manu("no title found")
        

        # ----------------------------------------------------------------------------------------------------------- 2 #
        # STATE 2 : dl url
        elif state == 2 :
            state = 3 # Default = Search info on track
            url = interface.get_URL()
            dl_music(url, no_playlist, interface.Dl_Logger(), [interface.Dl_hook])
            state = 0
            
            """file_name.append(dl_music(interface.get_URL(),path))
            file_extension.append(".mp3")
            remaining_file_nb += 1
            total_file_nb = remaining_file_nb
            interface.start_process(file_nb, total_file_nb, file_name[file_nb])
            title, artist, encoded_by = tagger.read_tags(path + file_name[file_nb])"""
            #interface.artist_and_title(artist, title)


        # ----------------------------------------------------------------------------------------------------------- 3 #
        # STATE 3 : Search info on track
        elif state == 3:
            state = 32  # Default = getting genre (track object and title needed)

            # Search for more info on the track using spotify api
            search = "track:" + title.replace("'", "") + " artist:" + artist
            results = sp.search(q= search, type = "track", limit = 2)
            items = results['tracks']['items']

            # Can a result be found
            if len(items) > 0:
                Is_Sure = True
                if (items[0]['album']['artists'][0]['name'] == 'Various Artists') :
                    track = items[1] # index 0 was a playlist TODO maybe add better checks
                else : 
                    track = items[0]

                track['name'] = remove_feat(track['name'])  # in case of featurings
                track['album']['artwork'] = track['album']['images'][0]['url']
                track['lyrics'] = {}

            
            elif params['all_Auto']:
                interface.error(5)  # music not found -> skipping
                state = 20  # skip track

            else :
                # trying without the artist only if user can verify
                search = "track:" + title.replace("'", "")
                results = sp.search(q=search, type = "track", limit = 1)
                items = results['tracks']['items']
                if len(items) > 0:
                    Is_Sure = False
                    track = items[0]
                    track['name'] = remove_feat(track['name'])  # in case of featurings
                    track['album']['artwork'] = track['album']['images'][0]['url']
                    track['lyrics'] = {}

            

                elif interface.ask(reason = "error 808 : music not found..." , message = "Do you want to retry with another spelling ?"):
                    (artist, title) = interface.get_title_manu("")
                    state = 3  # search info on track

                elif interface.ask("Fill the data manually ?"):
                    state = 31  # manual tagging

                else:
                    interface.warning("no action required", "file was skipped")  # music not found# nothing could be done / wanted to be done
                    state = 20  # skip track

        # ----------------------------------------------------------------------------------------------------------- 31 #
        # STATE 31 : manual tagging
        elif state == 31:
            state = 33  # Default = getting other info automatically (wo/ spotify)

            interface.manual_tagging(artist, title)

            # init variables (if no track object was created before hand)
            track = {}
            track['artists'] = [{}]
            track['album'] = {}
            track['lyrics'] = {}
            
            # already filled data
            track['name'] = title
            track['artists'][0]['name'] = artist
            
            #search to help user
            search = "https://www.google.com/search?q=" + slugify(track['name']) + "+" + slugify(track['artists'][0]['name'])
            webbrowser.open(search) 

            # user fills data
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

        # ----------------------------------------------------------------------------------------------------------- 32 #
        # STATE 32 : Getting genre + other info auto
        elif state == 32:
            state = 4 # Default = User verif

            # getting genre
            results = sp.artist(track['artists'][0]['id'])
            if len(results['genres']) > 0:
                track['genre'] = results['genres'][0]
            else:
                track['genre'] = params['default_genre']

            # getting label and copyright
            if params['get_label']:
                results = sp.album(track['album']['id'])
                if len(results) > 0:
                    track['album']['copyright'] = results['copyrights'][0]['text']
                    track['album']['label'] = results['label']
                else:
                    # default
                    track['album']['copyright'] = ""
                    track['album']['label'] = ""

            # getting BPM
            if params['get_bpm']:
                results = sp.audio_analysis(track['id'])
                if len(results) > 0:
                    track['bpm'] = int(results['track']['tempo'])
                else:
                    track['bpm'] = 0  # default

            #getting lyrics 
            if params['get_lyrics']: 
                (track['lyrics']['text'], track['lyrics']['service']) = get_lyrics(track['artists'][0]['name'], track['name'])
            else :
                track['lyrics']['service'] = "ignored"
                track['lyrics']['text'] =  ""

            

        # ----------------------------------------------------------------------------------------------------------- 33 #
        # STATE 33 : getting other info (if file was not found on spotify)
        elif state == 33 :
            state = 4 # Default = User verif

            # info that can't be accessed is switched to default
            track['disc_number'] = 1
            track['genre'] = params['default_genre']

            if params['get_label'] :
                track['album']['copyright'] = None
                track['album']['label'] = None
            if params['get_bpm'] : 
                track['bpm'] = None  

            #getting lyrics 
            if params['get_lyrics']: 
                (track['lyrics']['text'], track['lyrics']['service']) = get_lyrics(track['artists'][0]['name'], track['name'])
            else :
                track['lyrics']['service'] = "ignored"
                track['lyrics']['text'] =  ""

        # ----------------------------------------------------------------------------------------------------------- 4 #
        # STATE 4 : User verification (track object and title needed)
        elif state == 4:
            state = 5  # Default = file update (track object needed)

            interface.track_infos(Is_Sure , title = track['name'],
                                  artists = track['artists'],
                                  album = track['album']['name'],
                                  genre = track['genre'],
                                  release_date = track['album']['release_date'],
                                  track_nb = track['track_number'],
                                  total_track_nb = track['album']['total_tracks'],
                                  lyrics_service = track['lyrics']['service'])

            # displaying image (TODO improve)
            if params['Open_image_auto']:
                webbrowser.open(track['album']['artwork'])

            # switch state
            if params['Assume_mep_is_right'] and Is_Sure:
                pass # state  = 5

            elif not interface.ask("wrong song ?"):
                pass # state  = 5

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
            state = 6 # Default = Moving file

            try :
                # making sure the file is writable : 
                os.chmod(file_name[file_nb], stat.S_IRWXU)

                # preparing new file name and directory path 
                if track['track_number'] != None :
                    if track['track_number'] < 10 :
                        new_file_name = "0" + str(track['track_number']) + "-" + slugify(track['name'],separator='_') 
                    else :
                        new_file_name = str(track['track_number']) + "-" + slugify(track['name'],separator='_')
                else :
                    new_file_name = slugify(track['name'],separator='_')
                new_file_name = new_file_name + file_extension[file_nb]  #adding extension

                # changing name of the file
                os.path.realpath(file_name[file_nb])
                os.rename(file_name[file_nb], new_file_name)

                # adding featured artist to title 
                nb_artist = len(track['artists'])
                if nb_artist == 2:
                    track['name'] = track['name']+" ("+params['prefered_feat_acronyme']+track['artists'][1]['name']+")"  # correct title
                elif nb_artist > 2:
                    track['name'] = track['name']+" ("+params['prefered_feat_acronyme']+track['artists'][1]['name']+ \
                                                    " & "+track['artists'][2]['name']+")"  # correct title


                # downloading image 
                image_name = slugify(track['album']['name']+"_artwork")+".jpg"
                image_name = dl_image(track['album']['artwork'], image_name, interface)
                
                # modifing the tags
                ret = tagger.update_tags(new_file_name,image_name,track)
                if ret > 0 :
                    interface.error(ret)
                    state = 20  # skipping file          

                
            except FileNotFoundError :
                interface.error(2)  # file was moved
                state = 20  # skipping file          
            except Exception as e :
                print(e)
                interface.error(1) # file couldn't be edited
                state = 20  # skipping file 

        # ----------------------------------------------------------------------------------------------------------- 6 #
        # STATE 6 : Moving file
        elif state == 6:
            # No default state (either restart or ending)

            folder = params['folder_name']+os.path.sep+track['artists'][0]['name']+os.path.sep+track['album']['name']
            try :
                if os.path.exists(folder+os.path.sep+new_file_name) :
                    interface.warning("file already exists in folder", "keeping this file in main folder")
                    ignore.append(file_name[file_nb])
                else :
                    if not os.path.exists(folder):
                        os.makedirs(folder) #creating folder

                    shutil.move(new_file_name,folder) # place in correct folder
                    treated_file_nb += 1  # file correctly treated

            except Exception as e:
                interface.warning("Unexpected error:" + sys.exc_info()[0], "keeping this file in main folder")
                
            if remaining_file_nb > 1:
                file_nb += 1  # file being treated = next in the list
                remaining_file_nb -= 1  # one file done
                state = 1  # get title and artist automatically (new song)
            else:
                state = 10  # Ending program (or restarting)

        # ----------------------------------------------------------------------------------------------------------- 20 #
        # STATE 20 : Skipping track
        elif state == 20:
            ignore.append(file_name[file_nb])
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
                time.sleep(1)
                # reseting variables
                file_extension = [".mp3"]
                file_name = ["music.mp3"]
                file_nb = 1
                remaining_file_nb = 0
                total_file_nb = 0
                state = 0
            elif mode_nb == 3 :
                # reseting variables
                file_extension = [".mp3"]
                file_name = ["music.mp3"]
                file_nb = 1
                remaining_file_nb = 0
                total_file_nb = 0
                state = 2
            else:
                interface.end_full_auto(total_file_nb, treated_file_nb)
                sys.exit("")


if __name__ == '__main__':
    main()
