# -*-coding:utf-8 -*

import os 
import sys   # to get the name of the prog file
import time  # for sleep function

# for file modification
from pathlib import Path
import json   # to parse config file
import shutil # to move file
import eyed3  # music tag editor 

# for image 
import requests   # to get image from the web 
import webbrowser # to directly open image in browser 

# for spotify api 
import spotipy #Spotify API
from spotipy.oauth2 import SpotifyClientCredentials

# for debug only
import pprint 

# modifiable variables in config file TO UPDATE !!!!!!!!!!!!!!!!!!!!!!
'''
folder_name             : Name of the folder where all the music will be droped
prefered_feat_acronyme  : Used when a track has multiple artist. The title will look like : *title_of_track* (*prefered_feat_acronyme* *other artist*)
default_genre           : If MEP doesn't find a genre this is what will be written in the file
mode                    : 1 is full auto, 2 is semi auto and 3 is discovery
'''

#global variables
treated_file_nb = 0
remaining_file_nb = 0
file_nb = 1
state = 0
All_Auto = bool


# converting user answer (y or n) into true or false
# Special answer : p will end program  (used for debug) 
def question_user(message) :
    global All_Auto
    if All_Auto :
        return False

    ans = input(message+" (y for yes n for no) : ")
    if ans== 'y' or ans == 'Y' :
        return True
    elif ans == 'p' :

        state = 10 # Ending program (or restarting)# emergency stop for debug
    else :
        return False


# Removes the "'feat." type from the title
# @returns corrected title
def remove_feat(title) :
    if "(Ft" in title or "(ft" in title or "(Feat" in title or "(feat" in title:
        # complicated in case there is anothere paranthesis in the title
        b = []
        b = title.split("(")
        title = b[0]
        for i in range (1, len(b)-1):
            title = title + "(" + b[i]
    return title.strip() 

def correct(new_file_name) :
    temp = new_file_name.split('.')
    extension = '.'+ temp[len(temp)-1]
    new_file_name = new_file_name.replace(extension,'') # removing extension
    new_file_name = new_file_name.replace('/','') # removing / . , and "  frome name
    new_file_name = new_file_name.replace('.','') 
    new_file_name = new_file_name.replace(',','') 
    new_file_name = new_file_name.replace('?','')
    new_file_name = new_file_name.replace('"','') + extension
    return new_file_name

