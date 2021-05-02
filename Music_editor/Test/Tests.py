from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
import unicodedata

from slugify import slugify

import youtube_dl
import pprint
import json
import os
import shutil

filename = "file.mp3"
artist = "artist"
album = "album"
folder = artist+os.path.sep+album
if os.path.exists(folder) :
    if os.path.exists(folder+os.path.sep+filename) :
        pass# file already exists
    else :
        shutil.move(filename,folder)

else :
    os.makedirs(folder)
    shutil.move(filename,folder)





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


