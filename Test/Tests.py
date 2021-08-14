import codecs
import time
from multiprocessing import Process
import os
import logging

#Not working 
#from Music_editor import Downloads, Info_search, Tagger, Utilitaries
from slugify import slugify

import requests, sys, os, re, urllib
from bs4 import BeautifulSoup
import pprint

if __name__ == '__main__':
    #search = s.Info_search({"qzd":14})
    url = "https://www.musixmatch.com/search/%s-%s/tracks" % ("The-Strokes", "At-The-Door")
    print(url)
    #_musixmatch("The Strokes", "At The Door")




