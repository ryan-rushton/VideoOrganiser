import os
import shutil

from django.test import TestCase
from VideoOrganiser.settings import BASE_DIR
from .file_managers import get_file_details, check_extension, remove_empty_dirs, recursive_extract_files, move_movie, \
    move_new_tv_show, move_existing_tv_show, blind_media_move, change_genre
from .config import ALLOWED_EXTENSIONS, BASE_DIR_FILES, PENDING_GENRE_DIR
from .models import TvShow, Movie, Genre


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


class TestRecursiveExtractFiles(TestCase):
    def test_recursive_extract_files(self):
        # Create a dir for tests
        test_dir = os.path.join(BASE_DIR, 'mfo', 'test_dir')
        if not os.path.isdir(test_dir):
            os.mkdir(test_dir)

        # Create first dir, will not be empty
        dir_a_path = os.path.join(test_dir, 'dir_a')
        if not os.path.isdir(dir_a_path):
            os.mkdir(dir_a_path)

        # Create a 2 folder deep path to test recursive case
        dir_a2_path = os.path.join(dir_a_path, 'dir_a2')
        if not os.path.isdir(dir_a2_path):
            os.mkdir(dir_a2_path)

        # Create an initially empty dir
        dir_b_path = os.path.join(test_dir, 'dir_b')
        if not os.path.isdir(dir_b_path):
            os.mkdir(dir_b_path)

        # Create a file1
        file_path1 = os.path.join(dir_a_path, 'test_file1.txt')
        open(file_path1, 'w+').close()

        # Create a file2
        file_path2 = os.path.join(dir_a2_path, 'test_file2.txt')
        open(file_path2, 'w+').close()

        # Create a file3
        file_path3 = os.path.join(dir_b_path, 'test_file3.txt')
        open(file_path3, 'w+').close()

        rtn = recursive_extract_files(test_dir)
        self.assertTrue(file_path1 in rtn)
        self.assertTrue(file_path2 in rtn)
        self.assertTrue(file_path3 in rtn)

        # Remove test folder
        shutil.rmtree(test_dir)


class TestRemoveEmptyDirs(TestCase):
    def test_remove_empty_dirs(self):
        # Create a dir for tests
        test_dir = os.path.join(BASE_DIR, 'mfo', 'test_dir')
        if not os.path.isdir(test_dir):
            os.mkdir(test_dir)

        # Create first dir, will not be empty
        dir_a_path = os.path.join(test_dir, 'dir_a')
        if not os.path.isdir(dir_a_path):
            os.mkdir(dir_a_path)

        # Create a 2 folder deep path to test recursive case
        dir_a2_path = os.path.join(dir_a_path, 'dir_a2')
        if not os.path.isdir(dir_a2_path):
            os.mkdir(dir_a2_path)

        # Create an initially empty dir
        dir_b_path = os.path.join(test_dir, 'dir_b')
        if not os.path.isdir(dir_b_path):
            os.mkdir(dir_b_path)

        # Create a file
        file_path = os.path.join(dir_a2_path, 'test_file.txt')
        open(file_path, 'w+').close()

        # test that dir_b is deleted but file and dir_a aren't
        remove_empty_dirs(test_dir)
        self.assertTrue(os.path.isfile(file_path))
        self.assertTrue(os.path.isdir(dir_a_path))
        self.assertFalse(os.path.isdir(dir_b_path))

        # Remove the file and check recursive case
        os.remove(file_path)
        remove_empty_dirs(test_dir)
        self.assertFalse(os.path.isdir(dir_a_path))

        # Remove test folder
        shutil.rmtree(test_dir)


