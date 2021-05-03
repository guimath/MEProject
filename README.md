# MEProject


## Description
This project is a program allowing you to modify music tags (album, genre, etc...) semi automatically, using the Spotify api.  
It will search the music using the spotify api and fill the tags of your files accordingly.  
It is designed to make downloading music and reorganizing your music library easier. 

If you just want to use it, you can get the .exe/.app  version that won't require any software install (you can skip developers paragraph)

## User manual
**How to use the config file :** (config.json)
This file allows you to change what the program will do. You can modify it by simply double clicking on it a modifying a the value of any given key. The keys are :  
* `folder_name`        : a string that will be used as the name of the folder where all music will be moved once processed. Doesn't need to already exist (the program will create it if needed)  
* `prefered_feat_sign` : a String that will be used as the featuring sign on tracks with multiple artists. Title of such songs will be _title (preferred_feat_sign second_artist)_  
* `default_genre`      : a String that will be used as the default genre if no genre has been found.  
* `get_label`          : a boolean (true or false) to add label to tags  
* `get_bpm`            : a boolean (true or false) to add bpm to tags  
* `get_lyrics`         : a boolean (true or false) to add Lyrics to tags  
* `store_image_in_file`: a boolean (true or false) to include the artwork directly in the file or to add the image separately.
     

**How to use depending on the mode :**  
* `full auto` : To standardize a big music library     
**input needed :** none, but that means the files need to have correct title and artist tags. if the info found is unsure, the file will be skipped    
**Speed :** It is relatively quick but adding lyrics will make it run slower. Because this mode is fully automatic, you can simply run it in the background

* `Semi auto` To add new files w/ or w/o correct tags  
**input needed :** you will need to check wether the info found in the tags is correct or you will need to _manually_ add title and artist the program should then process the file automatically    
**Speed :** should still be a lot quicker than manually changing tags  
**Specifics :** there is also a manual tagging option if spotify doesn't  have the music

* `downloads` To download music from youtube url
**input needed :** first you need to choose wether you want to download a whole playlist (if you want to dl an album for example) and then paste the url of the song to download  
**Speed :** the dl (while this method is a lot quicker than online mp3 converters) is a bit slow but once again you can let the program run in the background once you have entered the url. 

* `discovery` To better understand how the program works  
**input needed :** this mode is heavily reliant on user verification so you will have to input a lot of info. This allows you to control everything and test the program before using it on a bigger scale.  
**Speed :** this mode is not designed to be quick, it is simply recommended that you start with this mode if you're weary of my coding skills. You should not be using this mode for more than a few files.

**output :** it will put all the files correctly processed in the music folder (organized as ``artist/album/track_nb-title.mp3``) and leave the untreated files where they were


## Developers
**Required :** To work properly, python 3 is needed. You'll also need a few packages : 
* `eyed3` : mp3 tag editor
* `python-slugify` : to remove problematic characters
* `spotipy` : spotify api to search infos
* `bs4` : to scrap website for infos
* `webbrowser` : to open links in your browser
* `youtube-dl` : to download music from youtube

To add those simply launch your console and type "pip install _nameOfPackage_"  

The youtube-dl package also requires ffprobe or ffmpeg. Installation varies depending on the os.