"""
Test suite for the StyledLayerDescriptor python library.

License
=======
Copyright 2011 David Zwarg <U{dzwarg@azavea.com}>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

U{http://www.apache.org/licenses/LICENSE-2.0}

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: David Zwarg
@contact: dzwarg@azavea.com
@copyright: 2011, Azavea
@license: Apache 2.0
@version: 1.0.6
"""
from sld import *
import unittest, copy
from lxml import etree

class SLD_Test(unittest.TestCase):
    """
    All tests for django-sld are contained in this TestCase class.
    """

    _sld0 = None
    """Store a parsed SLD, with known styles and structure"""

    _sld1 = None
    """Store a dynamically generated SLD"""

    def setUp(self):
        """
        Set up the test fixture.
        """
        if SLD_Test._sld0 is None:
            SLD_Test._sld0 = StyledLayerDescriptor('test/style.sld')
            SLD_Test._sld1 = StyledLayerDescriptor()


    def test_constructor1(self):
        """
        Test an empty constructor, and make sure the SLD is valid.
        """
        sld = StyledLayerDescriptor()

        self.assertTrue( 'sld' in sld._nsmap )

        expected = """<sld:StyledLayerDescriptor xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0"/>"""
        actual = etree.tostring(sld._node, with_tail=False)
        self.assertEqual(actual, expected)

        sld.normalize()

        self.assertTrue(sld.validate())
        

    def test_constructor2(self):
        """
        Test a constructor on a bogus file.
        """
        try:
            sld = StyledLayerDescriptor('junk')
            self.fail("Error")
        except:
            # Good, failure on a junk file.
            pass

    def test_sld_version(self):
        """
        Test the SLD version on the root element.
        """
        self.assertEqual( self._sld0.version, "1.0.0" )

    def test_sld_ns(self):
        """
        Test the namespace on the root element.
        """
        self.assertEqual( self._sld0.xmlns, 'http://www.opengis.net/sld' )

    def test_sld_namedlayer1(self):
        """
        Test the object type of the NamedLayer property.
        """
        self.assertTrue( isinstance(self._sld0.NamedLayer, NamedLayer), "NamedLayer property is not the proper class.")

    def test_sld_namedlayer2(self):
        """
        Test the creation and construction of a NamedLayer element.
        """
        self.assertTrue( self._sld1.NamedLayer is None )

        sld = copy.deepcopy(self._sld1)

        sld.create_namedlayer('test named layer')
        self.assertFalse( sld.NamedLayer is None )

        sld.normalize()
        self.assertTrue(sld.validate())

    def test_namedlayer_name(self):
        """
        Test the proper parsing of the name of the NamedLayer.
        """
        expected = 'poptot'
        self.assertEqual( self._sld0.NamedLayer.Name, expected, "NamedLayer was named '%s', not '%s'" % (self._sld0.NamedLayer.Name, expected,))

    def test_namedlayer_userstyle1(self):
        """
        Test the object type of the UserStyle property.
        """
        self.assertTrue( isinstance(self._sld0.NamedLayer.UserStyle, UserStyle), "UserStyle property is not the proper class.")

    def test_namedlayer_userstyle2(self):
        """
        Test the proper parsing of the UserStyle property.
        """
        sld = copy.deepcopy(self._sld1)

        sld.create_namedlayer('test named layer')

        self.assertTrue( sld.NamedLayer.UserStyle is None)

        sld.NamedLayer.create_userstyle()

        self.assertFalse( sld.NamedLayer.UserStyle is None)

        sld.normalize()
        self.assertFalse(sld.validate())

    def test_userstyle_title1(self):
        """
        Test the parsing of the UserStyle Title, and proper rendering.
        """
        sld = copy.deepcopy(self._sld0)
        us = sld.NamedLayer.UserStyle 
        expected = 'Population'
        self.assertEqual( us.Title, expected, "UserStyle Title was '%s', not '%s'" % (us.Title, expected,))

        expected = 'Consternation'
        us.Title = expected
        self.assertEqual( us.Title, expected, "UserStyle Title was '%s', not '%s'" % (us.Title, expected,))

        us._node.remove(us._node[2])

        expected = """<UserStyle xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <Title>%s</Title>
      <Abstract>A grayscale style showing the population numbers in a given geounit.</Abstract>
      </UserStyle>""" % expected
        actual = etree.tostring(us._node, with_tail=False)
        self.assertEqual( len(actual), len(expected))
        self.assertEqual( actual, expected, "UserStyle was not serialized correctly.\n%s" % actual )

        sld.normalize()
        self.assertFalse(sld.validate())

    def test_userstyle_title2(self):
        """
        Test the construction of the UserStyle Title, and proper rendering.
        """
        sld = copy.deepcopy(self._sld1)
        sld.create_namedlayer('test named layer')
        sld.NamedLayer.create_userstyle()

        us = sld.NamedLayer.UserStyle 
        self.assertTrue( us.Title is None, "UserStyle Title was not None")

        expected = 'Consternation'
        us.Title = expected
        self.assertEqual( us.Title, expected, "UserStyle Title was '%s', not '%s'" % (us.Title, expected,))

        expected = """<sld:UserStyle xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"><sld:Title>%s</sld:Title></sld:UserStyle>""" % expected
        actual = etree.tostring(us._node, with_tail=False)
        self.assertEqual( len(actual), len(expected))
        self.assertEqual( actual, expected, "UserStyle was not serialized correctly.\n%s" % actual )

        sld.normalize()
        self.assertFalse(sld.validate())

    def test_userstyle_abstract1(self):
        """
        Test the parsing of the UserStyle Abstract, and proper rendering.
        """
        sld = copy.deepcopy(self._sld0)
        us = sld.NamedLayer.UserStyle
        expected = 'A grayscale style showing the population numbers in a given geounit.'
        self.assertEqual( us.Abstract, expected, "UserStyle Abstract was '%s', not '%s'" % (us.Abstract, expected,))

        expected = 'Something completely different'
        us.Abstract = expected
        self.assertEqual( us.Abstract, expected, "UserStyle Abstract was '%s', not '%s'" % (us.Abstract, expected,))

        us._node.remove(us._node[2])

        expected = """<UserStyle xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <Title>Population</Title>
      <Abstract>%s</Abstract>
      </UserStyle>""" % expected
        actual = etree.tostring(us._node, with_tail=False)
        self.assertEqual( len(actual), len(expected) )
        self.assertEqual( actual, expected, "UserStyle was not serialized correctly.\n%s" % actual )

        sld.normalize()
        self.assertFalse(sld.validate())

    def test_userstyle_abstract2(self):
        """
        Test the construction of the UserStyle Abstract, and proper rendering.
        """
        sld = copy.deepcopy(self._sld1)
        sld.create_namedlayer('test named layer')
        sld.NamedLayer.create_userstyle()

        us = sld.NamedLayer.UserStyle
        self.assertTrue( us.Abstract is None, "UserStyle Abstract was not None")

        expected = 'Something completely different'
        us.Abstract = expected
        self.assertEqual( us.Abstract, expected, "UserStyle Abstract was '%s', not '%s'" % (us.Abstract, expected,))

        expected = """<sld:UserStyle xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"><sld:Abstract>%s</sld:Abstract></sld:UserStyle>""" % expected
        actual = etree.tostring(us._node, with_tail=False)
        self.assertEqual( len(actual), len(expected) )
        self.assertEqual( actual, expected, "UserStyle was not serialized correctly.\n%s" % actual )

        sld.normalize()
        self.assertFalse(sld.validate())

    def test_userstyle_featuretypestyle1(self):
        """
        Test the object type of the FeatureTypeStyle property.
        """
        self.assertTrue( isinstance(self._sld0.NamedLayer.UserStyle.FeatureTypeStyle, FeatureTypeStyle), "FeatureTypeStyle property is not the proper class.")

    def test_userstyle_featuretypestyle2(self):
        """
        Test the construction of a new FeatureTypeStyle property.
        """
        sld = copy.deepcopy(self._sld1)
        sld.create_namedlayer('test named layer')
        sld.NamedLayer.create_userstyle()

        self.assertTrue( sld.NamedLayer.UserStyle.FeatureTypeStyle is None )

        sld.NamedLayer.UserStyle.create_featuretypestyle()

        self.assertFalse( sld.NamedLayer.UserStyle.FeatureTypeStyle is None )

        sld.normalize()
        self.assertFalse(sld.validate())

    def test_featuretypestyle_rules1(self):
        """
        Test the parsing of the Rules property.
        """
        rules = self._sld0.NamedLayer.UserStyle.FeatureTypeStyle.Rules
        self.assertEqual( len(rules), 6 )
        self.assertTrue( isinstance(rules[0], Rule), "Rule item in list is not the proper class." )

    def test_featuretypestyle_rules2(self):
        """
        Test the construction of the Rules property.
        """
        sld = copy.deepcopy(self._sld1)
        sld.create_namedlayer('test named layer')
        sld.NamedLayer.create_userstyle()
        sld.NamedLayer.UserStyle.create_featuretypestyle()

        rules = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules
        self.assertEqual( len(rules), 0 )

        sld.NamedLayer.UserStyle.FeatureTypeStyle.create_rule('test rule', PointSymbolizer)
        rules = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules

        self.assertEqual( len(rules), 1 )

        sld.normalize()
        self.assertTrue(sld.validate())

    def test_rule_title1(self):
        """
        Test the parsing of the individual Rule properties.
        """
        sld = copy.deepcopy(self._sld0)
        rule = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        expected = "> 880"
        self.assertEqual( rule.Title, expected )

        expected = "> 999"
        rule.Title = expected
        self.assertEqual( rule.Title, expected )

        expected = """<Rule xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
          <Title>&gt; 999</Title>
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
        </Rule>"""
        actual = etree.tostring(rule._node, with_tail=False)
        self.assertEqual( actual, expected, actual )
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_rule_title2(self):
        """
        Test the construction of new Rule properties.
        """
        sld = copy.deepcopy(self._sld1)
        sld.create_namedlayer('test named layer')
        sld.NamedLayer.create_userstyle()
        sld.NamedLayer.UserStyle.create_featuretypestyle()
        sld.NamedLayer.UserStyle.FeatureTypeStyle.create_rule('test rule', PointSymbolizer)

        rule = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        expected = "> 999"
        rule.Title = expected
        self.assertEqual( rule.Title, expected )

        expected = """<sld:Rule xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"><sld:Title>&gt; 999</sld:Title><sld:PointSymbolizer><sld:Graphic><sld:Mark><sld:WellKnownName>square</sld:WellKnownName><sld:Fill><sld:CssParameter name="fill">#ff0000</sld:CssParameter></sld:Fill></sld:Mark></sld:Graphic></sld:PointSymbolizer></sld:Rule>"""
        actual = etree.tostring(rule._node, with_tail=False)
        self.assertEqual( actual, expected, actual )
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_rule_filter1(self):
        """
        Test the parsing of the Filter property.
        """
        sld = copy.deepcopy(self._sld0)
        rule = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        self.assertFalse( rule.Filter.PropertyIsGreaterThanOrEqualTo is None )

        self.assertEqual( rule.Filter.PropertyIsGreaterThanOrEqualTo.PropertyName, 'number' )
        self.assertEqual( rule.Filter.PropertyIsGreaterThanOrEqualTo.Literal, '880' )
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_rule_filter_none(self):
        """
        Test the construction of the Filter property.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        rfilter = rule.create_filter()

        self.assertTrue( rfilter is None )
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_filter_eq(self):
        """
        Test the construction of an equality filter.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        rfilter = rule.create_filter('valueA', '==', '5000')

        self.assertTrue( rfilter.PropertyIsNotEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLessThan is None )
        self.assertTrue( rfilter.PropertyIsLessThanOrEqualTo is None )
        self.assertTrue( rfilter.PropertyIsGreaterThan is None )
        self.assertTrue( rfilter.PropertyIsGreaterThanOrEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLike is None )
        self.assertFalse( rfilter.PropertyIsEqualTo is None )
        self.assertEqual( rfilter.PropertyIsEqualTo.PropertyName, 'valueA' )
        self.assertEqual( rfilter.PropertyIsEqualTo.Literal, '5000' )

        sld.normalize()
        self.assertTrue(sld.validate())

    def test_filter_lte(self):
        """
        Test the construction of a less-than-or-equal Filter.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        rfilter = rule.create_filter('valueB', '<=', '5000')

        self.assertTrue( rfilter.PropertyIsEqualTo is None )
        self.assertTrue( rfilter.PropertyIsNotEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLessThan is None )
        self.assertTrue( rfilter.PropertyIsGreaterThan is None )
        self.assertTrue( rfilter.PropertyIsGreaterThanOrEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLike is None )
        self.assertFalse( rfilter.PropertyIsLessThanOrEqualTo is None )
        self.assertEqual( rfilter.PropertyIsLessThanOrEqualTo.PropertyName, 'valueB' )
        self.assertEqual( rfilter.PropertyIsLessThanOrEqualTo.Literal, '5000' )
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_filter_lt(self):
        """
        Test the construction of a less-than Filter.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        rfilter = rule.create_filter('valueC', '<', '500')

        self.assertTrue( rfilter.PropertyIsEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLessThanOrEqualTo is None )
        self.assertTrue( rfilter.PropertyIsNotEqualTo is None )
        self.assertTrue( rfilter.PropertyIsGreaterThan is None )
        self.assertTrue( rfilter.PropertyIsGreaterThanOrEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLike is None )
        self.assertFalse( rfilter.PropertyIsLessThan is None )
        self.assertEqual( rfilter.PropertyIsLessThan.PropertyName, 'valueC' )
        self.assertEqual( rfilter.PropertyIsLessThan.Literal, '500' )

        sld.normalize()
        self.assertTrue(sld.validate())

    def test_filter_gte(self):
        """
        Test the construction of a greater-than-or-equal Filter.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        rfilter = rule.create_filter('valueD', '>=', '100')

        self.assertTrue( rfilter.PropertyIsEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLessThanOrEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLessThan is None )
        self.assertTrue( rfilter.PropertyIsNotEqualTo is None )
        self.assertTrue( rfilter.PropertyIsGreaterThan is None )
        self.assertTrue( rfilter.PropertyIsLike is None )
        self.assertFalse( rfilter.PropertyIsGreaterThanOrEqualTo is None )
        self.assertEqual( rfilter.PropertyIsGreaterThanOrEqualTo.PropertyName, 'valueD' )
        self.assertEqual( rfilter.PropertyIsGreaterThanOrEqualTo.Literal, '100' )
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_filter_gt(self):
        """
        Test the construction of a greater-than Filter.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        rfilter = rule.create_filter('valueE', '>', '10')

        self.assertTrue( rfilter.PropertyIsEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLessThanOrEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLessThan is None )
        self.assertTrue( rfilter.PropertyIsGreaterThanOrEqualTo is None )
        self.assertTrue( rfilter.PropertyIsNotEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLike is None )
        self.assertFalse( rfilter.PropertyIsGreaterThan is None )
        self.assertEqual( rfilter.PropertyIsGreaterThan.PropertyName, 'valueE' )
        self.assertEqual( rfilter.PropertyIsGreaterThan.Literal, '10' )
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_filter_neq(self):
        """
        Test the construction of an inequality Filter.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        rfilter = rule.create_filter('valueF', '!=', '0.01')

        self.assertTrue( rfilter.PropertyIsEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLessThan is None )
        self.assertTrue( rfilter.PropertyIsLessThanOrEqualTo is None )
        self.assertTrue( rfilter.PropertyIsGreaterThan is None )
        self.assertTrue( rfilter.PropertyIsGreaterThanOrEqualTo is None )
        self.assertTrue( rfilter.PropertyIsLike is None )
        self.assertFalse( rfilter.PropertyIsNotEqualTo is None )
        self.assertEqual( rfilter.PropertyIsNotEqualTo.PropertyName, 'valueF' )
        self.assertEqual( rfilter.PropertyIsNotEqualTo.Literal, '0.01' )
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_filter_and(self):
        """
        Test the construction of a logical-and Filter.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        
        filter1 = Filter(rule)
        filter1.PropertyIsGreaterThan = PropertyCriterion(filter1, 'PropertyIsGreaterThan')
        filter1.PropertyIsGreaterThan.PropertyName = 'number'
        filter1.PropertyIsGreaterThan.Literal = '-10'

        filter2 = Filter(rule)
        filter2.PropertyIsLessThanOrEqualTo = PropertyCriterion(filter2, 'PropertyIsLessThanOrEqualTo')
        filter2.PropertyIsLessThanOrEqualTo.PropertyName = 'number'
        filter2.PropertyIsLessThanOrEqualTo.Literal = '10'

        rule.Filter = filter1 + filter2

        expected = """<sld:Rule xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"><sld:Title>test rule</sld:Title><sld:PointSymbolizer><sld:Graphic><sld:Mark><sld:WellKnownName>square</sld:WellKnownName><sld:Fill><sld:CssParameter name="fill">#ff0000</sld:CssParameter></sld:Fill></sld:Mark></sld:Graphic></sld:PointSymbolizer><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>-10</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>10</ogc:Literal></ogc:PropertyIsLessThanOrEqualTo></ogc:And></ogc:Filter></sld:Rule>"""
        actual = etree.tostring(rule._node, with_tail=False)
        self.assertEqual(actual, expected)
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_filter_or(self):
        """
        Test the construction of a logical-or Filter.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        
        filter1 = Filter(rule)
        filter1.PropertyIsGreaterThan = PropertyCriterion(filter1, 'PropertyIsGreaterThan')
        filter1.PropertyIsGreaterThan.PropertyName = 'number'
        filter1.PropertyIsGreaterThan.Literal = '10'

        filter2 = Filter(rule)
        filter2.PropertyIsLessThan= PropertyCriterion(filter2, 'PropertyIsLessThan')
        filter2.PropertyIsLessThan.PropertyName = 'number'
        filter2.PropertyIsLessThan.Literal = '-10'

        rule.Filter = filter1 | filter2

        expected = """<sld:Rule xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"><sld:Title>test rule</sld:Title><sld:PointSymbolizer><sld:Graphic><sld:Mark><sld:WellKnownName>square</sld:WellKnownName><sld:Fill><sld:CssParameter name="fill">#ff0000</sld:CssParameter></sld:Fill></sld:Mark></sld:Graphic></sld:PointSymbolizer><ogc:Filter><ogc:Or><ogc:PropertyIsGreaterThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>10</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:PropertyIsLessThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>-10</ogc:Literal></ogc:PropertyIsLessThan></ogc:Or></ogc:Filter></sld:Rule>"""
        actual = etree.tostring(rule._node, with_tail=False)
        self.assertEqual(actual, expected)
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_filter_and_or(self):
        """
        Test the construction of a logical-and combined with a logical-or Filter.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        
        filter1 = Filter(rule)
        filter1.PropertyIsGreaterThan = PropertyCriterion(filter1, 'PropertyIsGreaterThan')
        filter1.PropertyIsGreaterThan.PropertyName = 'number'
        filter1.PropertyIsGreaterThan.Literal = '10'

        filter2 = Filter(rule)
        filter2.PropertyIsLessThan = PropertyCriterion(filter2, 'PropertyIsLessThan')
        filter2.PropertyIsLessThan.PropertyName = 'number'
        filter2.PropertyIsLessThan.Literal = '-10'

        filter3 = Filter(rule)
        filter3.PropertyIsEqualTo = PropertyCriterion(filter3, 'PropertyIsEqualTo')
        filter3.PropertyIsEqualTo.PropertyName = 'value'
        filter3.PropertyIsEqualTo.Literal = 'yes'

        rule.Filter = filter1 + (filter2 | filter3)

        expected = """<sld:Rule xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"><sld:Title>test rule</sld:Title><sld:PointSymbolizer><sld:Graphic><sld:Mark><sld:WellKnownName>square</sld:WellKnownName><sld:Fill><sld:CssParameter name="fill">#ff0000</sld:CssParameter></sld:Fill></sld:Mark></sld:Graphic></sld:PointSymbolizer><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>10</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:Or><ogc:PropertyIsLessThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>-10</ogc:Literal></ogc:PropertyIsLessThan><ogc:PropertyIsEqualTo><ogc:PropertyName>value</ogc:PropertyName><ogc:Literal>yes</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Or></ogc:And></ogc:Filter></sld:Rule>"""
        actual = etree.tostring(rule._node, with_tail=False, pretty_print=False)
        self.assertEqual(actual, expected)
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_rule_polysymbolizer1(self):
        """
        Test the parsing of the PolygonSymbolizer property.
        """
        sld = copy.deepcopy(self._sld0)
        rule = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        self.assertFalse( rule.PolygonSymbolizer is None )

        sld.normalize()
        self.assertTrue(sld.validate())

    def test_rule_polysymbolizer2(self):
        """
        Test the construction of a PolygonSymbolizer property.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        symbolizer = rule.create_symbolizer('Polygon')

        self.assertTrue( symbolizer.Fill is None )
        self.assertTrue( symbolizer.Stroke is None )
        self.assertTrue( symbolizer.Font is None )
        
        sld.normalize()
        self.assertTrue(sld.validate())
        
    def test_polysymoblizer_fill1(self):
        """
        Test the parsing of a Fill property.
        """
        sld = copy.deepcopy(self._sld0)
        rule = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        self.assertFalse( rule.PolygonSymbolizer.Fill is None )

        del rule.PolygonSymbolizer.Fill

        self.assertTrue( rule.PolygonSymbolizer.Fill is None )
        
        sld.normalize()
        self.assertTrue(sld.validate())

    def test_polysymbolizer_fill2(self):
        """
        Test the construction of a Fill property.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        symbolizer = rule.create_symbolizer('Polygon')
        fill = symbolizer.create_fill()

        self.assertFalse( fill.CssParameters is None )
        self.assertEqual( len(fill.CssParameters), 0 )
       
        sld.normalize()
        self.assertTrue(sld.validate())
        
    def test_fill_cssparameter1(self):
        """
        Test the parsing of the CssParameter property.
        """
        fill = self._sld0.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0].PolygonSymbolizer.Fill

        self.assertFalse( fill.CssParameters is None )
        self.assertEqual( len(fill.CssParameters), 1 )

        fill = self._sld0.NamedLayer.UserStyle.FeatureTypeStyle.Rules[5].LineSymbolizer.Stroke

        self.assertFalse( fill.CssParameters is None )
        self.assertEqual( len(fill.CssParameters), 2 )

    def test_fill_cssparameter2(self):
        """
        Test the construction of the CssParameter property.
        """
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', PointSymbolizer)
        symbolizer = rule.create_symbolizer('Polygon')
        fill = symbolizer.create_fill()
        parameter = fill.create_cssparameter('fill', '#ffffff')

        self.assertEqual( len(fill.CssParameters), 1 )
        self.assertEqual( fill.CssParameters[0].Name, 'fill' )
        self.assertEqual( fill.CssParameters[0].Value, '#ffffff' )
        
        sld.normalize()
        self.assertTrue(sld.validate())

if __name__ == '__main__':
    unittest.main()
