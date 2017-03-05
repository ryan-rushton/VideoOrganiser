VideoOrganiser
------------------------------------------------------------------------

What is it?
------------------------------------------------------------------------
This is planned to be a Django webapp that sits on a home server and enables
video files to be uploaded to the server over the network. It will sort the
video file based on its type (movie or tv show), and further if it contains
a season and episode number and based on genre.

Licence
------------------------------------------------------------------------
MIT License

Copyright (c) 2016 Ryan Arthur Robert Rushton

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Installation
------------------------------------------------------------------------
First navigate into the VideoOrganiser main directory.

Install a virtual environment in the VideoOrganiser directory using
    'python3 -m venv virtual_env'

Install the required packages using "virtual_env/bin/pip install -r requirements.txt"

A message broker needs to be installed, this is set up for rabbitmq, please see
https://www.rabbitmq.com/ for installation instructions

Set the directories to be used by VideoOrganiser by setting the directories in
mfo.config.

If you wish to modify the genre's used add or remove instances in mfo.fixtures.initial_genre.json,
making sure to keep the same format.

Set up the database with

    "virtual_env/bin/python manage.py migrate"
    "virtual_env/bin/python manage.py makemigrations"
    "virtual_env/bin/python manage.py loaddata initial_genre.json"

How to run?
------------------------------------------------------------------------
Start a celery worker to continually check the watched directory with
    'virtual_env/bin/celery -A VideoOrganiser worker -B'

Finally start the web app with
    'virtual_env/bin/python manage.py runserver'
