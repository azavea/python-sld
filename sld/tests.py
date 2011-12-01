"""
   Copyright 2011 David Zwarg <dzwarg@azavea.com>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from unittest import TestCase
from models import *
import copy
from lxml import etree

class SLD_Test(TestCase):
    _sld0 = None
    _sld1 = None
    def setUp(self):
        # Couldn't get this to work in setUpClass, but it would be better in there
        if SLD_Test._sld0 is None:
            SLD_Test._sld0 = StyledLayerDescriptor('sld/test/style.sld')
            SLD_Test._sld1 = StyledLayerDescriptor()

    def test_constructor1(self):
        sld = StyledLayerDescriptor()

        self.assertTrue( 'sld' in sld._nsmap )

        expected = """<sld:StyledLayerDescriptor xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"/>"""
        actual = etree.tostring(sld._node, with_tail=False)
        self.assertEqual(actual, expected)
        

    def test_constructor2(self):
        try:
            sld = StyledLayerDescriptor('junk')
            self.fail("Error")
        except:
            # Good, failure on a junk file.
            pass

    def test_sld0_version(self):
        self.assertEqual( self._sld0.version, "1.0.0" )

    def test_sld0_ns(self):
        self.assertEqual( self._sld0.xmlns, 'http://www.opengis.net/sld' )

    def test_sld0_namedlayer1(self):
        self.assertTrue( isinstance(self._sld0.NamedLayer, NamedLayer), "NamedLayer property is not the proper class.")

    def test_sld0_namedlayer2(self):
        self.assertTrue( self._sld1.NamedLayer is None )

        sld = copy.deepcopy(self._sld1)

        sld.create_namedlayer()
        self.assertFalse( sld.NamedLayer is None )

    def test_namedlayer_name(self):
        expected = 'poptot'
        self.assertEqual( self._sld0.NamedLayer.Name, expected, "NamedLayer was named '%s', not '%s'" % (self._sld0.NamedLayer.Name, expected,))

    def test_namedlayer_userstyle1(self):
        self.assertTrue( isinstance(self._sld0.NamedLayer.UserStyle, UserStyle), "UserStyle property is not the proper class.")

    def test_namedlayer_userstyle2(self):
        sld = copy.deepcopy(self._sld1)

        sld.create_namedlayer()

        self.assertTrue( sld.NamedLayer.UserStyle is None)

        sld.NamedLayer.create_userstyle()

        self.assertFalse( sld.NamedLayer.UserStyle is None)

    def test_userstyle_title1(self):
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

    def test_userstyle_title2(self):
        sld = copy.deepcopy(self._sld1)
        sld.create_namedlayer()
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

    def test_userstyle_abstract1(self):
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

    def test_userstyle_abstract2(self):
        sld = copy.deepcopy(self._sld1)
        sld.create_namedlayer()
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

    def test_userstyle_featuretypestyle1(self):
        self.assertTrue( isinstance(self._sld0.NamedLayer.UserStyle.FeatureTypeStyle, FeatureTypeStyle), "FeatureTypeStyle property is not the proper class.")

    def test_userstyle_featuretypestyle2(self):
        sld = copy.deepcopy(self._sld1)
        sld.create_namedlayer()
        sld.NamedLayer.create_userstyle()

        self.assertTrue( sld.NamedLayer.UserStyle.FeatureTypeStyle is None )

        sld.NamedLayer.UserStyle.create_featuretypestyle()

        self.assertFalse( sld.NamedLayer.UserStyle.FeatureTypeStyle is None )

    def test_featuretypestyle_rules1(self):
        rules = self._sld0.NamedLayer.UserStyle.FeatureTypeStyle.Rules
        self.assertEqual( len(rules), 6 )
        self.assertTrue( isinstance(rules[0], Rule), "Rule item in list is not the proper class." )

    def test_featuretypestyle_rules2(self):
        sld = copy.deepcopy(self._sld1)
        sld.create_namedlayer()
        sld.NamedLayer.create_userstyle()
        sld.NamedLayer.UserStyle.create_featuretypestyle()

        rules = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules
        self.assertEqual( len(rules), 0 )

        sld.NamedLayer.UserStyle.FeatureTypeStyle.create_rule()
        rules = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules

        self.assertEqual( len(rules), 1 )

    def test_rule_title1(self):
        sld = copy.deepcopy(self._sld0)
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

    def test_rule_title2(self):
        sld = copy.deepcopy(self._sld1)
        sld.create_namedlayer()
        sld.NamedLayer.create_userstyle()
        sld.NamedLayer.UserStyle.create_featuretypestyle()
        sld.NamedLayer.UserStyle.FeatureTypeStyle.create_rule()

        rule = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        self.assertTrue( rule.Title is None )

        expected = "> 999"
        rule.Title = expected
        self.assertEqual( rule.Title, expected )

        expected = """<sld:Rule xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"><sld:Title>&gt; 999</sld:Title></sld:Rule>"""
        actual = etree.tostring(rule._node, with_tail=False)
        self.assertEqual( actual, expected, actual )

    def test_rule_filter1(self):
        sld = copy.deepcopy(self._sld0)
        rule = sld.NamedLayer.UserStyle.FeatureTypeStyle.Rules[0]

        self.assertFalse( rule.Filter.PropertyIsGreaterThanOrEqualTo is None )

        self.assertEqual( rule.Filter.PropertyIsGreaterThanOrEqualTo.PropertyName, 'number' )
        self.assertEqual( rule.Filter.PropertyIsGreaterThanOrEqualTo.Literal, '880' )

    def test_rule_filter_none(self):
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer()
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule()
        rfilter = rule.create_filter()

        self.assertTrue( rfilter is None )

    def test_filter_eq(self):
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer()
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule()
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

    def test_filter_lte(self):
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer()
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule()
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

    def test_filter_lt(self):
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer()
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule()
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

    def test_filter_gte(self):
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer()
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule()
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

    def test_filter_gt(self):
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer()
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule()
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

    def test_filter_neq(self):
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer()
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule()
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

    def test_filter_and(self):
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer()
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule()
        
        filter1 = Filter(rule._node, rule._nsmap)
        filter1.PropertyIsGreaterThan = PropertyCriterion(filter1._node, filter1._nsmap, 'PropertyIsGreaterThan')
        filter1.PropertyIsGreaterThan.PropertyName = 'number'
        filter1.PropertyIsGreaterThan.Literal = '-10'

        filter2 = Filter(rule._node, rule._nsmap)
        filter2.PropertyIsLessThanOrEqualTo = PropertyCriterion(filter2._node, filter2._nsmap, 'PropertyIsLessThanOrEqualTo')
        filter2.PropertyIsLessThanOrEqualTo.PropertyName = 'number'
        filter2.PropertyIsLessThanOrEqualTo.Literal = '10'

        rule.Filter = filter1 + filter2

        expected = """<sld:Rule xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>-10</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>10</ogc:Literal></ogc:PropertyIsLessThanOrEqualTo></ogc:And></ogc:Filter></sld:Rule>"""
        actual = etree.tostring(rule._node, with_tail=False)
        self.assertEqual(actual, expected)

    def test_filter_or(self):
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer()
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule()
        
        filter1 = Filter(rule._node, rule._nsmap)
        filter1.PropertyIsGreaterThan = PropertyCriterion(filter1._node, filter1._nsmap, 'PropertyIsGreaterThan')
        filter1.PropertyIsGreaterThan.PropertyName = 'number'
        filter1.PropertyIsGreaterThan.Literal = '10'

        filter2 = Filter(rule._node, rule._nsmap)
        filter2.PropertyIsLessThan= PropertyCriterion(filter2._node, filter2._nsmap, 'PropertyIsLessThan')
        filter2.PropertyIsLessThan.PropertyName = 'number'
        filter2.PropertyIsLessThan.Literal = '-10'

        rule.Filter = filter1 | filter2

        expected = """<sld:Rule xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"><ogc:Filter><ogc:Or><ogc:PropertyIsGreaterThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>10</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:PropertyIsLessThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>-10</ogc:Literal></ogc:PropertyIsLessThan></ogc:Or></ogc:Filter></sld:Rule>"""
        actual = etree.tostring(rule._node, with_tail=False)
        self.assertEqual(actual, expected)

    def test_filter_and_or(self):
        sld = copy.deepcopy(self._sld1)
        namedlayer = sld.create_namedlayer()
        userstyle = namedlayer.create_userstyle()
        featuretypestyle = userstyle.create_featuretypestyle()
        rule = featuretypestyle.create_rule()
        
        filter1 = Filter(rule._node, rule._nsmap)
        filter1.PropertyIsGreaterThan = PropertyCriterion(filter1._node, filter1._nsmap, 'PropertyIsGreaterThan')
        filter1.PropertyIsGreaterThan.PropertyName = 'number'
        filter1.PropertyIsGreaterThan.Literal = '10'

        filter2 = Filter(rule._node, rule._nsmap)
        filter2.PropertyIsLessThan = PropertyCriterion(filter2._node, filter2._nsmap, 'PropertyIsLessThan')
        filter2.PropertyIsLessThan.PropertyName = 'number'
        filter2.PropertyIsLessThan.Literal = '-10'

        filter3 = Filter(rule._node, rule._nsmap)
        filter3.PropertyIsEqualTo = PropertyCriterion(filter3._node, filter3._nsmap, 'PropertyIsEqualTo')
        filter3.PropertyIsEqualTo.PropertyName = 'value'
        filter3.PropertyIsEqualTo.Literal = 'yes'

        rule.Filter = filter1 + (filter2 | filter3)

        expected = """<sld:Rule xmlns:sld="http://www.opengis.net/sld" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc"><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>10</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:Or><ogc:PropertyIsLessThan><ogc:PropertyName>number</ogc:PropertyName><ogc:Literal>-10</ogc:Literal></ogc:PropertyIsLessThan><ogc:PropertyIsEqualTo><ogc:PropertyName>value</ogc:PropertyName><ogc:Literal>yes</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Or></ogc:And></ogc:Filter></sld:Rule>"""
        actual = etree.tostring(rule._node, with_tail=False, pretty_print=False)
        self.assertEqual(actual, expected)


