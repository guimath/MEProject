# -*-coding:utf-8 -*
import pprint # for debug only
import os
from pathlib import Path
import requests # to get image from the web 
import shutil # to move file
import webbrowser # to directly open image in browser
import eyed3 # music tag editor 
import sys # to get the name of the prog file
import spotipy #Spotify API
from spotipy.oauth2 import SpotifyClientCredentials
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fb69ab85a5c749e08713458e85754515",
                                                           client_secret="ebe33b7ed0cd495a8e91bc4032e9edf2")) #private keys : do not share

# modifiable variables
folder_name = "processed music"  # Name of the folder where all the music will be droped
prefered_feat_acronyme= "feat. " # Used when a track has multiple artist. The title will look like : *title_of_track* (*prefered_feat_acronyme* *other artist*)
default_genre = "Other"          # If MEP doesn't find a genre this is what will be written in the file
Open_image_auto     = False      # True : MEP will automatically open the album image in your most recent browser window | False : No image is opened
Assume_mep_is_right = True       # True : once MEP has identified a track it will directly change the tags | False : MEP will fist ask you if the track is correct
All_Auto            = True       # True : will try to run fully automaticly. If a file requires human input, it simply won't be treated


#global variables
accepted_extensions = [".mp3", ".flac"]
file_name = ["music.mp3"]
file_extension = [".mp3"]
treated_file_nb = 0
remaining_file_nb = 0
file_nb = 1
#getting automatic path (in the directory of the program) "
path = os.path.dirname(os.path.realpath(__file__))
temp = "\ "
temp=temp[:1]
path = path+temp

# Stoping program
def end_prog():
    sys.exit("bye")

# converting user answer (y or n) into true or false
# Special answer : p will end program  (used for debug) 
def question_user(message) :
    if All_Auto :
        return False

    ans = input(message+" (y for yes n for no) : ")
    if ans== 'y' or ans == 'Y' :
        return True
    elif ans == 'p' :
        end_prog()
    else :
        return False

# Used if file can't be treated 
# wwill start process of the next file if available or end prog
def skip_track():
    global file_nb,treated_file_nb,remaining_file_nb
    if remaining_file_nb > 1 :
        file_nb += 1 # file being treated = next in the list
        treated_file_nb += 1
        remaining_file_nb -= 1 # one file done
        get_title_artist_auto()
    else :
        end_prog()

# once a file has been treated 
'''
def update_count(result):
    if result == 0 : # track not processed 
    elif result == 1 : # track uncertain
    else : #track correctly processed
'''



# Removes the "'feat." type from the title
# returns corrected title
def remove_feat(title) :
    if "(Ft" in title or "(ft" in title or "(Feat" in title or "(feat" in title:
        title, temp = title.split("(")
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

def get_title_artist_auto():
    global path, file_nb, remaining_file_nb, treated_file_nb

    print("file {} out of {} : '{}'".format(file_nb,remaining_file_nb+treated_file_nb,file_name[file_nb]))
    temp_path = path+file_name[file_nb]
    #trying to see if there are correct tags
    audiofile = eyed3.load(temp_path)
    if type(audiofile.tag.title)!='NoneType' :
        temp_title=remove_feat(audiofile.tag.title)
        if type(audiofile.tag.artist)!='NoneType' and audiofile.tag.artist != "None" :
            temp_artist = audiofile.tag.artist
        else : 
            temp_artist = "not found"

        print("artist : {}".format(temp_artist))
        print("title : {}".format(temp_title))
          
        if question_user("Wrong ?"):
            print("Let's do it manually then !\n")
        else :
            # switch state
            search_infos(temp_title,audiofile.tag.artist)
    else :
        print ("no title found")
    
    # switch state  
    if All_Auto :
        skip_track()
    else :
        get_title_artist_manu()
    

def get_title_artist_manu():
    # getting the user to add title and artist
    artist = input("artist name : ")
    title = input("track name  : ")
    # switch state
    search_infos(title,artist)

def search_infos(title,artist):
    # Search for more info on the track
    search = "track:"+title+" artist:"+artist
    results = sp.search(q=search,type="track",limit=1)   
    items = results['tracks']['items']
    #pprint.pprint(results) #debug 
    
    # Can a result be found
    if len(items)>0 :
        print("\nWe have a match !\n")
        track = items[0]
        # switch state 
        user_verification(track, title)
    else :
        # trying without the artist
        search = "track:"+title
        results = sp.search(q=search,type="track",limit=1)
        #pprint.pprint(results) #debug 
        items = results['tracks']['items']
        if len(items)>0 :
            print("\nexact track not found\n\nPotential track :")
            track = items[0] 
            # switch state
            user_verification(track, title)
       
        # music not found -> switch state
        if All_Auto :
            skip_track()
        elif question_user("error 808 : music not found... \nDo you want to retry with another spelling ?"):
            get_title_artist_manu()
        elif question_user("Fill the data manually ?"):
            print("function under developpement... sorry")
        else:
            end_prog() 
        
