import unittest
from hypothesis import given, strategies as st

import os
import time
import sys
import csv
from tempfile import NamedTemporaryFile
from io import TextIOWrapper

import core as c


class TestCore(unittest.TestCase):
    """ Tests all non-plot related functionality. """
    @given(st.just(os.curdir), st.text())
    def test_build_files(self, path, name):
        try:
            test_file = c.buildfile(path, name)
            self.assertIsInstance(test_file, TextIOWrapper)
            test_file.close()
            os.remove(test_file.name)
        except ValueError as e:
            if str(e) == 'embedded null byte':
                print('Caught embedded null byte error in test_build_files')
            elif str(e).count('Illegal file name'):
                print('Caught illegal file name exception')
            else:
                raise

        except FileNotFoundError:
            print('TestCore.test_build_files caught OS non legal file path: '
                  '%s%s' % (path, name))

    @given(st.just('.'), st.just('*'))
    def test_build_files_fail_on_invalid_character(self, path, name):
        with self.assertRaises(ValueError):
            c.buildfile(path, name)

    @given(st.just(csv.writer(NamedTemporaryFile('w+'))),
           st.lists(st.integers(), min_size=2))
    def test_write_csv_data(self, writer, data):
        self.assertEqual(c.write_csv_data(writer, data), data)

    @given(st.just('127.0.0.1'))
    def test_active_connections(self, address):
        try:
            self.assertIsInstance(c.ping(address,
                                         verbose=False).__next__()[1],
                                  float)
        except PermissionError as e:
            if e.errno == 1:
                print('Run tests as sudo')

    @given(st.just('0.0.0.0'))
    def test_failed_connections(self, address):
        self.assertEqual(c.ping(address, verbose=False).__next__()[1],
                         None)

    @given(st.just('127.0.0.1'), st.just(os.curdir), st.text(), st.booleans())
    def test_init(self, address, file_path, file_name, nofile):
        try:
            core_object = c.Core(address, file_path, file_name, nofile)
            self.assertIsInstance(core_object, c.Core)

            if not nofile:
                core_object.built_file.close()
                os.remove(core_object.built_file.name)
        except ValueError:
            pass

    @given(st.one_of(st.just('*'), st.just('\x80'), st.just('\x00')))
    def test_fail_string_validation(self, string):
        self.assertFalse(c.validate_string(string))

    @given(st.just('test string'))
    def test_complete_string_validation(self, string):
        self.assertTrue(c.validate_string(string))

    def test_quiet_output(self):
        backup = sys.stdout
        fileobj = NamedTemporaryFile('w+')
        sys.stdout = fileobj
        c_obj = c.ping('127.0.0.1', verbose=False)
        next(c_obj)
        sys.stdout = backup

        with open(fileobj.name) as f:
            self.assertEqual(f.read(), '')

    def test_ping_delay(self):
        obj = c.ping('127.0.0.1', delay=1, verbose=False)
        time_now = time.time()
        results = []

        for result in obj:
            if result is not None:
                results.append(result)

            if time.time() - time_now >= 1:
                break

        self.assertEquals(len(results), 1)

    def test_nofile(self):
        c.Core('127.0.0.1', file_path='tests/', file_name='TestCSV',
               nofile=True)

        self.assertFalse(os.access('tests/TestCSV.csv', os.F_OK))
