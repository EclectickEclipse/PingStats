import unittest
from hypothesis import given
from hypothesis import strategies as st
# TEST RESOURCES
from io import TextIOWrapper
import os
import csv
import sys
import platform
import subprocess
from tempfile import NamedTemporaryFile
import time
import datetime as dt

import core as c
import Plot


class TestCore(unittest.TestCase):
    """ Tests all non-plot related functionality. """
    @given(st.just(os.curdir), st.text())
    def test_build_files(self, path, name):
        try:
            test_file = c.Core.buildfile(path, name)
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
            c.Core.buildfile(path, name)

    @given(st.just(csv.writer(NamedTemporaryFile('w+'))),
           st.lists(st.integers(), min_size=2))
    def test_write_csv_data(self, writer, data):
        self.assertEqual(c.Core.write_csv_data(writer, data), data)

    @given(st.just('127.0.0.1'))
    def test_active_connections(self, address):
        try:
            self.assertIsInstance(c.Core.ping(address,
                                              verbose=False).__next__()[1],
                                  float)
        except PermissionError as e:
            if e.errno == 1:
                print('Run tests as sudo')

    @given(st.just('0.0.0.0'))
    def test_failed_connections(self, address):
        self.assertEqual(c.Core.ping(address, verbose=False).__next__()[1],
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
        c_obj = c.Core.ping('127.0.0.1', verbose=False)
        next(c_obj)
        sys.stdout = backup

        with open(fileobj.name) as f:
            self.assertEqual(f.read(), '')

    def test_ping_delay(self):
        obj = c.Core.ping('127.0.0.1', delay=1, verbose=False)
        time_now = time.time()
        results = []

        for result in obj:
            if result is not None:
                results.append(result)

            if time.time() - time_now >= 1:
                break

        self.assertEquals(len(results), 1)


class PlotTable_test(unittest.TestCase):
    def test_instantiate(self):
        self.assertIsInstance(Plot._PlotTable(), Plot._PlotTable)

    def test_instantiate_catch_zero_length(self):
        with self.assertRaises(ValueError):
            Plot._PlotTable(0)

    @given(st.integers(min_value=1))
    def test_instantiate_with_length_as_int(self, length):
        self.assertIsInstance(Plot._PlotTable(length), Plot._PlotTable)

    @given(st.one_of(st.text(), st.tuples(st.integers(), st.integers()),
                     st.booleans()))
    def test_instantiate_catch_invalid_data(self, data):
        with self.assertRaises(TypeError):
            Plot._PlotTable(data)

    @given(st.one_of(st.text(), st.tuples(st.integers(), st.integers()),
                     st.booleans(), st.floats(), st.text()))
    def test_appendx_invalid_data_catch(self, data):
        with self.assertRaises(TypeError):
            Plot._PlotTable().appendx(data)

    @given(st.just(dt.datetime.fromtimestamp(time.time())))
    def test_appendx_data_addition(self, data):
        ptable = Plot._PlotTable()
        ptable.appendx(data)

        self.assertTrue(ptable.x.count(data))

    @given(st.integers(min_value=1, max_value=5000), st.just(
        dt.datetime.fromtimestamp(time.time())))
    def test_appendx_flood(self, length_value, data):
        ptable = Plot._PlotTable(length_value)
        for i in range(length_value + 1):
            ptable.appendx(data)

        self.assertEqual(len(ptable.x), length_value)

    @given(st.one_of(st.tuples(st.integers(), st.integers()), st.integers(),
                     st.booleans(), st.text()))
    def test_appendy_invalid_data_catch(self, data):
        with self.assertRaises(TypeError):
            Plot._PlotTable().appendy(data)

    @given(st.floats())
    def test_appendy_data_addition(self, data):
        ptable = Plot._PlotTable()
        ptable.appendy(data)

        self.assertTrue(ptable.y.count(data))

    @given(st.integers(min_value=1, max_value=5000), st.floats())
    def test_appendy_flood(self, integer, data):
        ptable = Plot._PlotTable(integer)
        for i in range(integer + 1):
            ptable.appendy(data)

        self.assertEqual(len(ptable.y), integer)


class BasePlot_test(unittest.TestCase):
    # TODO Test `Plot._Plot.show_plot`
    @given(st.one_of(st.tuples(st.integers(), st.integers()),
                     st.booleans(), st.integers()))
    def test_instantiate_catch_invalid_title_string(self, data):
        with self.assertRaises(TypeError):
            plot = Plot._Plot
            plot.title_str = data

            plot()

    @given(st.just('\x00'))
    def test_instantiate_catch_null_byte_title_string(self, data):
        with self.assertRaises(ValueError) as e:
            plot = Plot._Plot
            plot.title_str = data
            plot()
            self.failIf(str(e).count('Title String must not have null bytes'),
                        'Did not catch the right exception. Caught: %s' %
                        str(e))

        plot.title_str = ''  # reset state to default

    @given(st.booleans())
    def test_instantiate_nofile(self, boolean):
        plot = Plot._Plot
        plot.nofile = boolean
        self.assertIsInstance(plot(), Plot._Plot)
        plot.nofile = False  # reset state to default


class AnimatePlot_test(unittest.TestCase):
    @given(st.just('127.0.0.1'),
           st.one_of(st.just(None), st.integers()),
           st.one_of(st.just(None), st.integers()))
    def test_instantiate_with_good_ip(self, address, table_length,
                                      refresh_freq):
        self.assertIsInstance(Plot.Animate(address,
                                           table_length=table_length,
                                           refresh_freq=refresh_freq),
                              Plot.Animate)

        self.can_init = True

    @given(st.just('127.0.0.1'),
           st.one_of(st.text(), st.tuples(st.integers(), st.integers()),
                     st.booleans()),
           st.one_of(st.text(), st.tuples(st.integers(), st.integers()),
                     st.booleans()))
    def test_instantiate_catch_bad_kwargs(self, address, table_length,
                                          refresh_freq):
        with self.assertRaises(TypeError) as e:
            Plot.Animate(address,
                         table_length=table_length,
                         refresh_freq=refresh_freq)

            if not e.count('table_length is not None or int') or e.count(
                    'refresh_freq is not None or int'):

                self.fail('Did not raise the right exception with \'%s\' and '
                          '\'%s\'.' % (str(table_length), str(refresh_freq)))

    def test_get_pings_with_good_ip(self):
        obj = Plot.Animate('127.0.0.1')
        gp = obj.get_pings(obj.ping_generator)

        time_now = time.time()
        for result in gp:
            if time.time() - time_now > 0.22:
                break

        print(obj.ptable.getx())
        self.assertGreaterEqual(len(obj.ptable.getx()), 1)
        self.assertGreaterEqual(len(obj.ptable.gety()), 1)

    def test_get_pings_with_bad_ip(self):
        obj = Plot.Animate('0.0.0.0')
        gp = obj.get_pings(obj.ping_generator)

        time_now = time.time()
        for result in gp:
            if time.time() - time_now > 0.2:
                break

        self.assertGreaterEqual(len(obj.ptable.getx()), 1)
        self.assertGreaterEqual(len(obj.ptable.gety()), 1)


class Plotfile_test(unittest.TestCase):
    @given(st.just('./test_data/PingStatsLog.csv'))
    def test_init(self, path):
        obj = Plot.PlotFile(path)

        self.assertIsInstance(obj, Plot.PlotFile)

    @given(st.just('./test_data/PingStatsLog.csv'))
    def test_generate_reader(self, path):
        fileobj = open(path)
        reader = csv.reader(fileobj)

        self.assertIsInstance(Plot.PlotFile.generate_reader(path),
                              type(reader))

        fileobj.close()

    @given(st.just(time.time()))
    def test_generate_datetime(self, timestamp):
        self.assertIsInstance(Plot.PlotFile.generate_datetime(timestamp),
                              type(dt.datetime.fromtimestamp(timestamp)))

    def test_yield_points(self):
        with open('./test_data/PingStatsLog.csv') as f:
            reader = csv.reader(f)
            for x, y in Plot.PlotFile.yield_points(reader):
                self.assertIsInstance(x, dt.datetime)
                self.assertIsInstance(y, float)


class GenerateFile_from_Plotfile_test(unittest.TestCase):
    @given(st.just('./test_data/PingStatsLog.csv'),
           st.just('./test_data/test_image.png'))
    def test_generate_file(self, data_path, image_path):
        p = Plot.PlotFile(data_path, image_path)
        p.show_plot()

        self.assertTrue(os.access(image_path, os.F_OK))

        if os.access(image_path, os.F_OK):
            os.remove(image_path)
        else:
            self.fail('Could not find a generated image to remove.')


if __name__ == '__main__':
    print(time.ctime())
    print('os.name: %s' % os.name)
    print('platform.system: %s' % platform.system())
    print('platform.release: %s' % platform.release())
    print('PingStats version: %s' % c.version)
    print('Python version (via sys.version): %s' % sys.version)
    pipe = subprocess.PIPE
    p = subprocess.Popen(['git', 'log', '--oneline', '-n 1'], stdout=pipe,
                         stderr=pipe)
    stdout, stderr = p.communicate()
    p.kill()
    print('stdout: \n%s\nstderr:\n%s\n\n' % (stdout, stderr))

    unittest.main(buffer=True)
