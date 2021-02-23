#!/usr/bin/env python
"""
Test suite for the StyledLayerDescriptor python library.

License
=======
Copyright 2011-2014 David Zwarg <U{david.a@zwarg.com}>

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
@contact: david.a@zwarg.com
@copyright: 2011-2014, Azavea
@license: Apache 2.0
@version: 1.0.10
"""
import sld
import unittest
import copy
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
            SLD_Test._sld0 = sld.StyledLayerDescriptor('test/style.sld')
            SLD_Test._sld1 = sld.StyledLayerDescriptor()

    def test_constructor1(self):
        """
        Test an empty constructor, and make sure the SLD is valid.
        """
        sld_doc = sld.StyledLayerDescriptor()

        self.assertTrue('sld' in sld_doc._nsmap)

        expected = ["<sld:StyledLayerDescriptor",
                    'xmlns:sld="http://www.opengis.net/sld"',
                    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
                    'xmlns:xlink="http://www.w3.org/1999/xlink"',
                    'xmlns:ogc="http://www.opengis.net/ogc"',
                    'version="1.0.0"'
                   ]
        actual = etree.tostring(sld_doc._node, with_tail=False)
        for item in expected:
          self.assertIn(item.encode('utf-8'), actual)

        sld_doc.normalize()

        self.assertTrue(sld_doc.validate())

    def test_constructor2(self):
        """
        Test a constructor on a bogus file.
        """
        try:
            sld.StyledLayerDescriptor('junk')
            self.fail("Error")
        except:
            # Good, failure on a junk file.
            pass

    def test_sld_version(self):
        """
        Test the SLD version on the root element.
        """
        self.assertEqual(self._sld0.version, "1.0.0")

    def test_sld_ns(self):
        """
        Test the namespace on the root element.
        """
        self.assertEqual(self._sld0.xmlns, 'http://www.opengis.net/sld')

    def test_sld_namedlayer1(self):
        """
        Test the object type of the NamedLayer property.
        """
        self.assertTrue(isinstance(self._sld0.NamedLayer, sld.NamedLayer), "NamedLayer property is not the proper class.")

    def test_sld_namedlayer2(self):
        """
        Test the creation and construction of a NamedLayer element.
        """
        self.assertTrue(self._sld1.NamedLayer is None)

        sld_doc = copy.deepcopy(self._sld1)

        sld_doc.create_namedlayer('test named layer')
        self.assertFalse(sld_doc.NamedLayer is None)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_namedlayer_name(self):
        """
        Test the proper parsing of the name of the NamedLayer.
        """
        expected = 'poptot'
        self.assertEqual(self._sld0.NamedLayer.Name, expected, "NamedLayer was named '%s', not '%s'" % (self._sld0.NamedLayer.Name, expected,))

    def test_namedlayer_userstyle1(self):
        """
        Test the object type of the UserStyle property.
        """
        self.assertTrue(isinstance(self._sld0.NamedLayer.UserStyle, sld.UserStyle), "UserStyle property is not the proper class.")

    def test_namedlayer_userstyle2(self):
        """
        Test the proper parsing of the UserStyle property.
        """
        sld_doc = copy.deepcopy(self._sld1)

        sld_doc.create_namedlayer('test named layer')

        self.assertTrue(sld_doc.NamedLayer.UserStyle is None)

        sld_doc.NamedLayer.create_userstyle()

        self.assertFalse(sld_doc.NamedLayer.UserStyle is None)

        sld_doc.normalize()
        self.assertFalse(sld_doc.validate())

    def test_userstyle_title1(self):
        """
        Test the parsing of the UserStyle Title, and proper rendering.
        """
        sld_doc = copy.deepcopy(self._sld0)
        us = sld_doc.NamedLayer.UserStyle
        expected = 'Population'
        self.assertEqual(us.Title, expected, "UserStyle Title was '%s', not '%s'" % (us.Title, expected,))

        expected = 'Consternation'
        us.Title = expected
        self.assertEqual(us.Title, expected, "UserStyle Title was '%s', not '%s'" % (us.Title, expected,))

        us._node.remove(us._node[2])

        expected = [
          '<UserStyle',
          'xmlns="http://www.opengis.net/sld"',
          'xmlns:ogc="http://www.opengis.net/ogc"',
          'xmlns:xlink="http://www.w3.org/1999/xlink"',
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
          '<Title>%s</Title>' % expected,
          '<Abstract>A grayscale style showing the population numbers in a given geounit.</Abstract>'
        ]
        actual = etree.tostring(us._node, with_tail=False)
        for item in expected:
          self.assertIn(item.encode('utf-8'), actual)

        sld_doc.normalize()
        self.assertFalse(sld_doc.validate())

    def test_userstyle_title2(self):
        """
        Test the construction of the UserStyle Title, and proper rendering.
        """
        sld_doc = copy.deepcopy(self._sld1)
        sld_doc.create_namedlayer('test named layer')
        sld_doc.NamedLayer.create_userstyle()

        us = sld_doc.NamedLayer.UserStyle
        self.assertTrue(us.Title is None, "UserStyle Title was not None")

        expected = 'Consternation'
        us.Title = expected
        self.assertEqual(us.Title, expected, "UserStyle Title was '%s', not '%s'" % (us.Title, expected,))

        expected = [
          '<sld:UserStyle',
          'xmlns:sld="http://www.opengis.net/sld"',
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
          'xmlns:xlink="http://www.w3.org/1999/xlink"',
          'xmlns:ogc="http://www.opengis.net/ogc"',
          '<sld:Title>%s</sld:Title>' % expected
        ]
        actual = etree.tostring(us._node, with_tail=False)
        for item in expected:
          self.assertIn(item.encode('utf-8'), actual)

        sld_doc.normalize()
        self.assertFalse(sld_doc.validate())

    def test_userstyle_abstract1(self):
        """
        Test the parsing of the UserStyle Abstract, and proper rendering.
        """
        sld_doc = copy.deepcopy(self._sld0)
        us = sld_doc.NamedLayer.UserStyle
        expected = 'A grayscale style showing the population numbers in a given geounit.'
        self.assertEqual(us.Abstract, expected, "UserStyle Abstract was '%s', not '%s'" % (us.Abstract, expected,))

        expected = 'Something completely different'
        us.Abstract = expected
        self.assertEqual(us.Abstract, expected, "UserStyle Abstract was '%s', not '%s'" % (us.Abstract, expected,))

        us._node.remove(us._node[2])

        expected = [
          '<UserStyle',
          'xmlns="http://www.opengis.net/sld"',
          'xmlns:ogc="http://www.opengis.net/ogc"',
          'xmlns:xlink="http://www.w3.org/1999/xlink"',
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
          '<Title>Population</Title>',
          '<Abstract>%s</Abstract>' % expected
        ]
        actual = etree.tostring(us._node, with_tail=False)
        for item in expected: 
          self.assertIn(item.encode('utf-8'), actual)

        sld_doc.normalize()
        self.assertFalse(sld_doc.validate())

    def test_userstyle_abstract2(self):
        """
        Test the construction of the UserStyle Abstract, and proper rendering.
        """
        sld_doc = copy.deepcopy(self._sld1)
        sld_doc.create_namedlayer('test named layer')
        sld_doc.NamedLayer.create_userstyle()

        us = sld_doc.NamedLayer.UserStyle
        self.assertTrue(us.Abstract is None, "UserStyle Abstract was not None")

        expected = 'Something completely different'
        us.Abstract = expected
        self.assertEqual(us.Abstract, expected, "UserStyle Abstract was '%s', not '%s'" % (us.Abstract, expected,))

        expected = [
          '<sld:UserStyle',
          'xmlns:sld="http://www.opengis.net/sld"',
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
          'xmlns:xlink="http://www.w3.org/1999/xlink"',
          'xmlns:ogc="http://www.opengis.net/ogc"',
          '<sld:Abstract>%s</sld:Abstract>' % expected
        ]
        actual = etree.tostring(us._node, with_tail=False)
        for item in expected:
          self.assertIn(item.encode('utf-8'), actual)

        sld_doc.normalize()
        self.assertFalse(sld_doc.validate())

    def test_userstyle_featuretypestyle1(self):
        """
        Test the object type of the FeatureTypeStyle property.
        """
        self.assertTrue(isinstance(self._sld0.NamedLayer.UserStyle.FeatureTypeStyle, sld.FeatureTypeStyle), "FeatureTypeStyle property is not the proper class.")

    def test_userstyle_featuretypestyle2(self):
        """
        Test the construction of a new FeatureTypeStyle property.
        """
        sld_doc = copy.deepcopy(self._sld1)
        sld_doc.create_namedlayer('test named layer')
        sld_doc.NamedLayer.create_userstyle()

        self.assertTrue(sld_doc.NamedLayer.UserStyle.FeatureTypeStyle is None)

        sld_doc.NamedLayer.UserStyle.create_featuretypestyle()

        self.assertFalse(sld_doc.NamedLayer.UserStyle.FeatureTypeStyle is None)

        sld_doc.normalize()
        self.assertFalse(sld_doc.validate())

    def test_featuretypestyle_rules1(self):
        """
        Test the parsing of the Rules property.
        """
        rules = self._sld0.NamedLayer.UserStyle.FeatureTypeStyle.Rules
        self.assertEqual(len(rules), 7)
        self.assertTrue(isinstance(rules[0], sld.Rule), "Rule item in list is not the proper class.")

    def test_featuretypestyle_rules2(self):
        """
        Test the construction of the Rules property.
        """
        sld_doc = copy.deepcopy(self._sld1)
        sld_doc.create_namedlayer('test named layer')
        sld_doc.NamedLayer.create_userstyle()
        sld_doc.NamedLayer.UserStyle.create_featuretypestyle()

        rules = sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.Rules
        self.assertEqual(len(rules), 0)

        sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.create_rule('test rule', sld.PointSymbolizer)
        rules = sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.Rules

        self.assertEqual(len(rules), 1)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_rule_title1(self):
        """
        Test the parsing of the individual Rule properties.
        """
        sld_doc = copy.deepcopy(self._sld0)
        rule = sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        expected = "> 880"
        self.assertEqual(rule.Title, expected)

        expected = "> 999"
        rule.Title = expected
        self.assertEqual(rule.Title, expected)

        expected = [
          '<Rule',
          'xmlns="http://www.opengis.net/sld"',
          'xmlns:ogc="http://www.opengis.net/ogc"',
          'xmlns:xlink="http://www.w3.org/1999/xlink"',
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
          '<Title>&gt; 999</Title>',
          '''<ogc:Filter>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>number</ogc:PropertyName>
              <ogc:Literal>880</ogc:Literal>
            </ogc:PropertyIsGreaterThanOrEqualTo>
          </ogc:Filter>''',
          '<MaxScaleDenominator>20000</MaxScaleDenominator>',
          '''<PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#252525</CssParameter>
            </Fill>
          </PolygonSymbolizer>'''
        ]
        actual = etree.tostring(rule._node, with_tail=False)
        for item in expected:
          self.assertIn(item.encode('utf-8'), actual)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_rule_title2(self):
        """
        Test the construction of new Rule properties.
        """
        sld_doc = copy.deepcopy(self._sld1)
        sld_doc.create_namedlayer('test named layer')
        sld_doc.NamedLayer.create_userstyle()
        sld_doc.NamedLayer.UserStyle.create_featuretypestyle()
        sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.create_rule('test rule', sld.PointSymbolizer)

        rule = sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        expected = "> 999"
        rule.Title = expected
        self.assertEqual(rule.Title, expected)

        expected = [
          '<sld:Rule',
          'xmlns:sld="http://www.opengis.net/sld"',
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
          'xmlns:xlink="http://www.w3.org/1999/xlink"',
          'xmlns:ogc="http://www.opengis.net/ogc"',
          '<sld:Title>&gt; 999</sld:Title><sld:PointSymbolizer><sld:Graphic><sld:Mark><sld:WellKnownName>square</sld:WellKnownName><sld:Fill><sld:CssParameter name="fill">#ff0000</sld:CssParameter></sld:Fill></sld:Mark></sld:Graphic></sld:PointSymbolizer>'
        ]
        actual = etree.tostring(rule._node, with_tail=False)
        for item in expected:
          self.assertIn(item.encode('utf-8'), actual)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_rule_filter1(self):
        """
        Test the parsing of the Filter property.
        """
        sld_doc = copy.deepcopy(self._sld0)
        rule = sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        self.assertFalse(rule.Filter.PropertyIsGreaterThanOrEqualTo is None)

        self.assertEqual(rule.Filter.PropertyIsGreaterThanOrEqualTo.PropertyName, 'number')
        self.assertEqual(rule.Filter.PropertyIsGreaterThanOrEqualTo.Literal, '880')

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_rule_filter_none(self):
        """
        Test the construction of the Filter property.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        rfilter = rule.create_filter()

        self.assertTrue(rfilter is None)
        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_filter_eq(self):
        """
        Test the construction of an equality filter.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        rfilter = rule.create_filter('valueA', '==', '5000')

        self.assertTrue(rfilter.PropertyIsNotEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLessThan is None)
        self.assertTrue(rfilter.PropertyIsLessThanOrEqualTo is None)
        self.assertTrue(rfilter.PropertyIsGreaterThan is None)
        self.assertTrue(rfilter.PropertyIsGreaterThanOrEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLike is None)
        self.assertFalse(rfilter.PropertyIsEqualTo is None)
        self.assertEqual(rfilter.PropertyIsEqualTo.PropertyName, 'valueA')
        self.assertEqual(rfilter.PropertyIsEqualTo.Literal, '5000')

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_filter_lte(self):
        """
        Test the construction of a less-than-or-equal Filter.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        rfilter = rule.create_filter('valueB', '<=', '5000')

        self.assertTrue(rfilter.PropertyIsEqualTo is None)
        self.assertTrue(rfilter.PropertyIsNotEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLessThan is None)
        self.assertTrue(rfilter.PropertyIsGreaterThan is None)
        self.assertTrue(rfilter.PropertyIsGreaterThanOrEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLike is None)
        self.assertFalse(rfilter.PropertyIsLessThanOrEqualTo is None)
        self.assertEqual(rfilter.PropertyIsLessThanOrEqualTo.PropertyName, 'valueB')
        self.assertEqual(rfilter.PropertyIsLessThanOrEqualTo.Literal, '5000')

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_filter_lt(self):
        """
        Test the construction of a less-than Filter.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        rfilter = rule.create_filter('valueC', '<', '500')

        self.assertTrue(rfilter.PropertyIsEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLessThanOrEqualTo is None)
        self.assertTrue(rfilter.PropertyIsNotEqualTo is None)
        self.assertTrue(rfilter.PropertyIsGreaterThan is None)
        self.assertTrue(rfilter.PropertyIsGreaterThanOrEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLike is None)
        self.assertFalse(rfilter.PropertyIsLessThan is None)
        self.assertEqual(rfilter.PropertyIsLessThan.PropertyName, 'valueC')
        self.assertEqual(rfilter.PropertyIsLessThan.Literal, '500')

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_filter_gte(self):
        """
        Test the construction of a greater-than-or-equal Filter.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        rfilter = rule.create_filter('valueD', '>=', '100')

        self.assertTrue(rfilter.PropertyIsEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLessThanOrEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLessThan is None)
        self.assertTrue(rfilter.PropertyIsNotEqualTo is None)
        self.assertTrue(rfilter.PropertyIsGreaterThan is None)
        self.assertTrue(rfilter.PropertyIsLike is None)
        self.assertFalse(rfilter.PropertyIsGreaterThanOrEqualTo is None)
        self.assertEqual(rfilter.PropertyIsGreaterThanOrEqualTo.PropertyName, 'valueD')
        self.assertEqual(rfilter.PropertyIsGreaterThanOrEqualTo.Literal, '100')

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_filter_gt(self):
        """
        Test the construction of a greater-than Filter.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        rfilter = rule.create_filter('valueE', '>', '10')

        self.assertTrue(rfilter.PropertyIsEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLessThanOrEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLessThan is None)
        self.assertTrue(rfilter.PropertyIsGreaterThanOrEqualTo is None)
        self.assertTrue(rfilter.PropertyIsNotEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLike is None)
        self.assertFalse(rfilter.PropertyIsGreaterThan is None)
        self.assertEqual(rfilter.PropertyIsGreaterThan.PropertyName, 'valueE')
        self.assertEqual(rfilter.PropertyIsGreaterThan.Literal, '10')

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_filter_neq(self):
        """
        Test the construction of an inequality Filter.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        rfilter = rule.create_filter('valueF', '!=', '0.01')

        self.assertTrue(rfilter.PropertyIsEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLessThan is None)
        self.assertTrue(rfilter.PropertyIsLessThanOrEqualTo is None)
        self.assertTrue(rfilter.PropertyIsGreaterThan is None)
        self.assertTrue(rfilter.PropertyIsGreaterThanOrEqualTo is None)
        self.assertTrue(rfilter.PropertyIsLike is None)
        self.assertFalse(rfilter.PropertyIsNotEqualTo is None)
        self.assertEqual(rfilter.PropertyIsNotEqualTo.PropertyName, 'valueF')
        self.assertEqual(rfilter.PropertyIsNotEqualTo.Literal, '0.01')

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_filter_and(self):
        """
        Test the construction of a logical-and Filter.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)

        filter1 = sld.Filter(rule)
        filter1.PropertyIsGreaterThan = sld.PropertyCriterion(filter1, 'PropertyIsGreaterThan')
        filter1.PropertyIsGreaterThan.PropertyName = 'number'
        filter1.PropertyIsGreaterThan.Literal = '-10'

        filter2 = sld.Filter(rule)
        filter2.PropertyIsLessThanOrEqualTo = sld.PropertyCriterion(filter2, 'PropertyIsLessThanOrEqualTo')
        filter2.PropertyIsLessThanOrEqualTo.PropertyName = 'number'
        filter2.PropertyIsLessThanOrEqualTo.Literal = '10'

        rule.Filter = filter1 + filter2

        expected = [
          '<sld:Rule',
          'xmlns:sld="http://www.opengis.net/sld"',
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
          'xmlns:xlink="http://www.w3.org/1999/xlink"',
          'xmlns:ogc="http://www.opengis.net/ogc"',
          '<sld:Title>test rule</sld:Title><sld:PointSymbolizer><sld:Graphic><sld:Mark><sld:WellKnownName>square</sld:WellKnownName><sld:Fill><sld:CssParameter name="fill">#ff0000</sld:CssParameter></sld:Fill></sld:Mark></sld:Graphic></sld:PointSymbolizer><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>-10</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>10</ogc:Literal></ogc:PropertyIsLessThanOrEqualTo></ogc:And></ogc:Filter>'
        ]
        actual = etree.tostring(rule._node, with_tail=False)
        for item in expected:
          self.assertIn(item.encode('utf-8'), actual)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_filter_or(self):
        """
        Test the construction of a logical-or Filter.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)

        filter1 = sld.Filter(rule)
        filter1.PropertyIsGreaterThan = sld.PropertyCriterion(filter1, 'PropertyIsGreaterThan')
        filter1.PropertyIsGreaterThan.PropertyName = 'number'
        filter1.PropertyIsGreaterThan.Literal = '10'

        filter2 = sld.Filter(rule)
        filter2.PropertyIsLessThan = sld.PropertyCriterion(filter2, 'PropertyIsLessThan')
        filter2.PropertyIsLessThan.PropertyName = 'number'
        filter2.PropertyIsLessThan.Literal = '-10'

        rule.Filter = filter1 | filter2

        expected = [
          '<sld:Rule',
          'xmlns:sld="http://www.opengis.net/sld"',
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
          'xmlns:xlink="http://www.w3.org/1999/xlink"',
          'xmlns:ogc="http://www.opengis.net/ogc"',
          '<sld:Title>test rule</sld:Title><sld:PointSymbolizer><sld:Graphic><sld:Mark><sld:WellKnownName>square</sld:WellKnownName><sld:Fill><sld:CssParameter name="fill">#ff0000</sld:CssParameter></sld:Fill></sld:Mark></sld:Graphic></sld:PointSymbolizer><ogc:Filter><ogc:Or><ogc:PropertyIsGreaterThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>10</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:PropertyIsLessThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>-10</ogc:Literal></ogc:PropertyIsLessThan></ogc:Or></ogc:Filter>'
        ]
        actual = etree.tostring(rule._node, with_tail=False)
        for item in expected:
          self.assertIn(item.encode('utf-8'), actual)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_filter_and_or(self):
        """
        Test the construction of a logical-and combined with a logical-or Filter.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)

        filter1 = sld.Filter(rule)
        filter1.PropertyIsGreaterThan = sld.PropertyCriterion(filter1, 'PropertyIsGreaterThan')
        filter1.PropertyIsGreaterThan.PropertyName = 'number'
        filter1.PropertyIsGreaterThan.Literal = '10'

        filter2 = sld.Filter(rule)
        filter2.PropertyIsLessThan = sld.PropertyCriterion(filter2, 'PropertyIsLessThan')
        filter2.PropertyIsLessThan.PropertyName = 'number'
        filter2.PropertyIsLessThan.Literal = '-10'

        filter3 = sld.Filter(rule)
        filter3.PropertyIsEqualTo = sld.PropertyCriterion(filter3, 'PropertyIsEqualTo')
        filter3.PropertyIsEqualTo.PropertyName = 'value'
        filter3.PropertyIsEqualTo.Literal = 'yes'

        rule.Filter = filter1 + (filter2 | filter3)

        expected = [
          '<sld:Rule',
          'xmlns:sld="http://www.opengis.net/sld"',
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
          'xmlns:xlink="http://www.w3.org/1999/xlink"',
          'xmlns:ogc="http://www.opengis.net/ogc"',
          '<sld:Title>test rule</sld:Title><sld:PointSymbolizer><sld:Graphic><sld:Mark><sld:WellKnownName>square</sld:WellKnownName><sld:Fill><sld:CssParameter name="fill">#ff0000</sld:CssParameter></sld:Fill></sld:Mark></sld:Graphic></sld:PointSymbolizer><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>10</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:Or><ogc:PropertyIsLessThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>-10</ogc:Literal></ogc:PropertyIsLessThan><ogc:PropertyIsEqualTo><ogc:PropertyName>value</ogc:PropertyName><ogc:Literal>yes</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Or></ogc:And></ogc:Filter>'
        ]
        actual = etree.tostring(rule._node, with_tail=False, pretty_print=False)
        for item in expected:
          self.assertIn(item.encode('utf-8'), actual)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_rule_polysymbolizer1(self):
        """
        Test the parsing of the PolygonSymbolizer property.
        """
        sld_doc = copy.deepcopy(self._sld0)
        rule = sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        self.assertFalse(rule.PolygonSymbolizer is None)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_rule_polysymbolizer2(self):
        """
        Test the construction of a PolygonSymbolizer property.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        symbolizer = rule.create_symbolizer('Polygon')

        self.assertTrue(symbolizer.Fill is None)
        self.assertTrue(symbolizer.Stroke is None)
        self.assertTrue(symbolizer.Font is None)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_polysymoblizer_fill1(self):
        """
        Test the parsing of a Fill property.
        """
        sld_doc = copy.deepcopy(self._sld0)
        rule = sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        self.assertFalse(rule.PolygonSymbolizer.Fill is None)

        del rule.PolygonSymbolizer.Fill

        self.assertTrue(rule.PolygonSymbolizer.Fill is None)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_polysymbolizer_fill2(self):
        """
        Test the construction of a Fill property.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        symbolizer = rule.create_symbolizer('Polygon')
        fill = symbolizer.create_fill()

        self.assertFalse(fill.CssParameters is None)
        self.assertEqual(len(fill.CssParameters), 0)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_raster_symbolizer1(self):
        """
        Test the parsing of a RasterSymbolizer
        """

        sld_doc = copy.deepcopy(self._sld0)
        rule = sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.Rules[6]

        self.assertFalse(rule.RasterSymbolizer is None)

    def test_raster_symbolizer2(self):
        """
        Test the construction of a RasterSymbolizer
        """

        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        symbolizer = rule.create_symbolizer('Raster')
        symbolizer.create_colormap()

        self.assertEqual(len(symbolizer.ColorMap.ColorMapEntries), 0)
        sld_doc.normalize()

        self.assertTrue(sld_doc.validate())

    def test_raster_symbolizer_colormap1(self):
        """
        Test the parsing of a raster symbolizer color map
        """

        sld_doc = copy.deepcopy(self._sld0)
        rule = sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.Rules[6]
        entries = rule.RasterSymbolizer.ColorMap.ColorMapEntries

        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0].get_color(), '#FFFFFF')
        self.assertEqual(entries[1].get_quantity(), 0)
        self.assertEqual(entries[2].get_label(), '25 mm.')
        self.assertEqual(entries[0].get_opacity(), 0)
        
        del entries[1]

        self.assertEqual(len(entries), 2)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_raster_symbolizer_colormap2(self):
        """
        Test the construction of a raster symbolizer color map.
        """

        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        symbolizer = rule.create_symbolizer('Raster')
        colormap = symbolizer.create_colormap()

        self.assertEqual(len(colormap.ColorMapEntries), 0)

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_fill_cssparameter1(self):
        """
        Test the parsing of the CssParameter property.
        """
        fill = self._sld0.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0].PolygonSymbolizer.Fill

        self.assertFalse(fill.CssParameters is None)
        self.assertEqual(len(fill.CssParameters), 1)

        fill = self._sld0.NamedLayer.UserStyle.FeatureTypeStyle.Rules[5].LineSymbolizer.Stroke

        self.assertFalse(fill.CssParameters is None)
        self.assertEqual(len(fill.CssParameters), 2)

    def test_fill_cssparameter2(self):
        """
        Test the construction of the CssParameter property.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule('test rule', sld.PointSymbolizer)
        symbolizer = rule.create_symbolizer('Polygon')
        fill = symbolizer.create_fill()
        fill.create_cssparameter('fill', '#ffffff')

        self.assertEqual(len(fill.CssParameters), 1)
        self.assertEqual(fill.CssParameters[0].Name, 'fill')
        self.assertEqual(fill.CssParameters[0].Value, '#ffffff')

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_rule_scale_denominators(self):
        """
        Test the parsing of the MaxScaleDenominator & MinScaleDenominator properties.
        """
        sld_doc = copy.deepcopy(self._sld0)
        rule = sld_doc.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        self.assertTrue(rule.MinScaleDenominator is None)
        self.assertFalse(rule.MaxScaleDenominator is None)

        expected = '20000'
        self.assertEqual(rule.MaxScaleDenominator, expected, "MaxScaleDominator was '%s', not '%s'" % (rule.MaxScaleDenominator, expected,))
        expected = '15000'
        rule.MaxScaleDenominator = expected
        self.assertEqual(rule.MaxScaleDenominator, expected, "MaxScaleDominator was '%s', not '%s'" % (rule.MaxScaleDenominator, expected,))

        del rule.MaxScaleDenominator
        self.assertTrue(rule.MaxScaleDenominator is None)

        expected = '15000'
        rule.MinScaleDenominator = expected
        self.assertEqual(rule.MinScaleDenominator, expected, "MinScaleDenominator was '%s', not '%s'" % (rule.MinScaleDenominator, expected,))

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())

    def test_scale_denominators(self):
        """
        Test the construction of the MaxScaleDenominator & MinScaleDenominator properties.
        """
        sld_doc = copy.deepcopy(self._sld1)
        namedlayer = sld_doc.create_namedlayer('test named layer')
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()

        rule1 = featuretypestyle.create_rule('test rule 1', sld.PointSymbolizer)
        self.assertTrue(rule1.MinScaleDenominator is None)
        self.assertTrue(rule1.MaxScaleDenominator is None)

        rule2 = featuretypestyle.create_rule('test rule 2', sld.PointSymbolizer, '10000', '20000')
        self.assertFalse(rule2.MinScaleDenominator is None)
        self.assertFalse(rule2.MaxScaleDenominator is None)
        self.assertEqual(rule2.MinScaleDenominator, '10000')
        self.assertEqual(rule2.MaxScaleDenominator, '20000')

        sld_doc.normalize()
        self.assertTrue(sld_doc.validate())
        

if __name__ == '__main__':
    unittest.main()
