# -*-coding:utf-8 -*
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in corect dir

import time 
from Test import * 

import shutil
from mep import Tagger

def main() :
    tagger = Tagger.Tagger(params={"store_image_in_file":True, "folder_name":""}, ADD_SIGN= True, SIGN="testing signature")

    track = {
    'name': 'Karma Police',
    'track_number': 6,
    'disc_number': 1,

    'genre': 'Rock',
    'bpm': 98,
    'lyrics': {'text':'Karma Police lyrics'},

    'album' : {
        'name': 'OK Computer',
        'release_date': '1997-05-28',
        'total_tracks': 12,

        'label':'Radiohead Label',
        'copyright':'Radiohead copyright'},
   
    'artists': [{
        'name': "Radiohead"}]
    }
 
    params = [{'format' : 'mp3', 'file_name' : 'z_tags_tester.mp3'},
              {'format' : 'flac', 'file_name' : 'z_tags_tester.flac'}]
    

    headp("Testing Tagger")
    for param in params :
        # read_tags
        try :
            start = time.time()
            assert(tagger.read_tags(file_name=param["file_name"])!= (None,None,None,None))
            end = time.time()
            greenp(f'read_tags - {param["format"]} - working (took {end-start}s)')
        except :
            redp(f'read_tags - {param["format"]} - not working')

        #update_tags
        shutil.copy("z_tags_tester.jpg","z_tags_tester1.jpg") #makes copy 
        try :
            start = time.time()
            assert(0 <= tagger.update_tags(file_name=param["file_name"], image_name="z_tags_tester1.jpg", track=track))
            end = time.time()
            greenp(f'update_tags - {param["format"]} - working (took {end-start}s)')
        except :
            redp(f'update_tags - {param["format"]} - not working')



if __name__ == '__main__':
    main()

