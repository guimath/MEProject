# Music Editor Project


## Description
This project is a program allowing you to modify music tags (album, genre, etc...) semi automatically, using the Spotify api.  
It will search the music using the spotify api and fill the tags of your files accordingly.  
It is designed to make downloading music and reorganizing your music library easier. 

If you just want to use it, you can get the .exe/.app  version that won't require any software install (you can skip developers paragraph)

## User manual

### What files are needed ?

You need to have in the same folder :
* the executable (1MEP.exe/1MEP.app)
* the config file (config.json)
* the ffmpeg folder (contains a program used during download)

And that's it ! 

### What are the different modes ? 
* The first one is a way to standardize a big music library, or a way to go quickly if you have a lot of files to process. It will scan the folder of the program, search a match for every file automatically and then let you verify the infos. if you see an incorrect match, you can just check the `retry` checkbox. Once you have looked through all the files you just click the `validate` button, all the unchecked files will be processed and it will go to the second mode to fix the issues with the rest of the files


* The second mode is slightly slower but gives more control. Before each search you get to check/modify the title and artist that will be used for the search. Then once you have picked those, you will get a detailed display of the information found. If it's not the correct result, you can click :
    * `next match/ previous match` to cycle through all the results found 
    * `retry` if you made a mistake on the title or artist (removing weird characters helps sometimes) 
    * `skip` if you really find nothing (I will add a way to manually fill the tags at some point)
    * `ok` if its all good :)

    The file will then be processed/skipped and you do the same for the next file.


* The third mode allows you to download music from Youtube. You simply fill the URL you want to download (you can also download a whole playlist like an album by checking the `Whole playlist ?` checkbox). And then click the `download` button. The download will start. It is relatively unreliable and can be a bit slow sometimes but it usually works. Once the download is complete you will get back to one of the two first modes wether you download a single file or not.


### How is my music stored ? 
The program will put all the files correctly processed in the music folder (organized as ``artist/album/track_nb-title_of_track.mp3``) and leave the untreated files where they were

### Settings 
The settings are stored in the config.json file. The allow you to change what the program will do. You can modify them by clicking on `settings` in the start window 

It allows you to modify :
* wether or not you want to search for :

    * the label/ copyright
    * the bpm
    * the lyrics

    if you don't care about any of those infos you should deselect them as they tend to make the search of infos slightly longer


* `wether or not you want the artwork to be included in the music files`
    
    It's usually better to not included it in every files as it will result in a larger size of files but might be easier depending on what music player you use.

* `the name of the folder where the music will go` 

    it can be any name you like (for example "my music") or a absolute path to a folder (for example "/home/guilhem/Musique")

* `Your preferred featuring acronym`      

    it will be included in the titles of songs with multiple artists like that : 
    
    ___TITLE (FEAT_ACRONYM OTHER_ARTIST)___
* `The defaut genre`     

    If no genre has been found this is what will show.

     
## Developers
**Required :** To work properly, python 3 is needed. You'll also need a few packages : 
* `eyed3` : mp3 tag editor
* `python-slugify` : to remove problematic characters
* `spotipy` : spotify api to search infos
* `bs4` : to scrap website for infos
* `youtube-dl` : to download music from youtube

To install those, you can do for each package "pip install _nameOfPackage_"  or you can run "pip install -r requirements.txt"

The youtube-dl package also requires ffprobe and ffmpeg. Installation varies depending on the os. You can also just add a folder named ffmpeg with the executable for ffprobe and ffmpeg. 