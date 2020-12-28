
import shutil

# to 'slugify' string
from slugify import slugify 
import re
import codecs

# to get lyrics (crawler)
import requests 
from bs4 import BeautifulSoup  


class MEP:
    def __init__(self, interface, debug):
        self.debug     = debug
        self.interface = interface

    # Removes the "'feat." type from the title
    # @returns corrected title
    def remove_feat(self, title):
        if "(Ft" in title or "(ft" in title or "(Feat" in title or "(feat" in title:
            # complicated in case there is anothere paranthesis in the title
            b = []
            b = title.split("(")
            title = b[0]
            for i in range(1, len(b)-1):
                title = title + "(" + b[i]
        return title.strip()

    """ 
    # removes unwanted characteres to make the name file friendly
    # @return value the correcter string
    def slugify(self, value):
        value = unicodedata.normalize('NFKC', value)
        value = re.sub(r'[^\w\s-]', '', value).strip().lower()
        value = re.sub(r'[-\s]+', '-', value)

        return value"""

    # Downloading picture from specified url as specified filename to specified path
    # @returns the complete path of the new downloaded file if worked correctly, else returns 0
    def get_file(self, file_url, filename, path):
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
                self.interface.warning("image url can't be reached", "not adding image to file")
                return ""

        except:
            self.interface.warning("image downloading failed", "not adding image to file")
            return ""
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
            search_url = "https://www.musixmatch.com/search/%s-%s/tracks" % (
                artist.replace(' ', '-'), title.replace(' ', '-'))
            header = {"User-Agent": "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)"}
            search_results = requests.get(search_url, headers=header)
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
        url = ""
        lyrics = "Error1"
        try:
            url = "http://genius.com/%s-%s-lyrics" % (artist.replace(' ', '-'), title.replace(' ', '-'))
            print(url)
            lyrics_page = requests.get(url)
            soup = BeautifulSoup(lyrics_page.text, 'html.parser')
            lyrics_container = soup.find("div", {"class": "lyrics"})
            if lyrics_container:
                
                lyrics = lyrics_container.get_text()
                # artist.lower().replace(" ", "")
                if artist.lower().replace(" ", "") not in soup.text.lower().replace(" ", ""):
                    print("?")
                #    lyrics = "Error2"
        except Exception as error:
            print(error)
        return lyrics

    def get_lyrics(self, artist, title):
        #slugify both
        title = slugify(title.replace("'",""))
        artist = slugify(artist.replace("'",""))
        #artist = artist[0] + artist[1:].lower() 
        lyrics = self._musixmatch(artist, title)
        service = "musixmatch"
        if lyrics == "Error1" :
            print("2nd try")
            lyrics = self._genius(artist, title)
            service = "genius"
            if lyrics == "Error1" :
                service = "lyrics not found"
                return "", service

        elif lyrics == "Error2" :
            service = "lyrics not found"
            return "", service
        return lyrics, service