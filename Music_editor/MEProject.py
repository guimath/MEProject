# -*-coding:utf-8 -*

import os 
import sys # to get the name of the prog file
import time  # for sleep function

# for file modification
from pathlib import Path
import json # to parse config file
import shutil # to move file
import eyed3 # music tag editor 

# for image 
import requests # to get image from the web 
import webbrowser # to directly open image in browser 

# for spotify api 
import spotipy #Spotify API
from spotipy.oauth2 import SpotifyClientCredentials

# for debug only
#import pprint 

# modifiable variables in config file
'''
folder_name             : Name of the folder where all the music will be droped
second_folder_name      : Name of the folder where the music will be droped if the program is unsure
prefered_feat_acronyme  : Used when a track has multiple artist. The title will look like : *title_of_track* (*prefered_feat_acronyme* *other artist*)
default_genre           : If MEP doesn't find a genre this is what will be written in the file
Open_image_auto         : True : MEP will automatically open the album image in your most recent browser window | False : No image is opened
Assume_mep_is_right     : True : once MEP has identified a track it will directly change the tags | False : MEP will fist ask you if the track is correct
All_Auto                : True : will try to run fully automaticly. If a file requires human input, it simply won't be treated
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
# returns corrected title
def remove_feat(title) :
    if "(Ft" in title or "(ft" in title or "(Feat" in title or "(feat" in title:
        # complicated in case there is anothere paranthesis in the title
        b = []
        b = title.split("(")
        title = b[0]
        for i in range (1, len(b)-1):
            title = title + "(" + b[i]
    return title.strip() 

# Downloading picture from specified url as specified filename to specified path
# returns the complete path of the new downloaded file if worked correctly, else returns 0
def get_file(file_url,filename,path) :

    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(file_url, stream = True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
    
        # Open a local file with wb ( write binary ) permission.
        with open(filename,'wb') as f: #not working from direct execution
            shutil.copyfileobj(r.raw, f)
        
        #move to wanted folder
        shutil.move(filename,path+filename)     
        return path+filename     
    else:
        return 0

def main():
    global treated_file_nb, remaining_file_nb, file_nb, All_Auto, state

    # Variable initialization
    Is_Sure = True
    accepted_extensions = [".mp3"]
    file_extension = [".mp3"]
    file_name = ["music.mp3"]
    title = ""
    artist = ""
    #track ?

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
    second_folder_name     = config["second_folder_name"]
    third_folder_name      = config["third_folder_name"]

    if config["mode"] == 1 : # full auto
        All_Auto = True
        Assume_mep_is_right = True
        Open_image_auto = False
    elif config["mode"] == 2 : # semi auto
        All_Auto = False
        Assume_mep_is_right = True
        Open_image_auto = False
    else :
        config["mode"] = 3 # discovery
        All_Auto = False
        Assume_mep_is_right = False
        Open_image_auto = True



    # Spotify api autorisation 
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id = config["client_id"],
                                                           client_secret = config["client_secret"]))
    print("\n")
    while True :

        # ------------------------------------------------------ #
        # STATE 0 : Scanning folder
        if state == 0 : 
            # scanning folder
            music_file_found = False
            folder1_found    = False
            folder2_found    = False
            folder3_found    = False
            wrong_format     = False
            for temp_file_name in os.listdir(path): 
                temp, temp_file_extension = os.path.splitext(temp_file_name)
                
                if temp_file_extension in accepted_extensions :
                    file_name.append(temp_file_name)  
                    file_extension.append(temp_file_extension)
                    remaining_file_nb += 1
                    music_file_found = True

                elif temp_file_name == folder_name :
                    folder1_found = True

                elif temp_file_name == second_folder_name :
                    folder2_found = True
                
                elif temp_file_name == third_folder_name :
                    folder3_found = True

                elif (temp_file_name != prog_name) and (temp_file_extension != "") and (temp_file_extension != ".json") :
                    wrong_format=True
                    wrong_file_name=temp_file_name
            
            # if there isn't a folder already, creates it
            if not folder1_found :
                os.makedirs(path+folder_name)
            if not folder2_found :
                os.makedirs(path+second_folder_name)
            if not folder3_found :
                os.makedirs(path+third_folder_name)

            # File found ?
            if music_file_found :
                state = 1 # get title and artist automatically
            elif wrong_format :
                print("the file '{}' is not in supported format" .format(wrong_file_name))
                print("the supported formats are : ")
                for i in range(0,len(accepted_extensions)):
                    print(accepted_extensions[i])
                state = 10
            else : # no file other than program and directory was found
                state = 10

        # ------------------------------------------------------ #
        # STATE 1 : get title and artist automatically
        elif state == 1 : 
            print("file {} out of {} : '{}'".format(file_nb,remaining_file_nb+treated_file_nb,file_name[file_nb]))
            temp_path = path + file_name[file_nb]
            
            # trying to see if there are correct tags
            audiofile = eyed3.load(temp_path)
            if type(audiofile.tag.title)!='NoneType' :
                temp_title = remove_feat(audiofile.tag.title)
                test=str(type(audiofile.tag.artist))
                if test == "<class 'NoneType'>" or audiofile.tag.artist == "None" :
                    temp_artist = "not found"
                else : 
                    temp_artist = audiofile.tag.artist
                    
                # Displays if at least the title was found
                print("artist : {}".format(temp_artist))
                print("title : {}".format(temp_title))
                
                if question_user("Wrong ?"):
                    print("Let's do it manually then !\n")
                    state = 2 # get title and artist manually  

                else :
                    title  = temp_title
                    artist = temp_artist
                    state = 3 # search info on track (title and artist needed)

            else :
                print ("no title found")
                if All_Auto :
                    state = 20
                else :
                    state = 2 # get title and artist manually

        # ------------------------------------------------------ #
        # STATE 2 : get title and artist manually
        elif state == 2 :
        # getting the user to add title and artist
            artist = input("artist name : ")
            title = input("track name  : ")
            # switch state
            state = 3 # search info on track


        # ------------------------------------------------------ #
        # STATE 3 : Search info on track 
        elif state == 3 : 
            # Search for more info on the track using spotify api 
            search = "track:" + title.replace("'","") + " artist:" + artist
            results = sp.search(q = search, type = "track", limit = 1)   
            items = results['tracks']['items']
            #pprint.pprint(results) #debug 
            
            # Can a result be found
            if len(items) > 0 :
                print("\nWe have a match !\n")
                Is_Sure = True
                track = items[0]
                # switch state 
                state = 4 # user verification (track object and title needed)
            elif not All_Auto :
                # trying without the artist only if user can verify
                search = "track:" + title.replace("'","")
                results = sp.search(q = search, type = "track", limit = 1)

                items = results['tracks']['items']
                if len(items) > 0 :
                    Is_Sure = False
                    print("\nexact track not found\n\nPotential track :")
                    track = items[0] 
                    # switch state
                    state = 4 # user verification (track object and title needed)
            
                # music not found -> switch state
                elif All_Auto :
                    state = 20
                    
                elif question_user("error 808 : music not found... \nDo you want to retry with another spelling ?"):
                    state = 2 # get title and artist manually

                elif question_user("Fill the data manually ?"):
                    print("function under developpement... sorry")
                    state = 20
                    # TEMPORARY

                else:
                    state = 20

        # ------------------------------------------------------ #
        # STATE 4 : User verification (track object and title needed)
        elif state == 4 :

            # getting genre 
            results = sp.artist(track['artists'][0]['id'])   
            if len(results['genres']) > 0:
                track['genres'] = results['genres']
            else :
                track['genres'] = default_genre
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
            print("album        : {}\nGenre        : {}\nrelease date : {}\nTrack number : {} out of {}\n".format(track['album']['name'],track['genres'][0],track['album']['release_date'],track['track_number'],track['album']['total_tracks']))
            
            # displaying image
            if Open_image_auto :
                webbrowser.open(track['album']['images'][0]['url'])

            # switch state
            if Assume_mep_is_right and Is_Sure:
                state = 5 # file update (track object needed)

            elif not question_user("wrong song ?"):
                state = 5 # file update (track object needed)
            
            elif question_user("Do you want to retry with another spelling ?"):
                state = 2 # get title and artist manually

            else : 
                state = 20

    
        # ------------------------------------------------------ #
        # STATE 5 : File update (track object needed)
        elif state == 5 :
    
            #preparing new file name and directory path
            new_file_name = track['name'] + "_" + track['artists'][0]['name']
            new_file_name = new_file_name.replace('/','') # removing / . , and "  frome name
            new_file_name = new_file_name.replace('.','') 
            new_file_name = new_file_name.replace(',','') 
            new_file_name = new_file_name.replace('"','') 
            new_file_name +=  file_extension[file_nb]

            temp_path = path + file_name[file_nb]
            new_path = path + new_file_name

            # changing name of the file
            if os.path.exists(temp_path):
                src = os.path.realpath(temp_path)
                os.rename(temp_path,new_path)
            else :
                print("error : file missing from directory")
            
            # downloading file
            image_name = "album_artwork.jpg"
            image_path = get_file(track['album']['images'][0]['url'],image_name,path)
            
            # modifing the tags
            audiofile = eyed3.load(new_path)
            audiofile.tag.title  = track['name']
            audiofile.tag.artist = track['artists'][0]['name']
            audiofile.tag.genre  = track['genres'][0]
            audiofile.tag.album  = track['album']['name']
            audiofile.tag.album_artist = track['artists'][0]['name']
            audiofile.tag.track_num    = (track['track_number'],track['album']['total_tracks'])
            audiofile.tag.release_date = track['album']['release_date'][:4] # only storing the year

            # read image into memory
            imagedata = open(image_path,"rb").read()
            # deleting previous artwork if present
            for i in range(0,len(audiofile.tag.images)):
                audiofile.tag.images.remove(audiofile.tag.images[0].description)

            # append image to tags
            audiofile.tag.images.set(3,imagedata,"image/jpeg",u"album_artwork")
            
            if os.path.exists(new_path) :
                audiofile.tag.save()
            

            # moving file and deleting temporary image
            if Is_Sure and not os.path.exists(path+folder_name+antislash+new_file_name) : 
                shutil.move(new_path,path+folder_name) # place in first folder
            elif not (Is_Sure or os.path.exists(path+second_folder_name+antislash+new_file_name)) :    
                shutil.move(new_path,path+second_folder_name) # place in second folder
            else :
                print("File already present in folder !!!!")
            os.remove(image_path)

            # input("all done !")
            # switch state
            treated_file_nb += 1
            remaining_file_nb -= 1 # one file done
            if (remaining_file_nb>0) : 
                file_nb += 1 # file being treated = next in the list
                state = 1 # get title and artist automatically
            else :
                state = 10 # Ending program (or restarting)# Ending program (or restarting)

        # ------------------------------------------------------ #
        # STATE 20 : Skipping track
        elif state == 20 :

            if not All_Auto :
                # file needs to be moved to third folder
                temp_path = path + file_name[file_nb]
                if not os.path.exists(path+third_folder_name+antislash+file_name[file_nb]) :    
                    shutil.move(temp_path,path+third_folder_name) # place in third folder

            if remaining_file_nb > 1 :
                file_nb += 1 # file being treated = next in the list
                remaining_file_nb -= 1 # one file done
                state = 1 
            else :
                state = 10

        # ------------------------------------------------------ #
        # STATE 10 : Ending program (or restarting)
        elif state == 10 :

            if config["mode"] == 2 : 
                # reset variables
                time.sleep(1)
                file_extension = [".mp3"]
                file_name = ["music.mp3"]
                treated_file_nb = 0
                file_nb = 1
                remaining_file_nb = 0
                state = 0

            else :
                print("{} files correctly processed out of {}".format(treated_file_nb,file_nb))
                sys.exit("bye")
                
            


if __name__ == '__main__':
    main()                                                      