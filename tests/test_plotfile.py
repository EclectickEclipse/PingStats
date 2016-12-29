import unittest
from hypothesis import given, strategies as st

# Test resources
import csv
import time
import datetime as dt

# PingStats modules
import Plot


class Plotfile_test(unittest.TestCase):
    """ Tests `Plot.PlotFile` functionality. """
    @given(st.just('./tests/PingStatsLog.csv'))
    def test_init(self, path):
        obj = Plot.PlotFile(path)

        self.assertIsInstance(obj, Plot.PlotFile)

    @given(st.just('./tests/PingStatsLog.csv'))
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
        with open('./tests/PingStatsLog.csv') as f:
            reader = csv.reader(f)
            for x, y in Plot.PlotFile.yield_points(reader):
                self.assertIsInstance(x, dt.datetime)
                self.assertIsInstance(y, float)
