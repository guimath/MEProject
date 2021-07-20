# for file modification
import os
import eyed3  # to parse mp3 files
import os

# ~ Responsible of all the writing and reading of music file tags ~ #
#   (only supports mp3 for now)

class Tagger:
    def __init__(self, params, ADD_SIGN, SIGN):
        self.add_signature = ADD_SIGN
        self.signature = SIGN
        self.state = [0,0,0,2,1,3]
        self.store_image_in_file =  params['store_image_in_file']
        self.folder = params['folder_name']
        
        eyed3.log.setLevel("ERROR")  # hides errors from eyed3 package

    """gets specific info stored in a given music file
       @return title, artist and encoded_by tags if file could be read, None else """
    def read_tags(self, file_name) :
        _ , extension = os.path.splitext(file_name)
        if extension == ".mp3":
            title, artist, encoded_by = self._read_mp3(file_name)
        else:
            #Extension not supported | Should never happen
            return (None, None, None)
        return title, artist, encoded_by

    """updates music file tags according to track object
        @return 0 if all went well, 1 if file was moved, 2 if file was un-editable
    """
    def update_tags(self, file_name, image_name, track):
        # 0 remove_image - 0
        # 1 move_image   - 0
        # 2 no_image     - 0
        # 3 file_was_moved - 2
        # 4 file_un-editable - 1
        action = 2
        _ , extension = os.path.splitext(file_name)
        if extension == ".mp3":

            action = self._write_mp3(file_name, image_name, track)
        else:
            #Should never happen
            if (image_name != ""):
                action = 0 # removing image
            else :
                action = 2
        
        if action == 0 :
            # removing image from folder
            os.remove(image_name)
    

        return self.state[action]

    """ -----------------------------------------------
        --------------- Private methods ---------------
        ----------------------------------------------- 
    """

    def _write_mp3(self, file_name, image_name, track):
        ret = 2 # no image
        # modifying the tags
        tag = eyed3.id3.tag.Tag()
        if tag.parse(fileobj = file_name):
            tag.title = track['name']
            tag.artist = track['artists'][0]['name']
            tag.genre = track['genre']
            tag.album = track['album']['name']
            tag.album_artist = track['artists'][0]['name']
            tag.track_num = (track['track_number'],track['album']['total_tracks'])
            tag.disc_num = (track['disc_number'], None)
            tag.recording_date = eyed3.core.Date.parse(track['album']['release_date'])

            try:
                if track['lyrics'] != "":
                    tag.lyrics.set("""{}""".format(track['lyrics']['text']))
            except KeyError:  # infos not found or not searched
                pass

            try:
                tag.bpm = track['bpm']
            except KeyError:  # infos not found or not searched
                pass

            try:
                tag.publisher = track['album']['label']
                tag.copyright = track['album']['copyright']
            except KeyError:  # infos not found or not searched
                pass

            if self.add_signature:
                tag.encoded_by = self.signature  # Program signature

            # works but no way to get info
            # tag.composer = ""

            # doesn't work and no easy way to get info
            # tag.artist_origin = "France" 

            # image
            if (image_name != ""):
                if self.store_image_in_file:
                    # read image into memory
                    imagedata = open(image_name, "rb").read()

                    # deleting previous artwork if present
                    for i in range(0, len(tag.images)):
                        tag.images.remove(tag.images[i].description)

                    # append image to tags
                    tag.images.set(3, imagedata, "image/jpeg",
                                   description = image_name)

                    tag.save(encoding="utf-8")
                    ret = 0

                else:
                    ret = 1  
            else :
                ret = 2

        tag.save(encoding="utf-8")
        return ret

    def _read_mp3(self, file_name):
        eyed3.load(file_name)  # creating object
        tag = eyed3.id3.tag.Tag()
        tag.parse(fileobj=file_name)

        return (tag.title, tag.artist, tag.encoded_by)