def user_verification(track, title):
    global default_genre
    # getting genre 
    results = sp.artist(track['artists'][0]['id'])   
    if len(results['genres'])>0:
        track['genres'] = results['genres']
    else :
        track['genres'] = [default_genre]

    # is there a featured artist ?
    nb_artist = len(track['artists'])   
    if nb_artist == 1 : # no feat
        print("{} by {} :".format(track['name'],track['artists'][0]['name']))

    else :# at least 1 feat
        track['name'] = remove_feat(track['name'])
        # 1 feat process
        if nb_artist == 2 :
            print("{} by {} featuring {}".format(track['name'],track['artists'][0]['name'],track['artists'][1]['name'])) #display 
            track['name'] = track['name']+" ("+prefered_feat_acronyme+track['artists'][1]['name']+")" # correct title
        # 2 feat or more process
        else:
            print("{} by {} featuring {} & {}".format(track['name'],track['artists'][0]['name'],track['artists'][1]['name'],track['artists'][2]['name']))  #display
            track['name'] = track['name']+" ("+prefered_feat_acronyme+track['artists'][1]['name']+" & "+['artists'][2]['name']+")"# correct title
    
    print("album        : {}\nGenre        : {}\nrelease date : {}\nTrack number : {} out of {}\n".format(track['album']['name'],track['genres'][0],track['album']['release_date'],track['track_number'],track['album']['total_tracks']))
    
    # displaying image
    if Open_image_auto and not All_Auto :
        webbrowser.open(track['album']['images'][0]['url'])

    # switch state
    if Assume_mep_is_right or All_Auto:
        file_update(track)
    elif not question_user("wrong song ?"):
        file_update(track)
    elif question_user("Do you want to retry with another spelling ?"):
        get_title_artist_manu()
    else : 
        end_prog()    

def file_update(track) :
    global file_name, file_extension, path, file_nb, remaining_file_nb, treated_file_nb
   
    #preparing new file name and directory path
    new_file_name = track['name'] + "_" + track['artists'][0]['name'] + file_extension[file_nb]
    temp_path = path + file_name[file_nb]
    new_path = path + new_file_name

    # changing name of the file
    if os.path.exists(temp_path):
        src = os.path.realpath(temp_path)
        os.rename(temp_path,new_path)
        print("new file name : {}".format(new_file_name))
        print("file {} processed ! {} remaining\n".format(file_nb,remaining_file_nb-1))
    else :
        print("error : file missing from directory")
    
    # downloading file
    image_name = "album_artwork.jpg"
    image_path = get_file(track['album']['images'][0]['url'],image_name,path)
    
    # modifing the tags
    audiofile = eyed3.load(new_path)
    audiofile.tag.title  = track['name']
    audiofile.tag.artist = track['artists'][0]['name']
    audiofile.tag.album  = track['album']['name']
    audiofile.tag.album_artist = track['artists'][0]['name']
    audiofile.tag.track_num = (track['track_number'],track['album']['total_tracks'])
    audiofile.tag.release_date = track['album']['release_date'][:4] # only storing the year
    audiofile.tag.genre = track['genres'][0]

    # read image into memory
    imagedata = open(image_path,"rb").read()
    # deleting previous artwork if present
    for i in range(0,len(audiofile.tag.images)):
        audiofile.tag.images.remove(audiofile.tag.images[0].description)

    # append image to tags
    audiofile.tag.images.set(3,imagedata,"image/jpeg",u"album_artwork")
    audiofile.tag.save()

    # moving file and deleting temporary image
    shutil.move(new_path,path+folder_name)
    os.remove(image_path)

    # input("all done !")
    # switch state
    if (remaining_file_nb>1) : 
        file_nb += 1 # file being treated = next in the list
        treated_file_nb += 1
        remaining_file_nb -= 1 # one file done
        get_title_artist_auto()
    else :
        end_prog()


def main():
    global file_name, file_extension, path, folder_name, file_nb, remaining_file_nb
    music_file_found = False
    folder_found = False
    wrong_format= False

    # getting the name of the prog
    prog_name = os.path.abspath(sys.argv[0])
    prog_name = prog_name[len(path):] #removing path from the file name
   
    print("\n")
    # Scaninng folder 
    for temp_file_name in os.listdir(path): 
        temp, temp_file_extension = os.path.splitext(temp_file_name)
        if temp_file_extension in accepted_extensions :
            file_name.append(temp_file_name)  
            file_extension.append(temp_file_extension)
            remaining_file_nb+=1
            music_file_found = True
        elif temp_file_name== folder_name :
            folder_found=True
        elif (temp_file_name != prog_name) and (temp_file_extension != "") :
            wrong_format=True
            wrong_file_name=temp_file_name

    # if there isn't a folder already, creates it
    if folder_found == False:
        os.makedirs(path+folder_name)

    # File found ?
    if music_file_found :
        get_title_artist_auto()
    elif wrong_format :
        print("the file '{}' is not in supported format" .format(wrong_file_name))
        print("the supported formats are : ")
        for i in range(0,len(accepted_extensions)):
            print(accepted_extensions[i])
    else : # no file other than program and directory was found
        print("error : no music file found")





if __name__ == '__main__':
    main()                                                      