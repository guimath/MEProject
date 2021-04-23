from bs4 import BeautifulSoup
import requests
import unicodedata

from slugify import slugify

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
        return list(lines) '''

def split_to_word(string):
    return string.replace("\n", " ").replace("\r", " ").split(" ")

def _genius(artist, title):
    url = ""
    lyrics = "Error1"
    try:
        url = "http://genius.com/%s-%s-lyrics" % (artist.replace(' ', '-'), title.replace(' ', '-'))
        lyrics_page = requests.get(url)
        soup = BeautifulSoup(lyrics_page.text, 'html.parser')
        lyrics_container = soup.find("div", {"class": "lyrics"})
        if lyrics_container:
            lyrics = lyrics_container.get_text()
            if artist.lower().replace(" ", "") not in soup.text.lower().replace(" ", ""):
                lyrics = "Error2"
    except Exception as error:
        print("unkown error with lyrics")
    return lyrics

def get_lyrics(artist, title):
    #slugify both
    lyrics = _genius(artist, title)
    if lyrics == "Error1" :
        print("warning no lyrics found")
    elif lyrics == "Error2" :
        print("unkown error with lyrics")
    else :
        return lyrics
    
def main() :
    val = "Spider ZED"
    val = str(val[0]) + val[1:].lower() 
    #val = re.sub(r'[-\s]+', '-', val)
    print(val)

if __name__ == '__main__':
    main()
