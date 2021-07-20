from slugify import slugify
from bs4 import BeautifulSoup  # crawler
import requests # get web pages
import re # get all pages corresponding 
import codecs # to decode text

# for spotify api
import spotipy  # Spotify API
from spotipy.oauth2 import SpotifyClientCredentials

import Utilitaries as util
from pprint import pprint

class Info_search:
    def __init__(self, params): 
        self.params =  params
        self.MATCH_NB = 4
        # Spotify api authorization Secret codes (DO NOT COPY / SHARE)
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fb69ab85a5c749e08713458e85754515",                                                        client_secret= "ebe33b7ed0cd495a8e91bc4032e9edf2")) 

    """ gets basic infos from web
        @return items dict containing multiple tracks """
    def get_basic_info(self, artist, title):
        return self._spotify_basic_info(artist, title)


    """ gets advanced infos (genre, label, bpm and lyrics) from web
        @return track dict"""
    def get_advanced_info(self, track):
        #getting genre, label and bpm
        if track["info_service"] == "spotify" :
            track = self._spotify_advanced_info(track)
        else :
            return track # impossible
        
        # getting lyrics
        if self.params['get_lyrics'] :
            (track['lyrics']['text'], track['lyrics']['service']) = self.get_lyrics(track['artists'][0]['name'], track['name'])
        else :
            track['lyrics']['service'] = "ignored"
            track['lyrics']['text'] =  ""

        return track

    """ gets lyrics from web 
        @return tuple containing two strings : lyrics and the service used (i.e. genius etc) """
    def get_lyrics(self, artist, title):
        #slugify both
        title = util.clean_string(title)
        artist = util.clean_string(artist)
        
        #Start with musixmatch
        lyrics = self._musixmatch(artist, title)
        service = "musixmatch"
        if lyrics == "Error1" :
            # if no result go to genius
            lyrics = self._genius(artist, title)
            service = "genius"
            if lyrics == "Error1" :
                # if no result stop
                return ("", "lyrics not found")

        elif lyrics == "Error2" :
            return ("", "lyrics not found")

        else :
            return lyrics, service

    """ -----------------------------------------------
        --------------- Private methods ---------------
        ----------------------------------------------- 
    """

    """ getting basic info using spotify api
    @return items dict or False if no match was found """    
    def _spotify_basic_info(self, artist, title):
        search = "track:" + title.replace("'", "") + " artist:" + artist
        items = self._spotify_search(search)
        if items :
            return items
        else :
            return self._spotify_search("track:" + title.replace("'", ""))

    """ Simple search (and slight modification) using the spotify api
        @return items dict or False if no match was found """
    def _spotify_search(self, search) :
        results = self.sp.search(q= search, type = "track", limit = self.MATCH_NB)
        items = results['tracks']['items']
        to_rm = []
        if len(items) > 0:
            for i in range(len(items)) :
                if (items[i]['album']['artists'][0]['name'] == 'Various Artists') :
                    to_rm.append(i)
                else :
                    items[i]['name'] = util.remove_feat(items[i]['name'])  # in case of featuring
                    items[i]['album']['artwork'] = items[i]['album']['images'][0]['url']
                    items[i]['lyrics'] = {}
                    items[i]["info_service"] = "spotify"
            nb = 0
            for i in to_rm :
                items.pop(i-nb)
                nb += 1

            return items
        else :
            return False

    """ getting more advanced infos from spotify api
        @return track dict"""         
    def _spotify_advanced_info(self, track):
        #getting genre
        results = self.sp.artist(track['artists'][0]['id'])
        if len(results['genres']) > 0:
            track['genre'] = results['genres'][0]
        else:
            track['genre'] = self.params['default_genre']

        # getting label and copyright
        if self.params['get_label']:
            results = self.sp.album(track['album']['id'])
            if len(results) > 0:
                track['album']['copyright'] = results['copyrights'][0]['text']
                track['album']['label'] = results['label']
            else:
                # default
                track['album']['copyright'] = ""
                track['album']['label'] = ""

        # getting BPM
        if self.params['get_bpm']:
            results = self.sp.audio_analysis(track['id'])
            if len(results) > 0:
                track['bpm'] = int(results['track']['tempo'])
            else:
                track['bpm'] = 0  # default
        
        return track 

    def _musixmatch(self, artist, title):

        url = ""
        lyrics = "Error1"

        def extract_mxm_props(soup_page):
            scripts = soup_page.find_all("script")
            props_script = None
            for script in scripts:
                if script and script.contents and "__mxmProps" in script.contents[0]:
                    props_script = script
                    break
            return props_script.contents[0]

        try:
            url = "https://www.musixmatch.com/search/%s-%s/tracks" % (artist, title)
            header = {"User-Agent": "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)"}
            search_results = requests.get(url, headers=header)
            soup = BeautifulSoup(search_results.text, 'html.parser')
            page = re.findall('"track_share_url":"([^"]*)', extract_mxm_props(soup))
            if page:
                url = codecs.decode(page[0], 'unicode-escape')
                lyrics_page = requests.get(url, headers=header)
                soup = BeautifulSoup(lyrics_page.text, 'html.parser')
                props = extract_mxm_props(soup)
                if '"body":"' in props:
                    lyrics = props.split('"body":"')[1].split('","language"')[0]
                    lyrics = lyrics.replace("\\n", "\n")
                    lyrics = lyrics.replace("\\", "")
                    if not lyrics.strip():
                        lyrics = "Error1"
                    album = soup.find(class_="mxm-track-footer__album")
                    if album:
                        album = album.find(class_="mui-cell__title").getText()
        except Exception as error:
            print(error)
            lyrics = "Error2"
        return lyrics

    def _genius(self, artist, title):
        lyrics = "Error1"
        try:
            url = "http://genius.com/%s-%s-lyrics" % (slugify(artist),slugify(title))
            lyrics_page = requests.get(url)
            soup = BeautifulSoup(lyrics_page.text, 'html.parser')
            lyrics_container = soup.find("div", {"class": "lyrics"})
            if lyrics_container:
                
                lyrics = lyrics_container.get_text()
                if artist.lower().replace(" ", "") not in soup.text.lower().replace(" ", ""):
                    print("Please contact programmer -> unwanted bug")
                #    lyrics = "Error2"
        except Exception as error:
            print(error)
        return lyrics

