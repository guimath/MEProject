import requests, urllib # get web pages
import re # get all pages corresponding 
import codecs # to decode text
import time

from slugify import slugify # TODO replace with util slugify

from bs4 import BeautifulSoup  # crawler

# for spotify api
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random import choice as random_choice

import mep.Utilities as util

# ~ Class responsible of all web searches (tags like album, genre etc as well as lyrics) ~ #

class Info_search:
    def __init__(self, params): 
        self.params =  params
        self.MATCH_NB = 4 # Number of matches that are saved during basic info search 

        # Spotify api authorization Secret codes (DO NOT COPY / SHARE)
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fb69ab85a5c749e08713458e85754515",                                                        client_secret= "ebe33b7ed0cd495a8e91bc4032e9edf2")) 

        self.HEADERS = [{'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 OPR/78.0.4093.184'},
                        {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'},
                        {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}]

        self.PROXIES = urllib.request.getproxies()
        self.retry = False

    """ gets basic infos from web
        @return items dict containing multiple tracks """
    def get_basic_info(self, artist, title):
        return self._spotify_basic_info(artist, title)


    """ gets advanced infos (genre, label, bpm and lyrics) from web
        @return track dict"""
    def get_advanced_info(self, track):
        #getting genre, label and bpm
        if track["info"]["service"] == "spotify" :
            track = self._spotify_advanced_info(track)
        else :
            return False # impossible
        
        # getting lyrics
        if self.params['get_lyrics'] :
            (track['lyrics']['text'], track['lyrics']['service']) = self.get_lyrics(track['artists'][0]['name'], track['name'])
        else :
            track['lyrics']['service'] = ""
            track['lyrics']['text'] =  ""

        track['info']['full'] = True
        return track

    """ gets lyrics from web 
        @return tuple containing two strings : lyrics and the service used (i.e. genius etc) """
    def get_lyrics(self, artist, title):
        title = util.clean_string(title)
        artist = util.clean_string(artist)
        
        lyrics, service = self._genius(artist, title), 'Genius'
        if lyrics :
            return lyrics, service

        lyrics,  service = self._musixmatch(artist, title), "Musixmatch"
        if lyrics :
            return lyrics, service
        
        lyrics, service = self._az_lyrics(artist, title), 'AZLyrics'
        if lyrics :
            return lyrics, service

        return ("", "Lyrics not found")
           
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
            return items, True
        else :
            return self._spotify_search("track:" + title.replace("'", "")), False

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
                    items[i]['info'] = {'service' : 'spotify', 'full':False}

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
    
    def _scrap(self, url):
        header = random_choice(self.HEADERS)

        try :
            response = requests.get(url, headers=header, proxies=self.PROXIES) 
            
            if response.status_code == 200:
                self.retry = False
                return BeautifulSoup(response.text, 'html.parser')

            elif response.status_code == 503 and not self.retry : # server overload
                time.sleep(0.2)
                print("waiting")
                self.retry = True
                return self._scrap(url) 
            else :
                print(f'Request error during lyrics search ({url=}), {response.status_code = } \nType : {response.headers["content-type"]}')
                self.retry = False
                return False
        except Exception as error:
            print(f'error during lyrics search ({url=}) : {error}')
            self.retry = False
            return False
    
    def _musixmatch(self, artist, title):
        url = "https://www.musixmatch.com/search/%s-%s/tracks" % (artist, title)
        #print(f'musixmatch : {url=}')
        
        def _extract_mxm_props(soup_page):
            scripts = soup_page.find_all("script")
            props_script = None
            for script in scripts:
                if script and script.contents and "__mxmProps" in script.contents[0]:
                    props_script = script
                    return props_script.contents[0]
            return False

        soup = self._scrap(url)
        if soup :
            props = _extract_mxm_props(soup)
            if props :
                page = re.findall('"track_share_url":"([^"]*)', props)
                if page:
                    url = codecs.decode(page[0], 'unicode-escape')
                    #print(f'musixmatch : {url=}')
                    soup = self._scrap(url)
                    if soup :
                        props = _extract_mxm_props(soup)
                        if '"body":"' in props:
                            lyrics = props.split('"body":"')[1].split('","language"')[0]
                            lyrics = lyrics.replace("\\n", "\n")
                            lyrics = lyrics.replace("\\", "")
                            if lyrics.strip():
                                return lyrics
        
        return False

    def _genius(self, artist, title):
        artist = slugify(artist)
        title = slugify(title)
        url = "http://genius.com/%s-%s-lyrics" % (artist,title)
        #print(f'genius : {url=}')
        
        soup = self._scrap(url)
        if soup :
            lyrics_container = soup.find("div", {"class": "lyrics"})
            if lyrics_container:
                    lyrics = lyrics_container.get_text()
                    if artist.lower().replace(" ", "") in soup.text.lower().replace(" ", ""):
                        return lyrics
        return False

    def _az_lyrics(self, artist, title):
        artist = util.remove_the(slugify(artist,separator=""))
        title = slugify(title,separator="")
        url = "https://www.azlyrics.com/lyrics/%s/%s.html" % (artist,title) 
        #print(f'azlyrics : {url=}')

        soup = self._scrap(url)
        if soup :
            center = soup.body.find("div", {"class": "col-xs-12 col-lg-8 text-center"})
            if center:
                lyrics = center.find("div", {"class": None}).text

                lyrics = re.sub(r"<br>", " ", lyrics)
                lyrics = re.sub(r"<i?>\W*", "[", lyrics)
                lyrics = re.sub(r"\W*</i>", "]", lyrics)
                lyrics = re.sub(r"&quot;", "\"", lyrics)
                lyrics = re.sub(r"</div>", "", lyrics)
                lyrics = lyrics.strip()
                return lyrics
        
        return False
   

    def _lyrics_ovh(self, artist, title):
        url = "https://api.lyrics.ovh/v1/%s/%s" % (artist, title)
        #print(f'lyricsOVH : {url=}')

        r = requests(url)
        print(r.status_code)
        print(r.text)
        print(r.content)
        return False 