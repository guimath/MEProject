class Interface:
    """ Everything that has to do with the visual interface is done here"""

    def __init__(self, params):
        # storing a few parameters
        self._ignore = ["MEProject.exe"]
        self.accepted_extensions = params["accepted_extensions"] 
        self.debug = params["debug"] 
        self.all_Auto = False #will be updated when user chooses mode
        # will inherit from pyglet ?
        
    """ Asking user a yes no question 
        @param message the string to be displayed as a question
        @return True or False (depending on user response) """
    def ask(self, message, reason = ""):
        if self.all_Auto:
            return False
        if (reason != ""):
            print(reason)
        ans = input("-> " + message + " (y/n) : ")
        if ans == 'y' or ans == 'Y':
            return True
        else:
            return False

    """ Welcoming user and getting mode
        @return mode_nb the mode number (between 1 and 3) chosen by user """
    def global_start(self):
        mode_name = ['full auto', 'semi auto', 'discovery','download']
        print("")
        print("         Welcome to MEProject")
        print("")
        print("-------------------------------------")
        print("|           mode selection          |")
        print("+-----------------------------------+")
        print("|     1     |     2     |     3     |")
        print("+-----------+-----------+-----------+")
        print("| full auto | semi auto | discovery |")
        print("-------------------------------------")
        print("")
        if self.debug :
            print("mode : 1")
            mode_nb = 1
        else :
            mode_nb = int(input("mode : "))
        
        if mode_nb > 4:
            mode_nb = 3
        elif mode_nb <= 1:
            mode_nb = 1
            self.all_Auto = True
            
        print("Now entering mode {}".format(mode_name[mode_nb-1]))
        print("\n")
        return mode_nb

    def get_URL(self) :
        return input("URL to download : ")


    """ error message for when user dropped a file in wrong format
        Displays the name of file in wrong format and a list of accepted formats"""
    def wrong_format(self, wrong_file_name):
        if (wrong_file_name not in self._ignore):
            print("the file '{}' is not in supported format" .format(wrong_file_name))
            print("the supported formats are : ")
            for i in range(0, len(self.accepted_extensions)):
                print(self.accepted_extensions[i])
            self._ignore.append(wrong_file_name)

    """ Beginning of the process for a new file
        Displays  what file is being treated"""
    def start_process(self, file_nb, total_file_nb, file_name):
        print("-------------------------------------------------------\n")
        print("file {} out of {} : '{}'".format(
            file_nb, total_file_nb, file_name))

    """ Showing artist and title (reduced version of track_info)"""
    def artist_and_title(self, artist, title):
        print("artist : {}".format(artist))
        print("title  : {}".format(title))

    """ error message : file already went through the system
        is linked to an ask
        """
    def already_treated(self):
        print("file has already been treated with MEP")

    """ Getting title and artist from user
        @return (artist, title) the info given by user 
        """
    def get_title_manu(self, reason= ""):
        if reason != "" :
            print(reason)

        print("Let's do it manually then !")
        print("")
        artist = input("artist name : ")
        title = input("track name  : ")
        return (artist, title)



    def manual_tagging(self, artist, title):
        print("ok let's go !")
        self.artist_and_title(artist, title)
        # will need to be expanded

    """ Displaying info on the track
        Visual might change depending on information"""
    def track_infos(self, Is_Sure, title, artists, album, genre, release_date, track_nb, total_track_nb, lyrics_service):
        if Is_Sure:
            print("")
            print("We have a match !")
            print("")
        else:
            print("")
            print("exact track not found")
            print("")
            print("Potential track :")
        nb_artist = len(artists)

        # Basic infos :
        if nb_artist == 1:  # no feat
            print("{} by {} :".format(title, artists[0]['name']))

        elif nb_artist == 2:
            print("{} by {} featuring {}".format(
                title, artists[0]['name'], artists[1]['name']))

        else:
            print("{} by {} featuring {} & {}".format(
                title, artists[0]['name'], artists[1]['name'], artists[2]['name']))


        print("album        : {}\nGenre        : {}\nrelease date : {}\nTrack number : {} out of {}\nLyrics       : {}".format(
            album, genre, release_date, track_nb, total_track_nb, lyrics_service))
        # there would also be a picture display if all was great...

    """ error message for when a file is skiped 
        Displays error number and explication"""
    def error(self, error_nb):
        print(    "---------------------------------")
        print(    "| file was skipped | error n°{}  |".format(error_nb)) 
        print(    "---------------------------------")
        if error_nb == 1:
            print("|    file couldn't be edited    |")
        elif error_nb == 2:
            print("| file was moved during process |")
        elif error_nb == 3:
            print("|  file already in the folder   |")
        elif error_nb == 4:
            print("| file didn't have usable tags  |")
        elif error_nb == 5:
            print("|  No matching track was found  |")
        print(    "---------------------------------\n")

    def warning(self, problem, solution):
        print("[WARNING] " + problem + " -> " + solution )
    
    """ Closing program when in full auto mode 
        Gives litle summary of actions (nb of files processed out of total)"""
    def end_full_auto(self, total_file_nb, treated_file_nb) :
        """ Closing program when in full auto mode 
            Gives litle summary of actions (nb of files processed out of total)"""

        if not self.debug: 
            if total_file_nb == 0:
                input("No file found")
            else:
                input("{} files correctly processed out of {}".format(
                    treated_file_nb, total_file_nb))
        else:
            print("{} files correctly processed out of {}".format(
                treated_file_nb, total_file_nb))
