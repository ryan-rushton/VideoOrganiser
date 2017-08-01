import re
import shutil
import os
import logging
from .models import TvShow, Movie, Genre
from .config import BASE_DIR_FILES, ALLOWED_EXTENSIONS, PENDING_GENRE_DIR


logger = logging.getLogger(__name__)


def recursive_extract_files(input_dir_path):
    """
    Recursively get the file paths from a directory
    :param input_dir_path: string, a dir path
    :return: [string], a list of file paths
    """
    rtn = []

    # Check if input_dir_path is actually a dir
    if os.path.isdir(input_dir_path):

        for item in os.listdir(input_dir_path):
            item_path = os.path.join(input_dir_path, item)

            # If an item in dir is a file and not hidden append to rtn
            if not item.startswith('.') and os.path.isfile(item_path):
                rtn.append(item_path)

            # If an item in dir is a dir and not hidden recurse and concatenate return with rtn
            elif not item.startswith('.') and os.path.isdir(item_path):
                rtn += recursive_extract_files(item_path)
    else:
        logger.error(f'Error: Not a directory: {input_dir_path}')
    return rtn


def remove_empty_dirs(input_dir_path):
    """
    This recursively removes empty directories from a  path. Hidden files are considered non existent.
    It does not delete the initial directory.
    :param input_dir_path: string, a path
    :return: Bool, None
    """

    # TODO make this friendly for windows systems

    # has_file is used to indicate if non hidden files were found
    has_files = False

    if os.path.isdir(input_dir_path):

        # Iterate though the dir
        for item in os.listdir(input_dir_path):
            item_path = os.path.join(input_dir_path, item)

            # When a non-hidden dir is found recurse on dir then delete if empty
            if not item.startswith('.') and os.path.isdir(item_path):
                if remove_empty_dirs(item_path):
                    os.rmdir(item_path)
                    logger.info(f'Deleted: {item_path}')
                else:
                    has_files = True

            # When a non-hidden file is found set has_files to True
            elif not item.startswith('.') and os.path.isfile(item_path):
                has_files = True

            # Case when a hidden file is found (osx and linux)
            elif item.startswith('.') and os.path.isfile(item_path):
                os.remove(item_path)
                logger.info(f'Deleted: {item_path}')

        # Return True if the dir is empty and False if not
        if has_files:
            return False
        else:
            return True

    else:
        logger.error(f'Error: Not a directory: {input_dir_path}')

    return None


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
    genre_obj = Genre.objects.filter(genre=genre)[0]
    file_name = os.path.split(media_file_path)[1]
    movie_dir = os.path.join(BASE_DIR_FILES, 'Movies')
    genre_dir = os.path.join(movie_dir, genre)

    # Create the required dirs if they don't exist
    if not os.path.isdir(genre_dir):
        try:
            os.makedirs(genre_dir)
            logger.info(f'Directory created: {movie_dir}')
        except OSError:
            logger.error(f'Error: Directory already exists: {movie_dir}')
        except:
            logger.error(f'Error: Could not be created, unknown error: {movie_dir}')

    # Move the file and add/modify an entry to the database
    try:
        shutil.move(media_file_path, os.path.join(genre_dir, file_name))
        logger.info(f'Move successful: {file_name} to {genre_dir}')
        try:
            if Movie.objects.filter(title=file_name).count() == 0:
                Movie(title=file_name, genre=genre_obj).save()
                logger.info(f'Database save successful: {file_name} with genre {genre}')
            else:
                entry = Movie.objects.filter(title=file_name)[0]
                entry.genre = genre_obj
                entry.save()
                logger.info(f'Database modification successful: {file_name} modified genre to {genre}')
            return True
        except:
            logger.error(f'Error: Cannot add or modify {file_name} in database')
    except:
        logger.error(f'Error: Move failed: {file_name} to {genre_dir}')


