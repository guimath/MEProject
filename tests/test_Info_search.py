# -*-coding:utf-8 -*
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in corect dir

import time 

from mep import Info_search


def main() :
    artist= "Radiohead" 
    title= "Nude"
    info_search = Info_search.Info_search({"none":None})

    service = ["Musixmatch","Genius", "AZLyrics", "LyricsOVH"]
    func = [info_search._musixmatch, info_search._genius, info_search._az_lyrics, info_search._lyrics_ovh]
    for i in range(len(service)) :
        try :
            start = time.time()
            assert(func[i](artist,title))
            end = time.time()
            print(f'{service[i]} working (took {end-start}s)')
        except :
            print(f'{service[i]} not working')


if __name__ == '__main__':
    main()
