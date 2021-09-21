NAME = 1MEP
COMP = pyinstaller
SRC  = mep/Main.py

build :
	$(COMP) $(SRC) -n $(NAME) --onefile --clean --hidden-import='PIL._tkinter_finder'
	chmod +x dist/1MEP

#for windows : pyinstaller mep\Main.py -n 1MEP --onefile --clean --hidden-import='PIL._tkinter_finder'
