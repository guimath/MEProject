# -*-coding:utf-8 -*

from mep import Downloads
# not working arghhhh

class Interface :
    def __init__(self):
        pass
    
    def warn(self, msg):
        print(msg)


interface = Interface()
interface.warn("starting")
img_url = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FOK_Computer&psig=AOvVaw2rDnGxUuPbwYg08DhsMK7e&ust=1629066638699000&source=images&cd=vfe&ved=0CAoQjRxqFwoTCIDAiqXIsfICFQAAAAAdAAAAABAD"
Downloads.dl_image(img_url,"test_image.png", interface)
