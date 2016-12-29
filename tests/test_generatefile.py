import unittest

# Test resources
import os

# PingStats modules
import Plot


class GenerateFile_from_Plotfile_test(unittest.TestCase):
    """ Tests `Plot.PlotFile` image generation. """
    def test_generate_file(self, data_path='./tests/PingStatsLog.csv',
                           image_path='./tests/test_image.png'):
        p = Plot.PlotFile(data_path, image_path)
        p.show_plot()

        self.assertTrue(os.access(image_path, os.F_OK))

        if os.access(image_path, os.F_OK):
            os.remove(image_path)
        else:
            self.fail('Could not find a generated image to remove.')
