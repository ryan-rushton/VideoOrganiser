from django.shortcuts import render
import os
from django.http import HttpResponse
from .config import base_dir

# Create your views here.


def index(request):
    current_dir = request.GET.get('new_dir')
    print(current_dir)
    child_dirs = []
    child_files = []
    if current_dir is None:
        current_dir = base_dir
        tmp = os.listdir(current_dir)
        for item in tmp:
            if item[0] != '.' and os.path.isdir(os.path.join(current_dir, item)):
                child_dirs.append((item, os.path.join(current_dir, item)))
            elif item[0] != '.':
                child_files.append((item, os.path.join(current_dir, item)))
    return render(request, 'mfo/index.html', {
        'current_dir': current_dir,
        'child_dirs': child_dirs,
        'child_files': child_files
    })
