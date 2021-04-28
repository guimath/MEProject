from __future__ import unicode_literals


import youtube_dl
import json
import os

global filename

class _MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def _my_hook(d):
    global filename
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
        filename=d['filename'].replace(".webm",".mp3")

def dl(url,path):
    global filename
    ydl_opts = {
    'format': 'bestaudio/best',
    'writeinfojson':True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': _MyLogger(),
    'progress_hooks': [_my_hook],
    }
        
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    path_info =path+filename.replace(".mp3",".info.json")
    with open(path_info, mode="r") as j_object:
                info = json.load(j_object)
    os.remove(path_info)

    return filename,info['track'],info['uploader'].replace(" - Topic", "")

