import os 
import string 
import json
from difflib import SequenceMatcher


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

"""
def slugify(text, entities=True, decimal=True, hexadecimal=True, max_length=0, word_boundary=False,
            separator="_", save_order=False, stopwords=(), regex_pattern=None, lowercase=True,
            replacements: typing.Iterable[typing.Iterable[str]] = ()):
   
    Make a slug from the given text.
    :param text (str): initial text
    :param entities (bool): converts html entities to unicode
    :param decimal (bool): converts html decimal to unicode
    :param hexadecimal (bool): converts html hexadecimal to unicode
    :param max_length (int): output string length
    :param word_boundary (bool): truncates to complete word even if length ends up shorter than max_length
    :param save_order (bool): if parameter is True and max_length > 0 return whole words in the initial order
    :param separator (str): separator between words
    :param stopwords (iterable): words to discount
    :param regex_pattern (str): regex pattern for allowed characters
    :param lowercase (bool): activate case sensitivity by setting it to False
    :param replacements (iterable): list of replacement rules e.g. [['|', 'or'], ['%', 'percent']]
    :return (str):
    

    # user-specific replacements
    if replacements:
        for old, new in replacements:
            text = text.replace(old, new)

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

    # character entity reference
    if entities:
        text = CHAR_ENTITY_PATTERN.sub(lambda m: unichr(name2codepoint[m.group(1)]), text)

    # decimal character reference
    if decimal:
        try:
            text = DECIMAL_PATTERN.sub(lambda m: unichr(int(m.group(1))), text)
        except Exception:
            pass

    # hexadecimal character reference
    if hexadecimal:
        try:
            text = HEX_PATTERN.sub(lambda m: unichr(int(m.group(1), 16)), text)
        except Exception:
            pass

    # translate
    text = unicodedata.normalize('NFKD', text)
    if sys.version_info < (3,):
        text = text.encode('ascii', 'ignore')

    # make the text lowercase (optional)
    if lowercase:
        text = text.lower()

    # remove generated quotes -- post-process
    text = QUOTE_PATTERN.sub('', text)

    # cleanup numbers
    text = NUMBERS_PATTERN.sub('', text)

    # replace all other unwanted characters
    if lowercase:
        pattern = regex_pattern or ALLOWED_CHARS_PATTERN
    else:
        pattern = regex_pattern or ALLOWED_CHARS_PATTERN_WITH_UPPERCASE
    text = re.sub(pattern, DEFAULT_SEPARATOR, text)

    # remove redundant
    text = DUPLICATE_DASH_PATTERN.sub(DEFAULT_SEPARATOR, text).strip(DEFAULT_SEPARATOR)

    # remove stopwords
    if stopwords:
        if lowercase:
            stopwords_lower = [s.lower() for s in stopwords]
            words = [w for w in text.split(DEFAULT_SEPARATOR) if w not in stopwords_lower]
        else:
            words = [w for w in text.split(DEFAULT_SEPARATOR) if w not in stopwords]
        text = DEFAULT_SEPARATOR.join(words)

    # finalize user-specific replacements
    if replacements:
        for old, new in replacements:
            text = text.replace(old, new)

    # smart truncate if requested
    if max_length > 0:
        text = smart_truncate(text, max_length, word_boundary, DEFAULT_SEPARATOR, save_order)

    if separator != DEFAULT_SEPARATOR:
        text = text.replace(DEFAULT_SEPARATOR, separator)

    return text"""

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

    #if exec in folder :
    if os.path.exists("ffmpeg/ffmpeg") and os.path.exists("ffmpeg/ffprobe") :
        return "./ffmpeg"
    
    #else tries to see if exec exists
    if os.path.split("ffmpeg")[0]:
        if is_exe("ffmpeg") :
            return "ffmpeg"
          
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, "ffmpeg")
            if is_exe(exe_file) :
                return exe_file

    return False