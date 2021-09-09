import os 
import string # clean_string
import json # config
from difflib import SequenceMatcher # similar

# slugify 
import re
import unicodedata
import text_unidecode as unidecode

_unicode = str
_unicode_type = str
unichr = chr

QUOTE_PATTERN = re.compile(r'[\']+')
ALLOWED_CHARS_PATTERN = re.compile(r'[^-a-z0-9]+')
ALLOWED_CHARS_PATTERN_WITH_UPPERCASE = re.compile(r'[^-a-zA-Z0-9]+')
DUPLICATE_DASH_PATTERN = re.compile(r'-{2,}')
NUMBERS_PATTERN = re.compile(r'(?<=\d),(?=\d)')
DEFAULT_SEPARATOR = '-'


# ~ Lib with simple functions to help keep main prog clean ~ #

""" Compares two strings 
    @return True if strings are similar
"""
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio() > 0.5

""" Removes the "'feat." type from the title
    @return corrected title """
def remove_feat(title):
    lst1 = ["(Ft", "(ft", "(FEAT", "(Feat", "(feat", "(with", "(With", "FEAT"]

    for element in lst1 :
        if element in title :
            title =  title[0:title.rfind(element)]
            return title.strip()

    return title.strip()

""" Removes "the" from the title
    @return corrected title """
def remove_the(string) :
    if string[:3] == "the" or string[:3] == "The":
        return string[3:].strip()
    else :
        return string


def slugify(text, separator=DEFAULT_SEPARATOR, lowercase=True):
   
    """ Make a slug from the given text.
        @return corrected text """    

    # ensure text is unicode
    if not isinstance(text, _unicode_type):
        text = _unicode(text, 'utf-8', 'ignore')

    # replace quotes with dashes - pre-process
    text = QUOTE_PATTERN.sub(DEFAULT_SEPARATOR, text)

    # decode unicode
    text = unidecode.unidecode(text)

    # ensure text is still in unicode
    if not isinstance(text, _unicode_type):
        text = _unicode(text, 'utf-8', 'ignore')
    
    # translate
    text = unicodedata.normalize('NFKD', text)

    # make the text lowercase (optional)
    if lowercase:
        text = text.lower()

    # remove generated quotes -- post-process
    text = QUOTE_PATTERN.sub('', text)

    # cleanup numbers
    text = NUMBERS_PATTERN.sub('', text)

    # replace all other unwanted characters
    if lowercase:
        pattern = ALLOWED_CHARS_PATTERN
    else:
        pattern = ALLOWED_CHARS_PATTERN_WITH_UPPERCASE
    text = re.sub(pattern, DEFAULT_SEPARATOR, text)

    # remove redundant
    text = DUPLICATE_DASH_PATTERN.sub(DEFAULT_SEPARATOR, text).strip(DEFAULT_SEPARATOR)
    
    if separator != DEFAULT_SEPARATOR:
        text = text.replace(DEFAULT_SEPARATOR, separator)

    return text

""" Removes / modifies none ascii characters and punctuation
    @return the clean string"""
def clean_string(data) :
    for c in string.punctuation:
        data = data.replace(c, "")

    return data.replace(" ", "-")

""" Updates/ create config file according to given params"""
def update_config(config, interface):
    jsonString = json.dumps(config)

    try :
        with open("config.json", mode="w") as j_object:
            j_object.write(jsonString)
        
        return True

    except FileNotFoundError:
        if interface.ask("No config file found \ncreate one ?") :
            pass
        return True
        
    except Exception as e :
        interface.warn("unknown error during writing to config file : \n" + str(e))
        return False


def read_config(interface) :
    config = {}
    try:
        with open("config.json", mode="r") as j_object:
            config = json.load(j_object)

    except FileNotFoundError:
        interface.warn("No config file found \nusing standard setup")

    except json.JSONDecodeError as e:
        interface.warn("At line " + str(e.lineno)+ " of the config file, bad syntax (" + str(e.msg) + ")\nusing standard setup") 
    
    except Exception as e :
        interface.warn("unknown error : " + str(e) + "\nusing standard setup")

    params = {}
    params['feat_acronym'] = str (config.get("feat_acronym", "feat."))
    params['default_genre'] = str(config.get("default_genre","Other"))
    params['folder_name'] = str (config.get("folder_name","music"))
    params['get_label'] = bool (config.get("get_label",True))
    params['get_bpm'] = bool (config.get("get_bpm",True))
    params['get_lyrics'] = bool (config.get("get_lyrics",True))
    params['store_image_in_file'] = bool (config.get("store_image_in_file",True))
    
    return params

def create_config() :
    try :
        f = open('config.json','w+')
        f.close()
        return True
    except :
        return False
        

def rm_file(file_name):
    try :
        os.remove(file_name)
        return True
    except :
        return False


def find_ffmpeg():
    def is_exe(prg):
        return os.path.isfile(prg) and os.access(prg, os.X_OK)

    # just for windows
    if os.name == 'nt' :
        ffmpeg_name = 'ffmpeg.exe'
        ffprobe_name = 'ffprobe.exe'
    else :
        ffmpeg_name = 'ffmpeg'
        ffprobe_name = 'ffprobe'

    #if exec in folder :
    if os.path.exists("ffmpeg/"+ffmpeg_name) and os.path.exists("ffmpeg/"+ffprobe_name) :
        return "./"+ffmpeg_name
    
    #else tries to see if exec exists
    if os.path.split("ffmpeg")[0]:
        if is_exe(ffmpeg_name) :
            return ffmpeg_name
          
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, ffmpeg_name)
            if is_exe(exe_file) :
                return exe_file

    return False