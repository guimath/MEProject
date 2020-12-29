# for file modification
import os
import eyed3  # to parse mp3 files
import json   # to parse config file
import shutil  # to move file
import stat   # to change read/write file status
import os


class Tagger:
    def __init__(self, params, path):
        self.debug = params['debug']
        self.store_image_in_file =  params['store_image_in_file']
        self.add_signature = params['add_signature']
        self.path = path
        self.folder_path = path + params['folder_name']

        eyed3.log.setLevel("ERROR")  # hides errors from eyed3 package

    def _mp3(self, file_path, image_name, image_path, track):
        ret = 2 # no image
        # modifing the tags
        tag = eyed3.id3.tag.Tag()
        if tag.parse(fileobj = file_path):
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
                    tag.lyrics.set("""{}""".format(track['lyrics']))
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

            # doesn't work
            #  # doenst work + no easy way to get info
            # tag.artist_origin = "France" # doesent work + no easy way to get info

            # image
            if (image_name != ""):
                if self.store_image_in_file:
                    # read image into memory
                    imagedata = open(image_path, "rb").read()

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

        tag.save(encoding="utf-8")
        return ret

    def update_file(self, file_path, image_name, track):
        action = 2
        image_path =  self.path + image_name
        tmp, extension = os.path.splitext(file_path)
        if extension == ".mp3":
            action = self._mp3(file_path, image_name, image_path, track)
        else:
            #Should never happen
            ret = 0
            if (self.image_name != ""):
                action = 0 # removing image
            else :
                action = 2
        
        if action == 0 :
            # removing image from folder
            os.remove(image_path)
        
        elif action == 1 :
            # moving image in directory (or deleting if already present)
            if not os.path.exists(self.folder_path + os.path.sep + image_name):
                # place in folder
                shutil.move(image_path, self.folder_path)
            else:
                os.remove(image_path)
        
        return 0


        # remove_image - 0
        # move_image   - 0
        # all_is_good  - 0
        # file_was_moved - 2
        # file_uneditable - 1