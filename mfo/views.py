from django.shortcuts import render, redirect
import os
import subprocess
import sys
import logging
import shutil
from django.http import JsonResponse
from .config import BASE_DIR_FILES, UPLOAD_DIR, WATCHED_DIR, PENDING_GENRE_DIR
from .forms import UploadForm, SelectGenre
from .file_managers import get_file_details, move_movie, move_new_tv_show, move_existing_tv_show, \
    recursive_extract_files, remove_empty_dirs

# ---------------------------------------------------------------------------------------------------------------------
# Below are functions that are helpers for views or ajax calls


logger = logging.getLogger(__name__)


def handle_uploaded_file(uploaded_files):
    """
    This is used to upload files to a folder that is being watched for changes.
    :param uploaded_files: [file]
    :return: None
    """
    for f in uploaded_files:
        with open(os.path.join(UPLOAD_DIR, f.name), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        src = os.path.join(UPLOAD_DIR, f.name)
        dst = os.path.join(WATCHED_DIR, f.name)
        result = shutil.move(src, dst)
        if result == dst:
            logger.info(f'Move successful: {src} tp {dst}')
        else:
            logger.error(f'Error: Move failed: {src} tp {dst}')


# ---------------------------------------------------------------------------------------------------------------------
# Create your views here.


# ---------------------------------------------------------------------------------------------------------------------
# Ajax functions


def play_vlc(request):
    """
    Function to play a video from the web interface in vlc on mac. Only works if VideoOrganiser is run locally
    :param request: request object
    :return: response object
    """
    video_path = request.GET.get('video_path')
    data = {}
    if sys.platform == 'darwin':
        subprocess.Popen([os.path.join('/Applications', 'VLC.app', 'Contents', 'MacOS', 'VLC'), video_path])
        logger.info('VLC app opened on server')
    return JsonResponse(data)


# This is used to store the filename passed to javascript when creating the modal form to get a genre
file_path_to_js = None


def get_genre(request):
    """
    The backend for creating a modal to select a genre for movies and tv shows that have not been assigned one.
    :param request: request object
    :return: response object
    """
    global file_path_to_js

    # Get a sorted directory of non hidden files
    real_dir = recursive_extract_files(PENDING_GENRE_DIR)
    real_dir.sort()

    # In the event that the request was POST
    if request.method == 'POST':
        genre_form = SelectGenre(request.POST)

        # If the form is valid get the genre from the form
        if genre_form.is_valid():
            genre = request.POST['genre']

            # Get the file name, details and move file
            file_name = os.path.split(file_path_to_js)[1]
            tmp = get_file_details(file_name)

            logger.info(f'Got genre {genre} for {file_name}')

            if tmp is None:
                move_movie(file_path_to_js, genre)
            else:
                move_new_tv_show(file_path_to_js, genre)

            # Move any other tv shows the belong to the series just entered.
            for item in real_dir:
                if item != file_path_to_js:
                    move_existing_tv_show(os.path.join(PENDING_GENRE_DIR, item))

            # Delete any dirs that are empty
            remove_empty_dirs(PENDING_GENRE_DIR)

            data = {'contains_data': False}
            logger.info(f'Sending JSON ajax information: {data}')
            return JsonResponse(data)

    # In the event that it was not a POST event send the details so a form and modal can be created
    # Note that the dir must not have been modified in 2 seconds
    else:
        if len(real_dir) > 0 and os.path.getmtime(PENDING_GENRE_DIR) > 2:
            genre_form = SelectGenre()
            file_path_to_js = real_dir[0]
            file_name = os.path.split(file_path_to_js)[1]
            data = {
                'contains_data': True,
                'genre_form': genre_form.as_p(),
                'file_name': file_name
            }
            logger.info(f'Sending JSON ajax information: {data}')
            return JsonResponse(data)
    data = {'contains_data': False}
    logger.info(f'Sending JSON ajax information: {data}')
    return JsonResponse(data)


def load_file_system(request):
    """
    Gets the file system structure for the index page.
    :param request: request object
    :return: response object
    """
    current_dir = request.GET.get('new_dir')
    child_dirs = []
    child_files = []
    if current_dir == 'home':
        current_dir = BASE_DIR_FILES
    elif current_dir == 'undefined':
        try:
            current_dir = request.session['current_dir']
        except KeyError:
            current_dir = BASE_DIR_FILES
    if current_dir != BASE_DIR_FILES:
        child_dirs.append(('..', os.path.split(current_dir)[0]))
    request.session['current_dir'] = current_dir
    tmp = os.listdir(current_dir)
    for item in tmp:
        if not item.startswith('.') and os.path.isdir(os.path.join(current_dir, item)):
            child_dirs.append((item, os.path.join(current_dir, item)))
        elif not item.startswith('.'):
            child_files.append((item, os.path.join(current_dir, item)))
    data = {
        'current_dir': current_dir,
        'child_dirs': child_dirs,
        'child_files': child_files
    }
    logger.info(f'Sending JSON ajax information: {data}')
    return JsonResponse(data)


# ---------------------------------------------------------------------------------------------------------------------
# Views that render the templates


def index(request):
    """
    The main index view.
    :param request: request object
    :return: response object
    """

    # Sets up the Upload form
    if request.method == 'POST':
        upload_form = UploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            file_list = request.FILES.getlist('choose_files')
            logger.info(f'Files uploaded: {file_list}')
            handle_uploaded_file(file_list)
    else:
        upload_form = UploadForm()
    return render(request, 'mfo/index.html', {
        'upload_form': upload_form
    })


def genre_view(request):
    """
    A view to allow deleting media and alternating genres
    :param request: request object
    :return: response object
    """
    # Sets up the Upload form
    if request.method == 'POST':
        upload_form = UploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            handle_uploaded_file(request.FILES.getlist('uploaded_files'))
    else:
        upload_form = UploadForm()
    return render(request, 'mfo/genre_view.html', {
        'upload_form': upload_form
    })
