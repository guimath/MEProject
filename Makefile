NAME = 1MEP
COMP = pyinstaller
SRC  = mep/Main.py
TEST = tests/test_all.py

build :
	$(COMP) $(SRC) -n $(NAME) --onefile --clean --hidden-import='PIL._tkinter_finder'
	chmod +x dist/$(NAME)

#for windows : pyinstaller mep\Main.py -n 1MEP --onefile --clean --hidden-import='PIL._tkinter_finder'


test :
	python3 $(TEST)