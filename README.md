# MEProject


**Description :** This project is a program allowing you to modify music tags (album, genre, etc...) semi automatically, using the Spotify api.  
It will search the music using the spotify api and fill the tags of your files accordingly.  
It is designed to make downloading music and reorganising your music library easier. 

If you just want to use it, you can get the .exe/.app  version that won't require any software install (you can skip required paragraph)

**Required :** To work properly, python V3 is needed. You'll also need a few packages : 
* `eyed3` : music tag editor
* `spotipy` : spotify api
* `webbrowser` : open image in browser  
To add those simply launch your console (cmd in windows) and type "pip install _nameOfPackage_"  

**How to use depanding on the mode :**  
* `full auto` : To standardise a big music library     
**input needed :** doesn't need any input from in this mode, but that means the files need to have correct title and artist tags (at least title)    
**Speed :** because it doesn't need any human interactions, it should be really quick. 

* `Semi auto` To add new files w/ or w/o correct tags  
**input needed :** you will need to check wether the info found in the tags is correct or you will need to _manually_ add title and artist the program should then process the file automatically    
**Speed :** should still be a lot quicker than manually changing tags 
**Specifics :** there is also a manual tagging option if spotify doesn't  have the music

* `discovery` To better understand how the program works  
**input needed :** this mode is heavly reliant on user verification so you will have to input a lot of info  
**Speed :** this mode is not designed to be quick, if you try to use it to update a lot of files it will get annoying 

**output :** it will put all the files correctly processed in the first folder, the unsure processed files in the second, and leave the files untreated where they were


