#!/usr/bin/env python
# coding: utf-8 

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in corect dir

import time 
from Test import * 

from mep import Downloads

class Interface :
    def __init__(self):
        pass
    
    def warn(self, msg):
        print(msg)
    
    def debug(self, msg):
        pass 
    def warning(self, msg):
        pass
    def error(self,msg):
        print(f'Error during yt-dl : {msg}')

def dl_hook(d) : 
    pass

def main() :
    interface = Interface()
    headp("Testing Downloads")
    img_url = "https://i.scdn.co/image/ab67616d0000b273c8b444df094279e70d0ed856"
    name = "test_image.jpg"
    start = time.time()
    assert(name == Downloads.dl_image(img_url,name, interface))
    end = time.time()
    greenp(f'dl_image working (took {end-start}s)')
    os.remove(name)

    yt_url = "https://www.youtube.com/watch?v=83m261lAlrs"
    name = "yt-DL_Don't woof.mp3"
    start = time.time()
    assert(Downloads.dl_music(yt_url,True, interface, [dl_hook]))
    end = time.time()
    greenp(f'dl_music working (took {end-start}s)')
    os.remove(name)

if __name__ == '__main__':
    main()
