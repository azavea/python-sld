"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from unittest import TestCase
from models import *
import copy
from lxml import etree

class SLD_Test(TestCase):
    _sld = None
    def setUp(self):
        # Couldn't get this to work in setUpClass, but it would be better in there
        if SLD_Test._sld is None:
            SLD_Test._sld = StyledLayerDescriptor('sld/test/style.sld')

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

    def test_sld_version(self):
        self.assertEqual( self._sld.version, "1.0.0" )

    def test_sld_ns(self):
        self.assertEqual( self._sld.xmlns, 'http://www.opengis.net/sld' )

    def test_sld_namedlayer(self):
        self.assertTrue( isinstance(self._sld.NamedLayer, NamedLayer), "NamedLayer property is not the proper class.")

    def test_namedlayer_name(self):
        expected = 'poptot'
        self.assertEqual( self._sld.NamedLayer.Name, expected, "NamedLayer was named '%s', not '%s'" % (self._sld.NamedLayer.Name, expected,))

    def test_namedlayer_userstyle(self):
        self.assertTrue( isinstance(self._sld.NamedLayer.UserStyle, UserStyle), "UserStyle property is not the proper class.")

    def test_userstyle_title(self):
        sld = copy.deepcopy(self._sld)
        us = sld.NamedLayer.UserStyle 
        expected = 'Population'
        self.assertEqual( us.Title, expected, "UserStyle Title was '%s', not '%s'" % (us.Title, expected,))

        expected = 'Consternation'
        us.Title = expected
        self.assertEqual( us.Title, expected, "UserStyle Title was '%s', not '%s'" % (us.Title, expected,))

        us._node.remove(us._node[2])

        expected = """<UserStyle xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <Title>Consternation</Title>
      <Abstract>A grayscale style showing the population numbers in a given geounit.</Abstract>
      </UserStyle>"""
        actual = etree.tostring(us._node, with_tail=False)
        self.assertEqual( len(actual), len(expected))
        self.assertEqual( actual, expected, "UserStyle was not serialized correctly.\n%s" % actual )

    def test_userstyle_abstract(self):
        sld = copy.deepcopy(self._sld)
        us = sld.NamedLayer.UserStyle
        expected = 'A grayscale style showing the population numbers in a given geounit.'
        self.assertEqual( us.Abstract, expected, "UserStyle Abstract was '%s', not '%s'" % (us.Abstract, expected,))

        expected = 'Something completely different'
        us.Abstract = expected
        self.assertEqual( us.Abstract, expected, "UserStyle Abstract was '%s', not '%s'" % (us.Abstract, expected,))

        us._node.remove(us._node[2])

        expected = """<UserStyle xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <Title>Population</Title>
      <Abstract>Something completely different</Abstract>
      </UserStyle>"""
        actual = etree.tostring(us._node, with_tail=False)
        self.assertEqual( len(actual), len(expected) )
        self.assertEqual( actual, expected, "UserStyle was not serialized correctly.\n%s" % actual )

    def test_userstyle_featuretypestyle(self):
        self.assertTrue( isinstance(self._sld.NamedLayer.UserStyle.FeatureTypeStyle, FeatureTypeStyle), "FeatureTypeStyle property is not the proper class.")

    def test_featuretypestyle_rules(self):
        rules = self._sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules
        self.assertEqual( len(rules), 6 )
        self.assertTrue( isinstance(rules[0], Rule), "Rule item in list is not the proper class." )

    def test_rule_title(self):
        sld = copy.deepcopy(self._sld)
        rule = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        expected = "> 880"
        self.assertEqual( rule.Title, expected )

        del rule.Title
        self.assertTrue( rule.Title is None )

        expected = "> 999"
        rule.Title = expected
        self.assertEqual( rule.Title, expected )

        expected = """<Rule xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
          <ogc:Filter>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>number</ogc:PropertyName>
              <ogc:Literal>880</ogc:Literal>
            </ogc:PropertyIsGreaterThanOrEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#252525</CssParameter>
            </Fill>
          </PolygonSymbolizer>
        <Title>&gt; 999</Title></Rule>"""
        actual = etree.tostring(rule._node, with_tail=False)
        self.assertEqual( actual, expected, actual )
