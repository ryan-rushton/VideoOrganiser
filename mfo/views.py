from django.shortcuts import render
import os
from django.http import JsonResponse
from .config import BASE_DIR_FILES, UPLOAD_DIR
from .forms import UploadForm


# ---------------------------------------------------------------------------------------------------------------------
# Below are functions that are one off's for views or ajax calls


def handle_uploaded_file(uploaded_files):
    """
    This is used to upload files to a folder that is being watched for changes.
    :param f: file
    :return: None
    """
    for f in uploaded_files:
        with open(os.path.join(UPLOAD_DIR, f.name), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
    return None

# ---------------------------------------------------------------------------------------------------------------------
# Create your views here.


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


def index(request):
    """
    The main index view.
    :param request: request object
    :return: response object
    """
    if request.method == 'POST':
        upload_form = UploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            handle_uploaded_file(request.FILES.getlist('uploaded_files'))

    else:
        upload_form = UploadForm()
    return render(request, 'mfo/index.html', {
        'upload_form': upload_form
    })