# Downloading picture from specified url as specified filename to specified path
# @returns the complete path of the new downloaded file if worked correctly, else returns 0
def get_file(file_url,filename,path) :
    path = path + filename
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(file_url, stream = True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
    
        # Open a local file with wb ( write binary ) permission.
        with open(path,'wb') as f: 
            shutil.copyfileobj(r.raw, f)
        
        return path     
    else:
        return 0

def main():
    global treated_file_nb, remaining_file_nb, file_nb, All_Auto, state

    # Variable initialization
    Is_Sure = True
    store_image_in_file = True
    accepted_extensions = [".mp3"]
    file_extension = [".mp3"]
    file_name = ["music.mp3"]
    title = ""
    artist = ""
    signature = "MEP by GM"

    # Getting path (in the directory of the program) 
    path = os.path.dirname(os.path.realpath(__file__))
    antislash = "\ "
    antislash=antislash[:1]
    path = path+antislash 
    eyed3.log.setLevel("ERROR") # hides errors from eyed3 package

    # getting the name of the prog
    prog_name = os.path.abspath(sys.argv[0])
    prog_name = prog_name[len(path):] #removing path from the file name

    # getting info from config file : 
    with open(path+"config.json", mode="r") as j_object:
        config = json.load(j_object)

    prefered_feat_acronyme = config["prefered_feat_sign"]
    default_genre          = config["default_genre"]      
    folder_name            = config["folder_name"] 


    print("Hello !")
    if config["mode"] == 1 : # full auto
        All_Auto = True
        Assume_mep_is_right = True
        Open_image_auto = False
        print("Mode : full auto")
    elif config["mode"] == 2 : # semi auto
        All_Auto = False
        Assume_mep_is_right = True
        Open_image_auto = False
        print("Mode : semi auto")
    else :
        config["mode"] = 3 # discovery
        All_Auto = False
        Assume_mep_is_right = False
        Open_image_auto = True
        print("Mode : discovery")


    # Spotify api autorisation 
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id = config["client_id"],
                                                           client_secret = config["client_secret"]))
    print("\n")
    while True :

        # ----------------------------------------------------------------------------------------------------------- #
        # STATE 0 : Scanning folder
        if state == 0 : 
            # scanning folder
            music_file_found = False
            folder_found    = False
            wrong_format     = False
            for temp_file_name in os.listdir(path): 
                temp, temp_file_extension = os.path.splitext(temp_file_name)
                
                if temp_file_extension in accepted_extensions :
                    file_name.append(temp_file_name)  
                    file_extension.append(temp_file_extension)
                    remaining_file_nb += 1
                    music_file_found = True

                elif temp_file_name == folder_name :
                    folder_found = True

                elif (temp_file_name != prog_name) and (temp_file_extension != "") and (temp_file_extension != ".json") :
                    wrong_format=True
                    wrong_file_name=temp_file_name
            
            # if there isn't a folder already, creates it
            if not folder_found :
                os.makedirs(path+folder_name)

            # File found ?
            if music_file_found :
                state = 1 # get title and artist automatically
            elif wrong_format :
                # Wrong format Display
                print("the file '{}' is not in supported format" .format(wrong_file_name))
                print("the supported formats are : ")
                for i in range(0,len(accepted_extensions)):
                    print(accepted_extensions[i])
                time.sleep(4)
                state = 10 
            else : # no file other than program and directory was found
                state = 10

        # ----------------------------------------------------------------------------------------------------------- 1 #
        # STATE 1 : get title and artist automatically
        elif state == 1 : 
            print("--------------------------------------------------------------------------")
            print("file {} out of {} : '{}'".format(file_nb,remaining_file_nb+treated_file_nb,file_name[file_nb]))
            temp_path = path + file_name[file_nb]
            
            # trying to see if there are correct tags
            eyed3.load(temp_path) # creating object
            tag = eyed3.id3.tag.Tag()
            tag.parse(fileobj=temp_path)
            
            if str(type(tag.title)) != "<class 'NoneType'>" :
                temp_title = remove_feat(tag.title)

                if str(type(tag.artist)) == "<class 'NoneType'>" or tag.artist == "None" :
                    temp_artist = "not found"
                else : 
                    temp_artist = tag.artist
                    
                # Displays if at least the title was found
                print("artist : {}".format(temp_artist))
                print("title  : {}".format(temp_title))
                
                if tag.encoded_by == signature :
                    print("file has already been treated with MEP")
                    if question_user("want to modify something ? "):
                        state = 2 # get title and artist 

                    else :
                        new_file_name = file_name[file_nb] 
                        state = 6 # just moving the file in correct directory


                elif question_user("Wrong ?"):
                    print("Let's do it manually then !\n")
                    state = 2 # get title and artist manually  

                else :
                    title  = temp_title
                    artist = temp_artist
                    state = 3 # search info on track (title and artist needed)

            else :
                print ("no title found")
                if All_Auto :
                    state = 20 # Skip track
                else :
                    state = 2 # get title and artist manually

        # ----------------------------------------------------------------------------------------------------------- 2 #
        # STATE 2 : get title and artist manually
        elif state == 2 :
        # getting the user to add title and artist
            artist = input("artist name : ")
            title = input("track name  : ")
            # switch state
            state = 3 # search info on track


        # ----------------------------------------------------------------------------------------------------------- 3 #
        # STATE 3 : Search info on track 
        elif state == 3 : 
            # Search for more info on the track using spotify api 
            search = "track:" + title.replace("'","") + " artist:" + artist
            results = sp.search(q = search, type = "track", limit = 1)   
            items = results['tracks']['items']
            #pprint.pprint(results) #debug 
            
            # Can a result be found
            if len(items) > 0 :
                 
                
                print("")
                print("We have a match !")
                print("")
                Is_Sure = True
                track = items[0]
                track['album']['artwork'] = track['album']['images'][0]['url'] 
                # switch state 
                state = 32 # Getting genre (track object and title needed)

            elif not All_Auto :
                # trying without the artist only if user can verify
                search = "track:" + title.replace("'","")
                results = sp.search(q = search, type = "track", limit = 1)
                
                items = results['tracks']['items']
                if len(items) > 0 :
                    Is_Sure = False
                    print("\nexact track not found \nPotential track :")
                    track = items[0] 
                    track['album']['artwork'] = track['album']['images'][0]['url'] 
                    state = 32 # Getting genre (track object and title needed)
            
                # music not found -> switch state
                elif All_Auto :
                    state = 20 # skip track
                    
                elif question_user("error 808 : music not found... \nDo you want to retry with another spelling ?"):
                    state = 2 # get title and artist manually

                elif question_user("Fill the data manually ?"):
                    state = 31 # manual tagging

                else:
                    print("\n")
                    state = 20 # skip track

        # ----------------------------------------------------------------------------------------------------------- 31 #
        # STATE 31 : manual tagging
        elif state == 31 :

            print("ok let's go !")
            print("title  : " + title)
            print("artist : " + artist)

            # init variables (if no track object was created before hand)
            track = {}
            track['artists'] = [{}]
            track['album']   =  {}

            # user filled data
            track['name']                 = title
            track['artists'][0]['name']    = artist
            webbrowser.open("https://www.google.com/search?q="+track['name']+"+"+track['artists'][0]['name'])

            if question_user("more than one artist ?") :
                track['artists'].append({'name' : input("second artist : ")})
                y = input("third artist (just press enter if there isn't another): ")
                if y != "":
                    track['artists'].append({'name' : y})

            track['album']['name']         =     input("album        : ")
            track['album']['release_date'] =     input("year         : ")
            track['track_number']          = int(input("track number : "))
            track['album']['total_tracks'] = int(input("out of       : "))
            #getting user to pick an artwork
            
            track['album']['artwork']      = input("image url        : ")


            # default stuff : might try to do other searches (with album for exemple) to complete those
            track['disc_number']= None
            track['genre']      = default_genre
            track['album']['copyright'] = ""
            track['album']['label'] = ""
            track['bpm'] = 0 # default

            print("\n Ok let's recap\n")
            state = 4 # user verification

        # ----------------------------------------------------------------------------------------------------------- 32 #
        # STATE 32 : Getting genre + other info auto
        elif state == 32 :
            # genre
            results = sp.artist(track['artists'][0]['id'])
            #pprint.pprint(results)
            if len(results['genres']) > 0:
                track['genre'] = results['genres'][0]
            else :
                track['genre'] = default_genre

            # getting label and copyright
            results = sp.album(track['album']['id'])
            if len(results) > 0 : 
                track['album']['copyright'] = results['copyrights'][0]['text']
                track['album']['label'] = results['label']
            else : 
                # default
                track['album']['copyright'] = ""
                track['album']['label'] = ""  

            # getting BPM
            results = sp.audio_analysis(track['id'])
            if len(results) > 0 :
                track['bpm'] = int(results['track']['tempo'])
            else : 
                track['bpm'] = 0 # default

            state = 4


        # ----------------------------------------------------------------------------------------------------------- 4 #
        # STATE 4 : User verification (track object and title needed)
        elif state == 4 :
            # is there a featured artist ?
            nb_artist = len(track['artists'])   
            if nb_artist == 1 : # no feat
                print("{} by {} :".format(track['name'], track['artists'][0]['name']))

            else :# at least 1 feat
                track['name'] = remove_feat(track['name'])
                # 1 feat process
                if nb_artist == 2 :
                    print("{} by {} featuring {}".format(track['name'],track['artists'][0]['name'],track['artists'][1]['name'])) #display 
                    track['name'] = track['name']+" ("+prefered_feat_acronyme+track['artists'][1]['name']+")" # correct title
                # 2 feat or more process
                else:
                    print("{} by {} featuring {} & {}".format(track['name'],track['artists'][0]['name'],track['artists'][1]['name'],track['artists'][2]['name']))  #display
                    track['name'] = track['name']+" ("+prefered_feat_acronyme+track['artists'][1]['name']+" & "+track['artists'][2]['name']+")"# correct title
            
            # Display info
            print("album        : {}\nGenre        : {}\nrelease date : {}\nTrack number : {} out of {}\n".format(track['album']['name'],track['genre'],track['album']['release_date'],track['track_number'],track['album']['total_tracks']))
            
            # displaying image
            if Open_image_auto :
                webbrowser.open(track['album']['artwork'])

            # switch state
            if Assume_mep_is_right and Is_Sure:
                state = 5 # file update (track object needed)

            elif not question_user("wrong song ?"):
                state = 5 # file update (track object needed)
            
            elif question_user("Do you want to retry with another spelling ?"):
                state = 2 # get title and artist manually

            elif question_user("fill the data manually ?"):
                state = 31
            else : 
                state = 20

    
        # ----------------------------------------------------------------------------------------------------------- 5 #
        # STATE 5 : File update (track object needed)
        elif state == 5 :
    
            #preparing new file name and directory path
            new_file_name = track['name'] + "_" + track['artists'][0]['name'] + file_extension[file_nb]
            new_file_name = correct(new_file_name) #removing annoying characters
            
            temp_path = path + file_name[file_nb]
            new_path = path + new_file_name

            # changing name of the file
            if os.path.exists(temp_path):
                src = os.path.realpath(temp_path)
                os.rename(temp_path,new_path)
            else :
                print("error : file missing from directory")
            
            # downloading file
            image_name = correct(track['album']['name']+"_artwork.jpg")
            image_path = get_file(track['album']['artwork'],image_name,path)
            
            # modifing the tags
            tag = eyed3.id3.tag.Tag()
            if tag.parse(fileobj=new_path) : 
                tag.title          = track['name']
                tag.artist         = track['artists'][0]['name']
                tag.genre          = track['genre']
                tag.album          = track['album']['name']
                tag.album_artist   = track['artists'][0]['name']
                tag.track_num      = (track['track_number'],track['album']['total_tracks'])
                tag.disc_num       = (track['disc_number'],None)
                tag.bpm            = track['bpm']  
                tag.publisher      = track['album']['label']
                tag.copyright      = track['album']['copyright']
                tag.encoded_by     = signature  # Program signature
                tag.recording_date = eyed3.core.Date.parse(track['album']['release_date'])

                # works but no way to get info
                #tag.composer = "compositeur"
                
                # doesn't work
                #tag.lyrics = "Escalope pannée" # doenst work
                # tag.artist_origin = "France" # doesent work

                
                if store_image_in_file :
                    # read image into memory
                    imagedata = open(image_path,"rb").read()

                    # deleting previous artwork if present
                    for i in range(0,len(tag.images)):
                        tag.images.remove(tag.images[i].description)

                    # append image to tags
                    tag.images.set(3,imagedata,"image/jpeg",description=image_name)
                    
                    # removing image 
                    os.remove(image_path) 

                else :
                    # moving image in directory (or deleting if already present)
                    if not os.path.exists(path+folder_name+antislash+image_name) : 
                        shutil.move(image_path,path+folder_name) # place in first folder
                    else :
                        os.remove(image_path)
                        
                tag.save()

            state = 6 # moving file
        
        # ----------------------------------------------------------------------------------------------------------- 6 #
        # STATE 6 : Moving file
        elif state == 6 :
            # moving file 

            new_path = path + new_file_name
            if not os.path.exists(path+folder_name+antislash+new_file_name) : 
                shutil.move(new_path,path+folder_name) # place in first folder 
                treated_file_nb += 1 # file correctly treated
            else :
                print("File already present in folder !!!!")
                
            # changing state
            if remaining_file_nb > 1 :
                file_nb += 1 # file being treated = next in the list
                remaining_file_nb -= 1 # one file done
                state = 1 # get title and artist automatically (new song)
            else :
                state = 10 # Ending program (or restarting)
                
            

        # ----------------------------------------------------------------------------------------------------------- 20 #
        # STATE 20 : Skipping track (only atteingned from full auto mode)
        elif state == 20 :
            if remaining_file_nb > 1 :
                file_nb += 1 # file being treated = next in the list
                remaining_file_nb -= 1 # one file done
                state = 1 # Get title and artist auto
            else :
                state = 10 # End prog

        # ----------------------------------------------------------------------------------------------------------- 10 #
        # STATE 10 : Ending program (or restarting)
        elif state == 10 :

            if config["mode"] == 2 : 
                # reset variables
                time.sleep(1)
                file_extension = [".mp3"]
                file_name = ["music.mp3"]
                file_nb = 1
                remaining_file_nb = 0
                state = 0

            else :
                input("{} files correctly processed out of {}".format(treated_file_nb,file_nb))
                sys.exit("bye")
                
            


if __name__ == '__main__':
    main()                                                      