import unittest

# Test resources
import os

# PingStats modules
import plot


class GenerateFile_from_Plotfile_test(unittest.TestCase):
    """ Tests `Plot.PlotFile` image generation. """
    def test_generate_file(self, data_path='./tests/TestCSVLog.csv',
                           image_path='./tests/test_image.png'):
        p = plot.PlotFile(data_path, image_path)
        p.get_figure()

        self.assertTrue(os.access(image_path, os.F_OK))

        if os.access(image_path, os.F_OK):
            os.remove(image_path)
        else:
            self.fail('Could not find a generated image to remove.')
