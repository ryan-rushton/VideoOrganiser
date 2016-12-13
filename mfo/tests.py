from django.test import TestCase
from .file_managers import get_file_details, check_extension
from .config import ALLOWED_EXTENSIONS


class TestFileHandler(TestCase):
    def test_get_file_details(self):
        filename1 = 'some.tv.show.s01e01.mp4'
        filename2 = 'some.tv.show.101.mp4'
        filename3 = 'some.movie.mp4'
        filename4 = 'some.tv.show.S01E01.mp4'
        self.assertEqual(get_file_details(filename1), ('some.tv.show', 'S01', 'E01'))
        self.assertEqual(get_file_details(filename2), None)
        self.assertEqual(get_file_details(filename3), None)
        self.assertEqual(get_file_details(filename4), ('some.tv.show', 'S01', 'E01'))


class TestCheckExtension(TestCase):
    def test_check_extension(self):
        for ext in ALLOWED_EXTENSIONS:
            self.assertTrue(check_extension('blah.' + ext))
