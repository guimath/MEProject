# for file modification
import os
import eyed3  # to parse mp3 files
import json   # to parse config file
import shutil  # to move file
import stat   # to change read/write file status
import os 

class Tagger :
    def __init__(self, debug):
        self.debug = debug
        eyed3.log.setLevel("ERROR")  # hides errors from eyed3 package     

    def _mp3(self, filename, image_path, track) :
        pass #TODO


    def update_file(self, filename, image_path, track):
        tmp, extension = os.path.splitext(filename)
        if extension == ".mp3" :
            return self._mp3(filename, image_path, track)
        else :
            return 0
