import unittest
from hypothesis import given, strategies as st

import plot


class BasePlot_test(unittest.TestCase):
    """ Tests `Plot._Plot` functionality. """
    # TODO Test `Plot._Plot.show_plot`
    @given(st.one_of(st.tuples(st.integers(), st.integers()),
                     st.booleans(), st.integers()))
    def test_instantiate_catch_invalid_title_string(self, data):
        with self.assertRaises(TypeError):
            p = plot._Plot
            p.title_str = data

            p()

    @given(st.just('\x00'))
    def test_instantiate_catch_null_byte_title_string(self, data):
        with self.assertRaises(ValueError) as e:
            p = plot._Plot
            p.title_str = data
            p()
            self.failIf(str(e).count('Title String must not have null bytes'),
                        'Did not catch the right exception. Caught: %s' %
                        str(e))

        plot.title_str = ''  # reset state to default
