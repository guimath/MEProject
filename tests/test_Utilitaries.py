# -*-coding:utf-8 -*
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in corect dir

import time 
from Test import * 

from mep import Utilitaries
def main() :
    lst =["Bing Crosby",
        "Elton John",
        "Mungo Jerry",
        "Bill Haley & His Comets",
        "Domenico Modugno",
        "Whitney Houston",
        "Elvis Presley",
        "USA for Africa",
        "The Ink Spots",
        "Céline Dion",
        "The Beatles",
        "John Travolta et Olivia Newton",
        "Bryan Adams"]
    res = ""

    headp("Testing Utilitaries")
    for a in lst :
        for b in lst :
            if  Utilitaries.similar(a,b) :
                res+=(f'{a} = {b} ')
    assert(res=="Bing Crosby = Bing Crosby Elton John = Elton John Mungo Jerry = Mungo Jerry Bill Haley & His Comets = Bill Haley & His Comets Domenico Modugno = Domenico Modugno Whitney Houston = Whitney Houston Elvis Presley = Elvis Presley USA for Africa = USA for Africa The Ink Spots = The Ink Spots Céline Dion = Céline Dion The Beatles = The Beatles John Travolta et Olivia Newton = John Travolta et Olivia Newton Bryan Adams = Bryan Adams ")
    greenp("similar working")
    
if __name__ == '__main__':
    main()
