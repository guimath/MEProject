"""from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
import unicodedata

from slugify import slugify

import youtube_dl
import pprint
import json
import os
import shutil
import string"""

import time
from multiprocessing import Process
import os
"""
def run_cpu_tasks_in_parallel(tasks):
    running_tasks = [Process(target=task) for task in tasks]
    for running_task in running_tasks:
        running_task.start()
    for running_task in running_tasks:
        running_task.join()

def func1() : 
    for i in range(10000000) :
        print("----------")

def func2() : 
    for i in range(10000000) :
        print("*********")

if __name__ == '__main__' :
    run_cpu_tasks_in_parallel([func1(),func2()])
"""
def func1():
  print ('func1: starting')
  for i in range(10000000): 
      print("*********")
      time.sleep(0.2)
  print ('func1: finishing')

def func2():
  print ('func2: starting')
  for i in range(10000000): 
      print("--------")
      time.sleep(0.2)
  print ('func2: finishing')

if __name__ == '__main__':
  """p1 = Process(target=func1)
  p1.start()
  p2 = Process(target=func2)
  p2.start()
  p1.join()
  p2.join()"""

"""
title = "Morose"
artist = "Damso"
search = ("Genius %s by %s" %(title, artist)).replace(" ", "+")

url_search = "https://www.google.com/search?client=opera&q=%s&sourceid=opera&ie=UTF-8&oe=UTF-8" %(search)
header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"}
resp = requests.get(url_search,headers = header)
"""

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


