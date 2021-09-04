import os
import requests #(uses only requests.get)
import shutil # (uses only shutil.copyfileobj)
import json

import youtube_dl 



# ~ Lib responsible of all downloads (image and music) ~ #

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
            interface.warn("image url can't be reached", "not adding image to file")
            return ""

    except:
        interface.warn("image downloading failed", "not adding image to file")
        return ""


""" Downloading mp3 file from specified urlS
"""        
def dl_music(url,no_playlist,logger, hook, lst=None):
    ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': no_playlist,
    'outtmpl' : "yt-DL_%(title)s.%(ext)s", #name of output file
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

    if os.path.exists("ffmpeg") :
        ydl_opts['ffmpeg_location'] = './ffmpeg'
    
    if lst :
        ydl_opts['playlist_items'] = lst
   
    try :     
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        logger.error(e.args)
        return False

    
def check_out_playlist(url):
    class Interface :
        def __init__(self):
            self.videos = {}
        
        def debug(self, msg):
            if '{"_type": ' in msg :
                j = json.loads(msg)
                self.videos = j['entries']
            if '[download] Downloading playlist:' in msg :
                self.playlist_name = msg.replace('[download] Downloading playlist: ','')

        def warning(self, msg):
            pass
        def error(self,msg):
            print(f'Error during yt-dl : {msg}')
    
    interface = Interface()
    
    ydl_opts = {
        'dump_single_json' : True,
        'extract_flat':'in_playlist',
        'playlistend': 50,
        'logger': interface,
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    res = []
    for video in interface.videos :
        secs = int(video['duration']%60)
        mins = int((video['duration'] - secs)/60)
        duration = f'{mins}min {secs}s'
        #print(video)
        res.append({'title': video['title'],'uploader':video['uploader'], 'duration':duration, 'id':len(res)})
    
    return res, interface.playlist_name