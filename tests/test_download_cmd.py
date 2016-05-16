from dronekit_sitl import SITL
from nose.tools import raises
import unittest

class TestDownloader(unittest.TestCase):
    @raises(SystemExit)
    def test_download_404(self):
        sitl = SITL()
        sitl.download('rocket', '1.123.098.123')