def move_new_tv_show(media_file_path, genre):
    """
    Move a TV show that is not already in the database
    :param media_file_path: string
    :param genre: string
    :return: True
    """

    # Get the Genre object and required dir paths
    try:
        genre_obj = Genre.objects.filter(genre=genre)[0]
    except IndexError:
        logger.error(f'IndexError: Could not get genre {genre} from database')
        return None
    file_name = os.path.split(media_file_path)[1]
    title, season, episode = get_file_details(file_name)
    tv_path = os.path.join(BASE_DIR_FILES, 'TV Shows')
    genre_path = os.path.join(tv_path, genre)
    title_path = os.path.join(genre_path, title)
    season_path = os.path.join(title_path, season)

    # Create the required dirs if they don't exist
    if not os.path.isdir(season_path):
        try:
            os.makedirs(season_path)
            logger.info(f'Directory created: {season_path}')
        except OSError:
            logger.error(f'OSError: Directory already exists: {season_path}')
        except:
            logger.error(f'Error: Could not be created, unknown error: {season_path}')

    # Move the file and add/modify an entry to the database
    try:
        shutil.move(media_file_path, os.path.join(season_path, file_name))
        logger.info(f'Move successful: {file_name} to {season_path}')
        try:
            TvShow(title=title, seasons=int(season[1:]), path=title_path, genre=genre_obj).save()
            logger.info(f'Database save successful: {title}, {season[1:]}, {title_path}, {genre}')
            return True
        except:
            logger.error(f'Error: Could not add to database: {title}, {season[1:]}, {title_path}, {genre}')
    except:
        logger.error(f'Error: Move failed: {file_name} to {season_path}')

    return None


def move_existing_tv_show(media_file_path, details=None):
    """
    Move a show that is existing the in the database
    :param media_file_path: string
    :param details: (string, string, string) (expected from get_file_details())
    :return: Bool
    """
    try:
        file_name = os.path.split(media_file_path)[1]
    except:
        logger.error(f'Error: Not a file system path: {media_file_path}')
        return None
    if details is None:
        details = get_file_details(file_name)
    if details is not None:
        title, season, episode = details
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
    try:
        file_name = os.path.split(media_file_path)[1]
    except:
        logger.error(f'Error: Not a file system path: {media_file_path}')
        return None

    details = get_file_details(file_name)

    # Check to see if this is a TV show
    if details is not None:

        # Attempt to move the show as if it was an existing show
        if move_existing_tv_show(media_file_path, details=details):
            return None

        # If the show is brand new return  name, season, episode
        else:
            dst = os.path.join(PENDING_GENRE_DIR, file_name)
            tmp = shutil.move(media_file_path, dst)
            if tmp == dst:
                logger.info(f'Move successful: {media_file_path} to {dst}')
                return details
            else:
                logger.error(f'Error: Move failed: {media_file_path} to {dst}')

    # return the media file path in the case of a movie
    else:
        dst = os.path.join(PENDING_GENRE_DIR, file_name)
        tmp = shutil.move(media_file_path, dst)
        if tmp == dst:
            logger.info(f'Move successful: {media_file_path} to {dst}')
            return media_file_path
        else:
            logger.error(f'Error: Move failed: {media_file_path} to {dst}')

    return None


def change_genre(title, new_genre):
    """
    Function to change the genre of a media file, both in db and in file system
    :param title: string (title from TvShow or Movie object)
    :param new_genre: string (genre from Genre object)
    :return: string or None
    """
    # Change the genre of a TvShow
    if TvShow.objects.filter(title=title).count() > 0:
        tv_show = TvShow.objects.filter(title=title)[0]

        # Get current tvshow path
        tv_show_path = tv_show.path

        # Get desired tvshow path
        tv_path = os.path.join(BASE_DIR_FILES, 'TV Shows')
        genre_path = os.path.join(tv_path, new_genre)
        dst = os.path.join(genre_path, title)

        # Move tvshow and update database
        tmp = shutil.move(tv_show_path, dst)
        if tmp == dst:
            logger.info(f'Move successful: {tv_show_path} to {dst}')
            if Genre.objects.filter(genre=new_genre).count() > 0:
                new_genre_obj = Genre.objects.filter(genre=new_genre)[0]
                tv_show.genre = new_genre_obj
                tv_show.path = dst
                tv_show.save()
                logger.info(f'Model update successful: {tv_show.title}, {tv_show.seasons}, {tv_show.path}, '
                            f'{tv_show.genre.genre}')
                return title
            else:
                logger.warning(f'Warning: Genre does not exist: {new_genre}')
        else:
            logger.error(f'Error: Move failed: {tv_show_path} to {dst}')

    # Change genre of a Movie
    elif Movie.objects.filter(title=title).count() > 0:
        movie = Movie.objects.filter(title=title)[0]
        old_genre = movie.genre.genre
        movie_dir = os.path.join(BASE_DIR_FILES, 'Movies')

        # Get current movie location
        old_genre_dir = os.path.join(movie_dir, old_genre)
        old_movie_path = os.path.join(old_genre_dir, title)

        move_movie(old_movie_path, new_genre)

    return None
