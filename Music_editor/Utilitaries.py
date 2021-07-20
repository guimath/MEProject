
import string 
import json

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

""" Updates/ create config file according to given params"""
def update_config(config, interface):
    jsonString = json.dumps(config)

    try :
        with open("config.json", mode="w") as j_object:
            j_object.write(jsonString)

    except FileNotFoundError:
        if interface.ask("No config file found \ncreate one ?") :
            pass
        
    except Exception as e :
        interface.warn("unknown error during writing to config file : \n" + str(e))


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

