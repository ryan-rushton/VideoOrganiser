from django.shortcuts import render, redirect
import os
from django.http import JsonResponse
from .config import BASE_DIR_FILES, WATCHED_DIR, UPLOAD_DIR
from .forms import UploadForm

# Create your views here.


def load_file_system(request):
    """
    Loads the file system for the page.
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


def handle_uploaded_file(f):
    with open(os.path.join(UPLOAD_DIR, f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print("%s uploaded" % str(f))


def index(request):
    if request.method == 'POST':
        upload_form = UploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            print('form valid')
            print(request.FILES['uploaded_file'])
            handle_uploaded_file(request.FILES['uploaded_file'])

        else:
            print('form not valid')

    else:
        upload_form = UploadForm()
    return render(request, 'mfo/index.html', {
        'upload_form': upload_form
    })
