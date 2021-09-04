#!/usr/bin/env python
# coding: utf-8 

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in corect dir

import time 
from Test import * 

from mep import Utilities


def main() :
    lst =["Bing Crosby",
        "Elton John",
        "Mungo Jerry",
        "Bill Haley & His Comets",
        "Domenico Modugno",
        "Whitney Houston",
        "Elvis Presley",
        "USA for Africa",
        "The Ink Spots",
        "Céline Dion",
        "The Beatles",
        "John Travolta et Olivia Newton",
        "Bryan Adams"]
    res = ""

    headp("Testing Utilities")
    for a in lst :
        for b in lst :
            if  Utilities.similar(a,b) :
                res+=(f'{a} = {b} ')
    assert(res=="Bing Crosby = Bing Crosby Elton John = Elton John Mungo Jerry = Mungo Jerry Bill Haley & His Comets = Bill Haley & His Comets Domenico Modugno = Domenico Modugno Whitney Houston = Whitney Houston Elvis Presley = Elvis Presley USA for Africa = USA for Africa The Ink Spots = The Ink Spots Céline Dion = Céline Dion The Beatles = The Beatles John Travolta et Olivia Newton = John Travolta et Olivia Newton Bryan Adams = Bryan Adams ")
    greenp("similar working")
    
    title = "LOVE. FEAT. Zacari"
    assert(Utilities.remove_feat(title)=="LOVE.")
    greenp("remove_feat working")

    artist = "The Strokes"  
    assert(Utilities.remove_the(artist)=="Strokes")
    greenp("remove_the working")

    title = "LOVE."
    assert(Utilities.clean_string(title)=="LOVE")
    greenp("clean_string working")



    interface = Interface()

    assert(Utilities.create_config())
    greenp("create_config working")

    config={'feat_acronym': 'feat.', 'default_genre': 'Other', 'folder_name': 'music', 'get_label': True, 'get_bpm': True, 'get_lyrics': True, 'store_image_in_file': True}
    start = time.time()
    assert(Utilities.update_config(config, interface))
    end = time.time()
    greenp(f"update_config working (took {end-start}s)")

    start = time.time()
    assert(Utilities.read_config(interface)==config)
    end = time.time()
    greenp(f"read_config working (took {end-start}s)")

    assert(Utilities.rm_file('config.json'))
    greenp("rm_file working")

class Interface :
    def __init__(self):
        pass
    
    def warn(self, msg):
        print(msg)
    
    def ask(self, msg):
        print("ask : "+msg) 
        return True
    

if __name__ == '__main__':
    main()
