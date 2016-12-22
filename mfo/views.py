from django.shortcuts import render
import os
import subprocess
import sys
from shutil import move
from django.http import JsonResponse
from .config import BASE_DIR_FILES, UPLOAD_DIR, WATCHED_DIR, PENDING_GENRE_DIR
from .forms import UploadForm, SelectGenre
from .file_managers import get_file_details, move_movie, move_new_tv_show, move_existing_tv_show, \
    recursive_extract_files, remove_empty_dirs

# ---------------------------------------------------------------------------------------------------------------------
# Below are functions that are one off's for views or ajax calls


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
        move(os.path.join(UPLOAD_DIR, f.name), os.path.join(WATCHED_DIR, f.name))


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
    return JsonResponse(data)


def get_genre(request):
    """
    The backend for creating a modal to select a genre for movies and tv shows that have not been assigned one.
    :param request: request object
    :return: response object
    """
    # Get a sorted directory of non hidden files
    real_dir = recursive_extract_files(PENDING_GENRE_DIR)
    real_dir.sort()

    # In the event that the request was POST
    if request.method == 'POST':
        genre_form = SelectGenre(request.POST)

        # If the form is valid get the genre from the form
        if genre_form.is_valid():
            genre = request.POST['genre']

            # From the files in the folder get the first non hidden from an alphabetical ordering
            file_name = os.path.split(real_dir[0])[1]

            # Move the media file
            media_file_path = real_dir[0]
            tmp = get_file_details(file_name)
            if tmp is None:
                move_movie(media_file_path, genre)
            else:
                move_new_tv_show(media_file_path, genre)

            # Move any other tv shows the belong to the series just entered.
            for item in real_dir:
                if item is not media_file_path:
                    move_existing_tv_show(os.path.join(PENDING_GENRE_DIR, item))

            # Delete any dirs that are empty
            remove_empty_dirs(PENDING_GENRE_DIR)

            # Create the upload form and return the index to reload the main page.
            upload_form = UploadForm()
            return render(request, 'mfo/index.html', {
                'upload_form': upload_form
            })

    # In the event that it was not a POST event send the details so a form and modal can be created
    else:
        if len(real_dir) > 0:
            genre_form = SelectGenre()
            file_name = os.path.split(real_dir[0])[1]
            data = {
                'contains_data': True,
                'genre_form': genre_form.as_p(),
                'file_name': file_name
            }
            return JsonResponse(data)

    return JsonResponse({'contains_data': False})


def load_file_system(request):
    """
    Gets the file system structure for the index page.
    :param request: request object
    :return: response object
    """
    current_dir = request.GET.get('new_dir')
    child_dirs = []
    child_files = []
    if current_dir is None or current_dir == 'undefined' or current_dir == BASE_DIR_FILES:
        current_dir = BASE_DIR_FILES
    else:
        child_dirs.append(('..', os.path.split(current_dir)[0]))
    tmp = os.listdir(current_dir)
    for item in tmp:
        if item[0] != '.' and os.path.isdir(os.path.join(current_dir, item)):
            child_dirs.append((item, os.path.join(current_dir, item)))
        elif item[0] != '.':
            child_files.append((item, os.path.join(current_dir, item)))
    data = {
        'current_dir': current_dir,
        'child_dirs': child_dirs,
        'child_files': child_files
    }
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
            handle_uploaded_file(request.FILES.getlist('uploaded_files'))
    else:
        upload_form = UploadForm()
    return render(request, 'mfo/index.html', {
        'upload_form': upload_form
    })


def map_genre(request):
    """

    :param request:
    :return:
    """
    # Sets up the Upload form
    if request.method == 'POST':
        upload_form = UploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            handle_uploaded_file(request.FILES.getlist('uploaded_files'))
    else:
        upload_form = UploadForm()
    return render(request, 'mfo/map_genre.html', {
        'upload_form': upload_form
    })
