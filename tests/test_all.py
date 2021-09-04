#!/usr/bin/env python
# coding: utf-8 

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in correct dir

import time 
from Test import * 

import test_Downloads, test_Info_search, test_Tagger, test_Utilitaries

def main() :
    test_Downloads.main()
    test_Info_search.main()
    test_Tagger.main()
    test_Utilitaries.main()

if __name__ == '__main__':
    main()
