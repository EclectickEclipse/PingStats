import unittest
from hypothesis import given, strategies as st

# Test resources
import datetime as dt
import time

# PingStats modules
import plot


class PlotTable_test(unittest.TestCase):
    """ Tests `Plot._PlotTable` functionality. """
    def test_instantiate(self):
        self.assertIsInstance(plot._PlotTable(), plot._PlotTable)

    def test_instantiate_catch_zero_length(self):
        with self.assertRaises(ValueError):
            plot._PlotTable(0)

    @given(st.integers(min_value=1))
    def test_instantiate_with_length_as_int(self, length):
        self.assertIsInstance(plot._PlotTable(length), plot._PlotTable)

    @given(st.one_of(st.text(), st.tuples(st.integers(), st.integers()),
                     st.booleans()))
    def test_instantiate_catch_invalid_data(self, data):
        with self.assertRaises(TypeError):
            plot._PlotTable(data)

    @given(st.one_of(st.text(), st.tuples(st.integers(), st.integers()),
                     st.booleans(), st.floats(), st.text()))
    def test_appendx_invalid_data_catch(self, data):
        with self.assertRaises(TypeError):
            plot._PlotTable().appendx(data)

    @given(st.just(dt.datetime.fromtimestamp(time.time())))
    def test_appendx_data_addition(self, data):
        ptable = plot._PlotTable()
        ptable.appendx(data)

        self.assertTrue(ptable.x.count(data))

    @given(st.integers(min_value=1, max_value=5000), st.just(
        dt.datetime.fromtimestamp(time.time())))
    def test_appendx_flood(self, length_value, data):
        ptable = plot._PlotTable(length_value)
        for i in range(length_value + 1):
            ptable.appendx(data)

        self.assertEqual(len(ptable.x), length_value)

    @given(st.one_of(st.tuples(st.integers(), st.integers()), st.integers(),
                     st.booleans(), st.text()))
    def test_appendy_invalid_data_catch(self, data):
        with self.assertRaises(TypeError):
            plot._PlotTable().appendy(data)

    @given(st.floats())
    def test_appendy_data_addition(self, data):
        ptable = plot._PlotTable()
        ptable.appendy(data)

        self.assertTrue(ptable.y.count(data))

    @given(st.integers(min_value=1, max_value=5000), st.floats())
    def test_appendy_flood(self, integer, data):
        ptable = plot._PlotTable(integer)
        for i in range(integer + 1):
            ptable.appendy(data)

        self.assertEqual(len(ptable.y), integer)
