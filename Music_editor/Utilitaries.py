
from slugify import slugify
import string 
from bs4 import BeautifulSoup  # crawler
import requests # get web pages
import re # get all pages corresponding 
import codecs # to decode text


""" Removes the "'feat." type from the title
    @return corrected title """
def remove_feat(title):
    if "(Ft" in title or "(ft" in title or "(Feat" in title or "(feat" in title:
        title =  title[0:title.rfind('(')]

    return title.strip()

""" Removes / modifies none ascii characters and punctuation
    @return the clean string"""
def clean_string(data) :
    for c in string.punctuation:
        data = data.replace(c, "")

    return data.replace(" ", "-")

""" gets lyrics from web 
    @return tuple containing two strings : lyrics and the service used (i.e. genius etc) """
def get_lyrics(artist, title):
    #slugify both
    title = clean_string(title)
    artist = clean_string(artist)
    lyrics = _musixmatch(artist, title)
    service = "musixmatch"
    if lyrics == "Error1" :
        lyrics = _genius(artist, title)
        service = "genius"
        if lyrics == "Error1" :
            service = "lyrics not found"
            return "", service

    elif lyrics == "Error2" :
        service = "lyrics not found"
        return "", service
    return lyrics, service

""" -----------------------------------------------
    --------------- Private methods ---------------
    ----------------------------------------------- 
"""
    
def _musixmatch(artist, title):

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

def _genius(artist, title):
    lyrics = "Error1"
    try:
        url = "http://genius.com/%s-%s-lyrics" % (slugify(artist),slugify(title))
        lyrics_page = requests.get(url)
        soup = BeautifulSoup(lyrics_page.text, 'html.parser')
        lyrics_container = soup.find("div", {"class": "lyrics"})
        if lyrics_container:
            
            lyrics = lyrics_container.get_text()
            # artist.lower().replace(" ", "")
            if artist.lower().replace(" ", "") not in soup.text.lower().replace(" ", ""):
                print("Please contact programmer -> unwanted bug")
            #    lyrics = "Error2"
    except Exception as error:
        print(error)
    return lyrics