class TestMoveMovie(TestCase):
    def test_move_movie(self):
        # Create a dir for tests
        test_dir = os.path.join(BASE_DIR, 'mfo', 'test_dir')
        os.mkdir(test_dir)

        # Create Genre's specifically for testing
        genre_obj1 = Genre(genre='TestGenre1')
        genre_obj1.save()
        genre_path1 = os.path.join(BASE_DIR_FILES, 'Movies', 'TestGenre1')
        genre_obj2 = Genre(genre='TestGenre2')
        genre_obj2.save()
        genre_path2 = os.path.join(BASE_DIR_FILES, 'Movies', 'TestGenre2')

        # Create a test file
        file_path = os.path.join(test_dir, 'test.mp4')
        open(file_path, 'w+').close()

        # This is the case when the Movie does not initially exist
        move_movie(file_path, genre_obj1.genre)
        test_path1 = os.path.join(genre_path1, 'test.mp4')
        self.assertTrue(os.path.isfile(test_path1))
        self.assertTrue(Movie.objects.filter(title='test.mp4').count() == 1)

        # Case when it already exsits and its genre is being changed
        move_movie(test_path1, genre_obj2.genre)
        test_path2 = os.path.join(genre_path2, 'test.mp4')
        self.assertTrue(os.path.isfile(test_path2))
        self.assertFalse(os.path.isfile(test_path1))
        self.assertTrue(Movie.objects.filter(title='test.mp4').count() == 1)
        self.assertTrue(Movie.objects.filter(title='test.mp4')[0].genre == genre_obj2)

        # Clean up db
        Movie.objects.filter(title='test.mp4')[0].delete()
        genre_obj1.delete()
        genre_obj2.delete()

        # Remove test folder
        shutil.rmtree(test_dir)
        shutil.rmtree(genre_path1)
        shutil.rmtree(genre_path2)


class TestMoveNewTvShow(TestCase):
    def test_move_new_tv_show(self):
        # Create a dir for tests
        test_dir = os.path.join(BASE_DIR, 'mfo', 'test_dir')
        os.mkdir(test_dir)

        # Create Genre's specifically for testing
        genre_obj1 = Genre(genre='TestGenre1')
        genre_obj1.save()
        genre_path1 = os.path.join(BASE_DIR_FILES, 'TV Shows', 'TestGenre1')

        # Create a test file
        file_path = os.path.join(test_dir, 'test.s01e01.mp4')
        open(file_path, 'w+').close()

        move_new_tv_show(file_path, genre_obj1.genre)
        test_path1 = os.path.join(genre_path1, 'test', 'S01', 'test.s01e01.mp4')
        self.assertTrue(os.path.isfile(test_path1))
        self.assertTrue(TvShow.objects.filter(title='test').count() == 1)

        # Clean up db
        TvShow.objects.filter(title='test')[0].delete()
        genre_obj1.delete()

        # Remove test folder
        shutil.rmtree(test_dir)
        shutil.rmtree(genre_path1)


class TestMoveExistingTvShow(TestCase):
    def test_move_existing_tv_show(self):
        # Create a dir for tests
        test_dir = os.path.join(BASE_DIR, 'mfo', 'test_dir')
        os.mkdir(test_dir)

        # Create Genre's specifically for testing
        genre_obj1 = Genre(genre='TestGenre1')
        genre_obj1.save()
        genre_path1 = os.path.join(BASE_DIR_FILES, 'TV Shows', 'TestGenre1')

        # Create a test file
        file_path = os.path.join(test_dir, 'test.s01e01.mp4')
        open(file_path, 'w+').close()

        # Test that a new show has been added
        move_new_tv_show(file_path, genre_obj1.genre)
        test_path1 = os.path.join(genre_path1, 'test', 'S01', 'test.s01e01.mp4')
        self.assertTrue(os.path.isfile(test_path1))
        self.assertTrue(TvShow.objects.filter(title='test').count() == 1)

        # Create a second episode for s01
        file_path2 = os.path.join(test_dir, 'test.s01e02.mp4')
        open(file_path2, 'w+').close()

        # Test that second episode added
        move_existing_tv_show(file_path2)
        test_path2 = os.path.join(genre_path1, 'test', 'S01', 'test.s01e02.mp4')
        self.assertTrue(os.path.isfile(test_path2))
        self.assertTrue(TvShow.objects.filter(title='test').count() == 1)

        # Create a second season
        file_path3 = os.path.join(test_dir, 'test.s02e01.mp4')
        open(file_path3, 'w+').close()

        # Test that the new season is added and db updated
        move_existing_tv_show(file_path3)
        test_path3 = os.path.join(genre_path1, 'test', 'S02', 'test.s02e01.mp4')
        self.assertTrue(os.path.isfile(test_path3))
        self.assertTrue(TvShow.objects.filter(title='test').count() == 1)
        self.assertTrue(TvShow.objects.filter(title='test')[0].seasons == 2)

        # Clean up db
        TvShow.objects.filter(title='test')[0].delete()
        genre_obj1.delete()

        # Remove test folder
        shutil.rmtree(test_dir)
        shutil.rmtree(genre_path1)


