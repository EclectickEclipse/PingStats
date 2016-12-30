import unittest
from hypothesis import given, strategies as st

# Test resources
import time
import os

# PingStats modules
import Plot


class AnimatePlot_test(unittest.TestCase):
    """ Tests `Plot.Animate` functionality. """
    # TODO Test `Plot.Animate.animate`
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
        obj = Plot.Animate('127.0.0.1', nofile=True)
        gp = obj.get_pings(obj.ping_generator)

        time_now = time.time()
        for result in gp:
            if time.time() - time_now > 0.22:
                break

        print(obj.ptable.getx())
        self.assertGreaterEqual(len(obj.ptable.getx()), 1)
        self.assertGreaterEqual(len(obj.ptable.gety()), 1)

    def test_get_pings_with_bad_ip(self):
        obj = Plot.Animate('0.0.0.0', nofile=True)
        gp = obj.get_pings(obj.ping_generator)

        time_now = time.time()
        for result in gp:
            if time.time() - time_now > 0.2:
                break

        self.assertGreaterEqual(len(obj.ptable.getx()), 1)
        self.assertGreaterEqual(len(obj.ptable.gety()), 1)

    def test_get_pings_write_csv(self):
        obj = Plot.Animate('0.0.0.0', file_path='tests/',
                           file_name='get_pings_test.csv')
        gp = obj.get_pings(obj.ping_generator)

        time_now = time.time()
        for result in gp:
            if time.time() - time_now > obj.delay:
                break

        self.assertGreaterEqual(len(obj.ptable.getx()), 1)
        self.assertGreaterEqual(len(obj.ptable.gety()), 1)
        self.assertTrue(os.access(obj.built_file.name, os.F_OK))
        try:
            os.remove(obj.built_file.name)
        except OSError:
            self.fail('Could not remove file at path: %s'
                      % obj.built_file.name)

    @given(st.booleans())
    def test_no_file(self, boolean):
        if boolean:
            p = Plot.Animate('127.0.0.1', file_path='tests//',
                             file_name='testCSV', nofile=boolean)
            self.assertIsInstance(p, Plot.Animate)
            self.assertFalse(os.access('tests/testCSV.csv', os.F_OK))

        else:
            p = Plot.Animate('127.0.0.1', file_path='tests/',
                             file_name='testCSV', nofile=boolean)
            self.assertIsInstance(p, Plot.Animate)
            self.assertTrue(os.access('tests/testCSV.csv', os.F_OK))
            try:
                os.remove('tests/testCSV.csv')
            except OSError as e:
                self.fail('Could not remove file created. Raised %s' % str(e))
