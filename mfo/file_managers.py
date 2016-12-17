import re
import shutil
import os
import time
from multiprocessing import Process
from .models import TvShow
from .config import BASE_DIR_FILES, WATCHED_DIR, IS_WATCHING, ALLOWED_EXTENSIONS


def check_extension(media_file):
    """
    Check to see if a file has an aloud extension
    :param media_file: string
    :return: Bool
    """
    tmp = media_file.split('.')
    if len(tmp) > 0 and tmp[-1] in ALLOWED_EXTENSIONS:
            return True
    return False


def get_file_details(filename):
    """
    Gets the season format and number from a filename
    :param filename: the filename string
    :return: strings of name, season, episode or None
    """

    file_list = filename.split('.')
    for i in range(len(file_list)):
        match_obj = re.match(r'([sS]\d+)([eE]\d+)', file_list[i])
        if match_obj:
            season = match_obj.group(1).upper()
            episode = match_obj.group(2).upper()
            name = '.'.join(file_list[:i])
            return name, season, episode
    return None


def move_tv_season(media_file_path):
    """
    Moves the file if it is a TV Show. Returns the input if a movie, or a 3-tuple if a new TV show or None if
    successsful
    :param media_file_path: string
    :return: None or string or (string, string, string)
    """
    tmp = get_file_details(media_file_path)

    # Check to see if this is a TV show
    if tmp is not None:
        name, season, episode = tmp
        db_entry = TvShow.objects.filter(name=name)

        # Check to see if the show already exists
        if db_entry.count() > 0:
            db_entry = db_entry[0]
            base_path = db_entry.path
            season_path = os.path.join(base_path, season)
            new_file_path = os.path.join(season_path, os.path.split(media_file_path)[1])

            # Check to see if the season dir exists
            if os.path.isdir(season_path):
                shutil.move(media_file_path, new_file_path)
                return None

            # Make season dir if it doesn't exist and update the seasons
            else:
                os.mkdir(season_path)
                db_entry.update(seasons=int(season))
                shutil.move(media_file_path, new_file_path)

        # If the show is brand new return  name, season, episode
        else:
            return name, season, episode

    # return the media file path in the case of a movie
    else:
        return media_file_path

    return False


class Watcher(Process):
    """
    This class extends the Process class and watches a folder for new media files
    """
    # TODO Finish this class off

    def __init__(self, q):
        Process.__init__(self)
        self.watched_dir = WATCHED_DIR
        self.q = q
        self.running = True

    def run(self):
        """
        This is the run method for the directory watcher. It looks for items in the WATCHED_DIR directory and handles
        them depending on what type of file they are.
        """
        # TODO a pop-up needs to be called to get a genre when the file is a new TV show or a movie
        while self.running:

            # Get all items in WATCHED_DIR
            media_files = os.listdir(self.watched_dir)
            if len(media_files) > 0:
                for item in media_files:
                    item_path = os.path.join(self.watched_dir, item)

                    # Attempt to move the file as if it were a known TV show
                    move_return = move_tv_season(item_path)

                    # This returns none if successful
                    if move_return is not None:

                        # The case it is a movie or doesnt follow the expected TV show format
                        if move_return == item_path:
                            pass

                        # The case that it is a new TV show, note this needs to be saved to the db
                        else:
                            name, season, episode = move_return

            if not self.q.empty():
                self.running = self.q.get()
            time.sleep(10)
