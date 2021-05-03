from __future__ import unicode_literals

import youtube_dl
import json
import os

import requests
import shutil

""" Downloading picture from specified url as specified filename to specified path
    @return the name of the new downloaded file if worked correctly, else returns '' """
def dl_image(file_url, filename, interface):
    # Open the url image, set stream to True, this will return the stream content.
    try:
        r = requests.get(file_url, stream=True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True

            # Open a local file with wb ( write binary ) permission.
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            return filename
        else:
            interface.warning("image url can't be reached", "not adding image to file")
            return ""

    except:
        interface.warning("image downloading failed", "not adding image to file")
        return ""


""" Downloading mp3 file from specified url
"""        
def dl_music(url,no_playlist,logger, hook):
    ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': no_playlist,
    'outtmpl' : "ytDL_%(id)s.%(ext)s", #name of output file
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    },{
        'key': 'FFmpegMetadata', #adding metadata to file
    }],
    'logger': logger,
    'progress_hooks': hook,
    }
        
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    
