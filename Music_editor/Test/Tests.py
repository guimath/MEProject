from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
import unicodedata

from slugify import slugify

import youtube_dl
import pprint
import json
import os

global filename

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    global filename
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
        filename=d['filename'].replace(".webm",".mp3")





def dl(url):
    ydl_opts = {
    'format': 'bestaudio/best',
    'writeinfojson':True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    }
        
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    path_info ="/home/guilhem/Documents/MEProject/"+filename.replace(".mp3",".info.json")
    with open(path_info, mode="r") as j_object:
                info = json.load(j_object)
    pprint.pprint(info)
    os.remove(path_info)

    return filename,info['track'],info['uploader'].replace(" - Topic", "")




print(dl("https://www.youtube.com/watch?v=1uYWYWPc9HU"))




'''
class GeniusCrawler(Crawler):
    def __init__(self):
        super().__init__('Genius Lyric')

    def search_for_lyrics(self, artist, song):
        try:
            _artist = str(artist).strip().replace(' ', '-').replace("'", '')
            _name_song = song.strip().replace(' ', '-').replace("'", '')
            song_url = '{}-{}-lyrics'.format(_artist, _name_song)
            request = requests.get("https://genius.com/{}".format(song_url))

            html_code = BeautifulSoup(request.text, features="html.parser")
            lyric = html_code.find("div", {"class": "lyrics"}).get_text()

            return self.format_lyrics(lyric)

        except Exception as e:
            self.raise_not_found()

    
    def format_lyrics(self, lyric):
        lines = map(
            lambda line: line if ']' not in line and '[' not in line else None,
            lyric.split('\n')
        )
        lines = filter(
            lambda line: line is not None,
            list(lines)
        )
        return list(lines) 

def split_to_word(string):
    return string.replace("\n", " ").replace("\r", " ").split(" ")'''


