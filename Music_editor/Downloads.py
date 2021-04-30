from __future__ import unicode_literals

import youtube_dl
import json
import os

import requests
import shutil

global filename

""" Downloading picture from specified url as specified filename to specified path
    @return the complete path of the new downloaded file if worked correctly, else returns 0"""
def dl_image(file_url, filename, path, interface):
    path = path + filename
    # Open the url image, set stream to True, this will return the stream content.
    try:
        r = requests.get(file_url, stream=True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True

            # Open a local file with wb ( write binary ) permission.
            with open(path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            return path
        else:
            interface.warning("image url can't be reached", "not adding image to file")
            return ""

    except:
        interface.warning("image downloading failed", "not adding image to file")
        return ""


""" Downloading mp3 file from specified url
    @return the filename
"""        
def dl_music(url,path):
    global filename
    ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'outtmpl' : "ytDL_%(id)s.%(ext)s", #name of output file
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    },{
        'key': 'FFmpegMetadata', #adding metadata to file
    }],
    'logger': _MyLogger(),
    'progress_hooks': [_my_hook],
    }
        
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename

""" -----------------------------------------------
    --------------- Private methods ---------------
    ----------------------------------------------- 
"""
    

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
        filename, _=d['filename'].split(".")
        filename += ".mp3"