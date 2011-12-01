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
from lxml.etree import parse, Element, XMLSchema, XMLSyntaxError
import urllib2
from tempfile import TemporaryFile
import os, copy, logging

class SLDNode(object):
    def __init__(self, parent, nsmap):
        self._parent = parent
        self._nsmap = nsmap
        self._node = None
   
    @staticmethod
    def makeproperty(ns, node, cls=None, name=None):
        def get_property(self):
            if cls is None:
                xpath = '%s:%s' % (ns, name)
            else:
                xpath = '%s:%s' % (ns, cls.__name__)

            xpath = self._node.xpath(xpath, namespaces=self._nsmap)
            if len(xpath) == 1:
                if cls is None:
                    return xpath[0].text
                else:
                    elem = cls.__new__(cls)
                    cls.__init__(elem, self._node, self._nsmap)
                    return elem
            else:
                return None

        def set_property(self, value):
            if cls is None:
                xpath = '%s:%s' % (ns, name)
            else:
                xpath = '%s:%s' % (ns, cls.__name__)

            xpath = self._node.xpath(xpath, namespaces=self._nsmap)
            if len(xpath) == 1:
                if cls is None:
                    xpath[0].text = value
                else:
                    xpath[0] = value._node
            else:
                if cls is None:
                    elem = self._node.makeelement('{%s}%s' % (self._nsmap[ns], name), nsmap=self._nsmap)
                    elem.text = value
                    self._node.append(elem)
                else:
                    self._node.append(value._node)

        def del_property(self):
            if cls is None:
                xpath = '%s:%s' % (ns, name)
            else:
                xpath = '%s:%s' % (ns, cls.__name__)

            xpath = self._node.xpath(xpath, namespaces=self._nsmap)
            if len(xpath) == 1:
                self._node.remove(xpath[0])


        return property(get_property, set_property, del_property, "")


    def get_or_create_element(self, ns, name):
        if len(self._node.xpath('%s:%s' % (ns, name), namespaces=self._nsmap)) >= 1:
            return getattr(self, name)

        return self.create_element(ns, name)

    def create_element(self, ns, name):
        elem = self._node.makeelement('{%s}%s' % (self._nsmap[ns], name), nsmap=self._nsmap)
        self._node.append(elem)

        return getattr(self, name)


class PropertyCriterion(SLDNode):
    def __init__(self, parent, nsmap, name):
        super(PropertyCriterion, self).__init__(parent, nsmap)
        xpath = self._parent.xpath('ogc:'+name, namespaces=self._nsmap)
        if len(xpath) < 1:
            self._node = self._parent.makeelement('{%s}%s' % (self._nsmap['ogc'], name), nsmap=self._nsmap)
            self._parent.append(self._node)
        else:
            self._node = xpath[0]

        setattr(self.__class__, 'PropertyName', SLDNode.makeproperty('ogc', self._node, name='PropertyName'))
        setattr(self.__class__, 'Literal', SLDNode.makeproperty('ogc', self._node, name='Literal'))


class Filter(SLDNode):
    def __init__(self, parent, nsmap):
        super(Filter, self).__init__(parent, nsmap)
        xpath = self._parent.xpath('ogc:Filter', namespaces=self._nsmap)
        if len(xpath) == 1:
            self._node = xpath[0]
        else:
            self._node = self._parent.makeelement('{%s}Filter' % self._nsmap['ogc'], nsmap=self._nsmap)

    def __add__(x, y):
        elem = x._node.makeelement('{%s}And' % x._nsmap['ogc'])
        elem.append(copy.copy(x._node[0]))
        elem.append(copy.copy(y._node[0]))

        f = Filter(x._parent, x._nsmap)
        f._node.append(elem)

        return f

    def __or__(x, y):
        elem = x._node.makeelement('{%s}Or' % x._nsmap['ogc'])
        elem.append(copy.copy(x._node[0]))
        elem.append(copy.copy(y._node[0]))

        f = Filter(x._parent, x._nsmap)
        f._node.append(elem)

        return f

    def __getattr__(self, name):
        if not name.startswith('PropertyIs'):
            raise AttributeError('Property name must be one of: PropertyIsEqualTo, PropertyIsNotEqualTo, PropertyIsLessThan, PropertyIsLessThanOrEqualTo, PropertyIsGreaterThan, PropertyIsGreaterThanOrEqualTo, PropertyIsLike.')
        xpath = self._node.xpath('ogc:'+name, namespaces=self._nsmap)
        if len(xpath) == 0:
            return None

        return PropertyCriterion(self._node, self._nsmap, name)

    def __setattr__(self, name, value):
        if not name.startswith('PropertyIs'):
            object.__setattr__(self, name, value)
            return

        xpath = self._node.xpath('ogc:'+name, namespaces=self._nsmap)
        if len(xpath) > 0:
            xpath[0] = value
        else:
            elem = self._node.makeelement('{%s}%s' % (self._nsmap['ogc'], name), nsmap=self._nsmap)
            self._node.append(elem)

    def __delattr__(self, name):
        xpath = self._node.xpath('ogc:'+name, namespaces=self._nsmap)
        if len(xpath) > 0:
            self._node.remove(xpath[0])