class TestBlindMediaMove(TestCase):
    def test_blind_media_move(self):
        # Create a dir for tests
        test_dir = os.path.join(BASE_DIR, 'mfo', 'test_dir')
        os.mkdir(test_dir)

        # Create Genre's specifically for testing
        genre_obj1 = Genre(genre='TestGenre1')
        genre_obj1.save()
        genre_path1 = os.path.join(BASE_DIR_FILES, 'TV Shows', 'TestGenre1')

        # Create a test TV file
        file_name = 'test.s01e01.mp4'
        file_path = os.path.join(test_dir, file_name)
        open(file_path, 'w+').close()

        # Create a test Movie file
        file_name2 = 'somemovie.mp4'
        file_path2 = os.path.join(test_dir, file_name2)
        open(file_path2, 'w+').close()

        self.assertTrue(blind_media_move(file_path) == ('test', 'S01', 'E01'))
        self.assertTrue(blind_media_move(file_path2) == file_path2)
        self.assertTrue(os.path.isfile(os.path.join(PENDING_GENRE_DIR, file_name)))
        self.assertTrue(os.path.isfile(os.path.join(PENDING_GENRE_DIR, file_name2)))
        os.remove(os.path.join(PENDING_GENRE_DIR, file_name2))

        shutil.move(os.path.join(PENDING_GENRE_DIR, file_name), file_path)
        move_new_tv_show(file_path, genre=genre_obj1.genre)

        self.assertTrue(TvShow.objects.filter(title='test').count() == 1)

        # Create a test TV file
        file_path3 = os.path.join(test_dir, 'test.s01e02.mp4')
        open(file_path3, 'w+').close()
        self.assertTrue(blind_media_move(file_path3) is None)

        # Clean up db
        TvShow.objects.filter(title='test')[0].delete()
        genre_obj1.delete()

        # Remove test folder
        shutil.rmtree(test_dir)
        shutil.rmtree(genre_path1)


class TestChangeGenre(TestCase):
    def test_change_genre(self):
        # Create a dir for tests
        test_dir = os.path.join(BASE_DIR, 'mfo', 'test_dir')
        os.mkdir(test_dir)

        # Create Genre's specifically for testing
        genre_obj1 = Genre(genre='TestGenre1')
        genre_obj1.save()
        genre_path1 = os.path.join(BASE_DIR_FILES, 'TV Shows', 'TestGenre1')
        genre_movie_path1 = os.path.join(BASE_DIR_FILES, 'Movies', 'TestGenre1')

        # Create Genre's specifically for testing
        genre_obj2 = Genre(genre='TestGenre2')
        genre_obj2.save()
        genre_path2 = os.path.join(BASE_DIR_FILES, 'TV Shows', 'TestGenre2')
        genre_movie_path2 = os.path.join(BASE_DIR_FILES, 'Movies', 'TestGenre2')

        # Create a test TV file
        file_name = 'test.s01e01.mp4'
        file_path = os.path.join(test_dir, file_name)
        open(file_path, 'w+').close()

        # Create a test Movie file
        file_name2 = 'somemovie.mp4'
        file_path2 = os.path.join(test_dir, file_name2)
        open(file_path2, 'w+').close()

        # Test TV Show instance
        move_new_tv_show(file_path, genre=genre_obj1.genre)
        self.assertTrue(os.path.isfile(os.path.join(genre_path1, 'test', 'S01', file_name)))
        self.assertTrue(TvShow.objects.filter(title='test')[0].genre == genre_obj1)

        change_genre('test', genre_obj2.genre)

        self.assertFalse(os.path.isfile(os.path.join(genre_path1, 'test', 'S01', file_name)))
        self.assertTrue(os.path.isfile(os.path.join(genre_path2, 'test', 'S01', file_name)))
        self.assertTrue(TvShow.objects.filter(title='test')[0].genre == genre_obj2)

        # Test Movie instance
        move_movie(file_path2, genre=genre_obj1.genre)
        self.assertTrue(os.path.isfile(os.path.join(genre_movie_path1, file_name2)))
        self.assertTrue(Movie.objects.filter(title=file_name2)[0].genre == genre_obj1)

        change_genre(file_name2, genre_obj2.genre)

        self.assertFalse(os.path.isfile(os.path.join(genre_movie_path1, file_name2)))
        self.assertTrue(os.path.isfile(os.path.join(genre_movie_path2, file_name2)))
        self.assertTrue(Movie.objects.filter(title=file_name2)[0].genre == genre_obj2)

        shutil.rmtree(test_dir)
        shutil.rmtree(genre_path2)
