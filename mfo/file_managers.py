import re
import shutil
import os
from .models import TvShow, Movie, Genre
from .config import BASE_DIR_FILES, ALLOWED_EXTENSIONS, PENDING_GENRE_DIR


def recursive_extract_files(input_dir_path):
    """
    Recursively get the files from a directory
    :param input_dir_path: string, a dir path
    :return: [string], a list of file paths
    """
    rtn = []
    for item in os.listdir(input_dir_path):
        item_path = os.path.join(input_dir_path, item)
        if not item.startswith('.') and os.path.isfile(item_path):
            rtn.append(item_path)
        elif not item.startswith('.') and os.path.isdir(item_path):
            rtn += recursive_extract_files(item_path)
    return rtn


def remove_empty_dirs(input_dir_path):
    """
    This recursively removes empty directories from a  path. Hidden files are considered non existent.
    It does not delete the initial directory.
    :param input_dir_path: string, a path
    :return: Bool
    """

    # TODO make this friendly for windows systems

    # has_file is used to indicate if non hidden files were found
    has_files = False

    # Iterate though the dir
    for item in os.listdir(input_dir_path):
        item_path = os.path.join(input_dir_path, item)

        # When a non-hidden dir is found recurse on dir then delete if empty
        if not item.startswith('.') and os.path.isdir(item_path):
            if remove_empty_dirs(item_path):
                os.rmdir(item_path)
            else:
                has_files = True

        # When a non-hidden file is found set has_files to True
        elif not item.startswith('.') and os.path.isfile(item_path):
            has_files = True

        # Case when a hidden file is found (osx and linux)
        elif item.startswith('.') and os.path.isfile(item_path):
            os.remove(item_path)

    # Return True if the dir is empty and False if not
    if has_files:
        return False
    else:
        return True


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
    :param filename: string
    :return: (string, string, string), strings of name, season, episode or None
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
    :param media_file_path: string, a path
    :param genre: string
    :return: True
    """

    # Get the Genre object and required dir paths
    genre = Genre.objects.filter(genre=genre)[0]
    file_name = os.path.split(media_file_path)[1]
    movie_dir = os.path.join(BASE_DIR_FILES, 'Movies')
    genre_dir = os.path.join(movie_dir, genre)

    # Create the required dirs if they don't exist
    if not os.path.isdir(movie_dir):
        os.mkdir(movie_dir)
    if not os.path.isdir(genre_dir):
        os.mkdir(genre_dir)

    # Move the file and add/modify an entry to the database
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

    # Get the Genre object and required dir paths
    genre_obj = Genre.objects.filter(genre=genre)[0]
    file_name = os.path.split(media_file_path)[1]
    title, season, episode = get_file_details(file_name)
    tv_path = os.path.join(BASE_DIR_FILES, 'TV Shows')
    genre_path = os.path.join(tv_path, genre)
    title_path = os.path.join(genre_path, title)
    season_path = os.path.join(title_path, season)

    # Create the required dirs if they don't exist
    if not os.path.isdir(tv_path):
        os.mkdir(tv_path)
    if not os.path.isdir(genre_path):
        os.mkdir(genre_path)
    if not os.path.isdir(title_path):
        os.mkdir(title_path)
    if not os.path.isdir(season_path):
        os.mkdir(season_path)

    # Move the file and add/modify an entry to the database
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
            genre = db_entry.genre.genre
            move_new_tv_show(media_file_path, genre)
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
            return None

        # If the show is brand new return  name, season, episode
        else:
            shutil.move(media_file_path, os.path.join(PENDING_GENRE_DIR, file_name))
            return title, season, episode

    # return the media file path in the case of a movie
    else:
        shutil.move(media_file_path, os.path.join(PENDING_GENRE_DIR, file_name))
        return media_file_path
