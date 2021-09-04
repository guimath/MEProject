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

    yt_url = "https://www.youtube.com/watch?v=ewOPQZZn4SY&list=OLAK5uy_mIPgAqJi0-TwDIDkX8x0jvBb9TqXTEdVw"
    expected_res = ([{'title': 'The Strokes - The Adults Are Talking (Official Video)', 'uploader': 'The Strokes', 'duration': '4min 48s', 'id': 0}, {'title': 'The Strokes - Selfless (Audio)', 'uploader': 'The Strokes', 'duration': '3min 44s', 'id': 1}, {'title': 'The Strokes - Brooklyn Bridge To Chorus (Audio)', 'uploader': 'The Strokes', 'duration': '3min 58s', 'id': 2}, {'title': 'The Strokes - Bad Decisions (Official Video)', 'uploader': 'The Strokes', 'duration': '4min 55s', 'id': 3}, {'title': 'The Strokes - Eternal Summer (Audio)', 'uploader': 'The Strokes', 'duration': '6min 17s', 'id': 4}, {'title': 'The Strokes - At The Door (Official Video)', 'uploader': 'The Strokes', 'duration': '5min 54s', 'id': 5}, {'title': 'The Strokes - Why Are Sundays So Depressing (Audio)', 'uploader': 'The Strokes', 'duration': '4min 38s', 'id': 6}, {'title': 'The Strokes - Not The Same Anymore (Audio)', 'uploader': 'The Strokes', 'duration': '5min 39s', 'id': 7}, {'title': 'The Strokes - Ode To The Mets (Official Video)', 'uploader': 'The Strokes', 'duration': '6min 49s', 'id': 8}], 'The New Abnormal')   
    start = time.time()
    assert(expected_res==Downloads.check_out_playlist(yt_url))
    end = time.time()
    greenp(f'check_out_playlist working (took {end-start}s)')

if __name__ == '__main__':
    main()
