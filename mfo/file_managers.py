import re
import shutil
import os
import time
from multiprocessing import Process
from .models import TvShow, Movie, Genre
from .config import BASE_DIR_FILES, WATCHED_DIR, ALLOWED_EXTENSIONS, PENDING_GENRE_DIR


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


def move_movie(media_file_path, genre):
    """
    Moves a movie to the required genre directory
    :param media_file_path: string
    :param genre: string
    :return: True
    """
    genre = Genre.objects.filter(genre=genre)[0]
    file_name = os.path.split(media_file_path)[1]
    movie_dir = os.path.join(BASE_DIR_FILES, 'Movies')
    genre_dir = os.path.join(movie_dir, genre)
    if not os.path.isdir(movie_dir):
        os.mkdir(movie_dir)
    if not os.path.isdir(genre_dir):
        os.mkdir(genre_dir)
    shutil.move(media_file_path, os.path.join(genre_dir, file_name))
    if Movie.objects.filter(title=file_name).count() == 0:
        Movie(title=file_name, genre=genre).save()
    else:
        entry = Movie.objects.filter(title=file_name)[0]
        entry.update(genre=genre)
    return True


def move_new_tv_show(media_file_path, genre):
    """
    Move a TV show that is not already in the database
    :param media_file_path: string
    :param genre: string
    :return: True
    """
    genre_obj = Genre.objects.filter(genre=genre)[0]
    file_name = os.path.split(media_file_path)[1]
    title, season, episode = get_file_details(file_name)
    tv_path = os.path.join(BASE_DIR_FILES, 'TV Shows')
    genre_path = os.path.join(tv_path, genre)
    title_path = os.path.join(genre_path, title)
    season_path = os.path.join(title_path, season)
    if not os.path.isdir(tv_path):
        os.mkdir(tv_path)
    if not os.path.isdir(genre_path):
        os.mkdir(genre_path)
    if not os.path.isdir(title_path):
        os.mkdir(title_path)
    if not os.path.isdir(season_path):
        os.mkdir(season_path)
    print(os.path.join(season_path, file_name))
    shutil.move(media_file_path, os.path.join(season_path, file_name))
    TvShow(title=title, seasons=int(season[1:]), path=title_path, genre=genre_obj).save()
    return True


def move_existing_tv_show(media_file_path):
    """
    Move a show that is existing the in the database
    :param media_file_path: string
    :return: Bool
    """
    file_name = os.path.split(media_file_path)[1]
    tmp = get_file_details(file_name)
    if tmp is not None:
        title, season, episode = tmp
        db_entry = TvShow.objects.filter(title=title)

        # Check to see if the show already exists
        if db_entry.count() > 0:
            db_entry = db_entry[0]
            base_path = db_entry.path
            season_path = os.path.join(base_path, season)
            new_file_path = os.path.join(season_path, file_name)

            # Check to see if the season dir exists
            if not os.path.isdir(season_path):
                os.mkdir(season_path)
                if int(db_entry.seasons) < int(season[1:]):
                    db_entry.update(seasons=int(season[1:]))

            shutil.move(media_file_path, new_file_path)
            return True
    return False


def blind_media_move(media_file_path):
    """
    Moves the file if it is a TV Show. Returns the input if a movie, or a 3-tuple if a new TV show or None if
    successsful
    :param media_file_path: string
    :return: None or string or (string, string, string)
    """
    file_name = os.path.split(media_file_path)[1]
    tmp = get_file_details(file_name)

    # Check to see if this is a TV show
    if tmp is not None:
        title, season, episode = tmp
        # Attempt to move the show as if it was a new show
        if move_existing_tv_show(media_file_path):
            pass

        # If the show is brand new return  name, season, episode
        else:
            shutil.move(media_file_path, os.path.join(PENDING_GENRE_DIR, file_name))
            return title, season, episode

    # return the media file path in the case of a movie
    else:
        shutil.move(media_file_path, os.path.join(PENDING_GENRE_DIR, file_name))
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
                    if os.path.getmtime(item_path) > 5:
                        # Attempt to move the file as if it were a known TV show
                        move_return = blind_media_move(item_path)

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
