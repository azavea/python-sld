"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from models import *

class SLD_Test(TestCase):
    def setUp(self):
        self.sld = 'sld/test/style.sld'

    def test_constructor1(self):
        """
        Test the StyledLayerDescriptor constructor.
        """
        try:
            sld = StyledLayerDescriptor('junk')
            self.fail("Error")
        except:
            # Good, failure on a junk file.
            pass

    def test_constructor2(self):
        try:
            sld = StyledLayerDescriptor(self.sld)
            # Good, passing on a real file.
        except:
            self.fail("Error")

    def test_sld_version(self):
        sld = StyledLayerDescriptor(self.sld)

        self.assertEqual( sld.version, "1.0.0" )