class Rule(SLDNode):
    def __init__(self, parent, nsmap, index):
        super(Rule, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('sld:Rule', namespaces=self._nsmap)[index]

        setattr(self.__class__, 'Title', SLDNode.makeproperty('sld', self._node, name='Title'))
        setattr(self.__class__, 'Filter', SLDNode.makeproperty('ogc', self._node, cls=Filter))
        #setattr(self.__class__, 'PolygonSymbolizer', SLDNode.makeproperty('sld', self._node, cls=PolygonSymbolizer))
        #setattr(self.__class__, 'LineSymbolizer', SLDNode.makeproperty('sld', self._node, cls=LineSymbolizer))

    def create_filter(self, propname=None, comparitor=None, value=None):
        if propname is None or comparitor is None or value is None:
            return None

        rfilter = self.create_element('ogc', 'Filter')
        ftype = None
        if comparitor == '==':
            ftype = 'PropertyIsEqualTo'
        elif comparitor == '<=':
            ftype = 'PropertyIsLessThanOrEqualTo'
        elif comparitor == '<':
            ftype = 'PropertyIsLessThan'
        elif comparitor == '>=':
            ftype = 'PropertyIsGreaterThanOrEqualTo'
        elif comparitor == '>':
            ftype = 'PropertyIsGreaterThan'
        elif comparitor == '!=':
            ftype = 'PropertyIsNotEqualTo'
        elif comparitor == '%':
            ftype = 'PropertyIsLike'

        if not ftype is None:
            prop = PropertyCriterion(rfilter._node, self._nsmap, ftype)
            prop.PropertyName = propname
            if not value is None:
                prop.Literal = value
            setattr(rfilter, ftype, prop)

        return rfilter
        

class Rules(SLDNode):
    def __init__(self, parent, nsmap):
        super(Rules, self).__init__(parent, nsmap)
        self._node = None
        self._nodes = self._parent.xpath('sld:Rule', namespaces=self._nsmap)

    def __len__(self):
        return len(self._nodes)

    def __getitem__(self, key):
        return Rule(self._parent, self._nsmap, key)

    def __setitem__(self, key, value):
        if isinstance(value, Rule):
            self._nodes.replace(self._nodes[key], value._node)
        elif isinstance(value, Element):
            self._nodes.replace(self._nodes[key], value)
   
    def __delitem__(self, key):
        self._nodes.remove(self._nodes[key])


class FeatureTypeStyle(SLDNode):
    def __init__(self, parent, nsmap):
        super(FeatureTypeStyle, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('sld:FeatureTypeStyle', namespaces=self._nsmap)[0]

    @property
    def Rules(self):
        return Rules(self._node, self._nsmap)

    def create_rule(self):
        elem = self._node.makeelement('{%s}Rule' % self._nsmap['sld'], nsmap=self._nsmap)
        self._node.append(elem)

        return Rule(self._node, self._nsmap, len(self._node)-1)


class UserStyle(SLDNode):
    def __init__(self, parent, nsmap):
        super(UserStyle, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('sld:UserStyle', namespaces=self._nsmap)[0]

        setattr(self.__class__, 'Title', SLDNode.makeproperty('sld', self._node, name='Title'))
        setattr(self.__class__, 'Abstract', SLDNode.makeproperty('sld', self._node, name='Abstract'))
        setattr(self.__class__, 'FeatureTypeStyle', SLDNode.makeproperty('sld', self._node, cls=FeatureTypeStyle))

    def create_featuretypestyle(self):
        return self.get_or_create_element('sld', 'FeatureTypeStyle')


class NamedLayer(SLDNode):
    def __init__(self, parent, nsmap):
        super(NamedLayer, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('sld:NamedLayer', namespaces=self._nsmap)[0]

        setattr(self.__class__, 'UserStyle', SLDNode.makeproperty('sld', self._node, cls=UserStyle))

    @property
    def Name(self):
        return self._node.xpath('sld:Name', namespaces=self._nsmap)[0].text

    def create_userstyle(self):
        return self.get_or_create_element('sld', 'UserStyle')


class StyledLayerDescriptor(SLDNode):
    def __init__(self, sld_file=None):
        super(StyledLayerDescriptor, self).__init__(None,None)

        localschema = TemporaryFile()
        schema_url = 'http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd'
        resp = urllib2.urlopen(schema_url)
        localschema.write(resp.read())
        resp.close()
        localschema.seek(0)

        theschema = parse(localschema)
        localschema.close()

        self._schema = XMLSchema(theschema)

        if not sld_file is None:
            self._node = parse(sld_file)
            self._nsmap = self._node.getroot().nsmap

            ns = self._nsmap.pop(None)
            self._nsmap['sld'] = ns

            if not self._schema.validate(self._node):
                logging.warn('SLD File "%s" does not validate against the SLD schema.', sld_file)
        else:
            self._nsmap = {
                'sld':"http://www.opengis.net/sld",
                'ogc':"http://www.opengis.net/ogc",
                'xlink':"http://www.w3.org/1999/xlink",
                'xsi':"http://www.w3.org/2001/XMLSchema-instance"
            }
            self._node = Element("{%s}StyledLayerDescriptor" % self._nsmap['sld'], nsmap=self._nsmap)

        setattr(self.__class__, 'NamedLayer', SLDNode.makeproperty('sld', self._node, cls=NamedLayer))

    @property
    def version(self):
        """
        Get the SLD version.
        """
        return self._node.getroot().get('version')

    @property
    def xmlns(self):
        """
        Get the XML Namespace.
        """
        return self._node.getroot().nsmap[None]

    def create_namedlayer(self):
        return self.get_or_create_element('sld', 'NamedLayer')
