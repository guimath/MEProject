# -*-coding:utf-8 -*
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # patch for imports
os.chdir(os.path.dirname(__file__)) # places in corect dir

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def redp(msg):
    print(f'{FAIL}{msg}{ENDC}')

def greenp(msg):
    print(f'{OKGREEN}{msg}{ENDC}')

def headp(msg):
    (print)
    print("--------------------")
    print(f'{BOLD}{WARNING}{msg}{ENDC}')
