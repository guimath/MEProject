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

class _MyLogger(object):
    def debug(self, msg):
        pass#print(msg)
        

    def warning(self, msg):
        pass#print(msg)

    def error(self, msg):
        print(msg)

def _my_hook(d):
    global filename
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
        filename=d['filename'].replace(".webm",".mp3")





def dl(url):
    ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'outtmpl' : "ytDL_%(id)s.%(ext)s",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    },{
        'key': 'FFmpegMetadata',
    }],
    'logger': _MyLogger(),
    'progress_hooks': [_my_hook],
    }
        
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename




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


