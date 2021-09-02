#!/usr/bin/env python
# coding: utf-8 

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in corect dir

import time 
from Test import * 

from mep import Info_search

def main() :

    artist= "Radiohead" 
    title= "Nude"
    info_search = Info_search.Info_search({"none":None})

    headp("Testing info search")
    start = time.time()
    assert(info_search._spotify_basic_info("Radiohead","Karma Police"))
    end = time.time()
    greenp(f'spotify_basic_info working (took {end-start}s)')

    headp("Testing lyrics")
    service = ["Musixmatch","Genius", "AZLyrics", "LyricsOVH"]
    func = [info_search._musixmatch, info_search._genius, info_search._az_lyrics, info_search._lyrics_ovh]
    for i in range(len(service)) :
        try :
            start = time.time()
            assert(func[i](artist,title))
            end = time.time()
            greenp(f'{service[i]} working (took {end-start}s)')
        except :
            redp(f'{service[i]} not working')



if __name__ == '__main__':
    main()
