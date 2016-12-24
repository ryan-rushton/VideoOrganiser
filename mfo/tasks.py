import os
from VideoOrganiser.celery import app
from .config import WATCHED_DIR
from .file_managers import blind_media_move, remove_empty_dirs, recursive_extract_files


# This sets up a celery periodic task that runs the check_watched_dir as below
app.conf.beat_schedule['watch_dir'] = {
        'task': 'mfo.tasks.check_watched_dir',
        'schedule': 5.0
    }


@app.task
def check_watched_dir():
    """
    A celery task that runs and moves files in WATCHED_DIR via the blind_media_move function
    :return: None
    """
    media_files = recursive_extract_files(WATCHED_DIR)
    if len(media_files) > 0:
        for item in media_files:
            item_path = os.path.join(WATCHED_DIR, item)
            if os.path.getmtime(item_path) > 5:
                # Attempt to move the file as if it were a known TV show
                blind_media_move(item_path)
    return None
