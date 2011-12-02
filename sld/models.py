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
from lxml.etree import parse, Element, XMLSchema, XMLSyntaxError, tostring
import urllib2
from tempfile import NamedTemporaryFile
import os, copy, logging, settings
from StringIO import StringIO

class SLDNode(object):
    """
    A base class for all python objects that relate directly to SLD elements.
    An SLDNode contains references to the underlying parent node, underlying
    element node, and the namespace map.

    The SLDNode base class also contains utility methods to construct properties
    for child SLDNode objects.
    """

    # The defined namespaces in SLD documents.
    _nsmap = {
        'sld':"http://www.opengis.net/sld",
        'ogc':"http://www.opengis.net/ogc",
        'xlink':"http://www.w3.org/1999/xlink",
        'xsi':"http://www.w3.org/2001/XMLSchema-instance"
    }

    def __init__(self, parent):
        """
        Create a new SLDNode. It is not necessary to call this directly, because
        all child classes should initialize the SLDNode internally.

        @type  parent: etree.Element
        @param parent: The parent element of this node.
        @type   nsmap: dict
        @param  nsmap: The dictionary of namespaces.
        """
        self._parent = parent
        self._node = None
   
    @staticmethod
    def makeproperty(ns, node, cls=None, name=None, docstring=None):
        """
        Make a property on an instance of an SLDNode, which relates to a specific
        child node in the SLD specification.
        """
        def get_property(self):
            """
            A generic property getter.
            """
            if cls is None:
                xpath = '%s:%s' % (ns, name)
            else:
                xpath = '%s:%s' % (ns, cls.__name__)

            xpath = self._node.xpath(xpath, namespaces=SLDNode._nsmap)
            if len(xpath) == 1:
                if cls is None:
                    return xpath[0].text
                else:
                    elem = cls.__new__(cls)
                    cls.__init__(elem, self._node)
                    return elem
            else:
                return None

        def set_property(self, value):
            """
            A generic property setter.
            """
            if cls is None:
                xpath = '%s:%s' % (ns, name)
            else:
                xpath = '%s:%s' % (ns, cls.__name__)

            xpath = self._node.xpath(xpath, namespaces=SLDNode._nsmap)
            if len(xpath) == 1:
                if cls is None:
                    xpath[0].text = value
                else:
                    xpath[0] = value._node
            else:
                if cls is None:
                    elem = self._node.makeelement('{%s}%s' % (SLDNode._nsmap[ns], name), nsmap=SLDNode._nsmap)
                    elem.text = value
                    self._node.append(elem)
                else:
                    self._node.append(value._node)

        def del_property(self):
            """
            A generic property deleter.
            """
            if cls is None:
                xpath = '%s:%s' % (ns, name)
            else:
                xpath = '%s:%s' % (ns, cls.__name__)

            xpath = self._node.xpath(xpath, namespaces=SLDNode._nsmap)
            if len(xpath) == 1:
                self._node.remove(xpath[0])

        return property(get_property, set_property, del_property, docstring)


    def get_or_create_element(self, ns, name):
        """
        Attempt to get the only child element from this SLDNode. If the node
        does not exist, create the element, attach it to the DOM, and return
        the class object that wraps the node.
        """
        if len(self._node.xpath('%s:%s' % (ns, name), namespaces=SLDNode._nsmap)) == 1:
            return getattr(self, name)

        return self.create_element(ns, name)

    def create_element(self, ns, name):
        """
        Create
        """
        elem = self._node.makeelement('{%s}%s' % (SLDNode._nsmap[ns], name), nsmap=SLDNode._nsmap)
        self._node.append(elem)

        return getattr(self, name)


class CssParameter(SLDNode):
    def __init__(self, parent, index):
        super(CssParameter, self).__init__(parent)
        self._node = self._parent.xpath('sld:CssParameter', namespaces=SLDNode._nsmap)[index]

    def get_name(self):
        return self._node.attrib['name']

    def set_name(self, value):
        self._node.attrib['name'] = value

    def del_name(self):
        del self._node.attrib['name']

    Name = property(get_name, set_name, del_name, "")

    def get_value(self):
        return self._node.text

    def set_value(self, value):
        self._node.text = value

    def del_value(self):
        self._node.clear()

    Value = property(get_value, set_value, del_value, "")


class CssParameters(SLDNode):
    def __init__(self, parent):
        super(CssParameters, self).__init__(parent)
        self._node = None
        self._nodes = self._parent.xpath('sld:CssParameter', namespaces=SLDNode._nsmap)

    def __len__(self):
        return len(self._nodes)

    def __getitem__(self, key):
        return CssParameter(self._parent, key)

    def __setitem__(self, key, value):
        if isinstance(value, CssParameter):
            self._nodes.replace(self._nodes[key], value._node)
        elif isinstance(value, Element):
            self._nodes.replace(self._nodes[key], value)
   
    def __delitem__(self, key):
        self._nodes.remove(self._nodes[key])


class StyleItem(SLDNode):
    def __init__(self, parent, name):
        super(StyleItem, self).__init__(parent)
        xpath = self._parent.xpath('sld:'+name, namespaces=SLDNode._nsmap)
        if len(xpath) < 1:
            self._node = self._parent.makeelement('{%s}%s' % (SLDNode._nsmap['sld'], name), nsmap=SLDNode._nsmap)
            self._parent.append(self._node)
        else:
            self._node = xpath[0]

    @property
    def CssParameters(self):
        return CssParameters(self._node)

    def create_cssparameter(self, name=None, value=None):
        elem = self._node.makeelement('{%s}CssParameter' % SLDNode._nsmap['sld'], nsmap=SLDNode._nsmap)
        self._node.append(elem)

        if not (name is None or value is None):
            elem.attrib['name'] = name
            elem.text = value

        return CssParameter(self._node, len(self._node)-1)
    

class Fill(StyleItem):
    def __init__(self, parent):
        super(Fill, self).__init__(parent, 'Fill')


class Font(StyleItem):
    def __init__(self, parent):
        super(Font, self).__init__(parent, 'Font')


class Stroke(StyleItem):
    def __init__(self, parent):
        super(Stroke, self).__init__(parent, 'Stroke')


class Symbolizer(SLDNode):
    def __init__(self, parent, name):
        super(Symbolizer, self).__init__(parent)

        if name[len(name)-1] == '*':
            name = name[0:-1] + 'Symbolizer'

        xpath = self._parent.xpath('sld:%s' % name, namespaces=SLDNode._nsmap)
        if len(xpath) < 1:
            self._node = self._parent.makeelement('{%s}%s' % (SLDNode._nsmap['sld'], name), nsmap=SLDNode._nsmap)
            self._parent.append(self._node)
        else:
            self._node = xpath[0]

        setattr(self.__class__, 'Fill', SLDNode.makeproperty('sld', self._node, cls=Fill))
        setattr(self.__class__, 'Font', SLDNode.makeproperty('sld', self._node, cls=Font))
        setattr(self.__class__, 'Stroke', SLDNode.makeproperty('sld', self._node, cls=Stroke))

    def create_fill(self):
        return self.create_element('sld', 'Fill')

    def create_font(self):
        return self.create_element('sld', 'Font')

    def create_stroke(self):
        return self.create_element('sld', 'Stroke')


class PolygonSymbolizer(Symbolizer):
    def __init__(self, parent):
        super(PolygonSymbolizer, self).__init__(parent, 'Polygon*')


class LineSymbolizer(Symbolizer):
    def __init__(self, parent):
        super(LineSymbolizer, self).__init__(parent, 'Line*')


class TextSymbolizer(Symbolizer):
    def __init__(self, parent): 
        super(TextSymbolizer, self).__init__(parent, 'Text*')


class Mark(Symbolizer):
    def __init__(self, parent):
        super(Mark, self).__init__(parent, 'Mark')

        setattr(self.__class__, 'WellKnownName', SLDNode.makeproperty('sld', self._node, name='WellKnownName'))


class Graphic(SLDNode):
    def __init__(self, parent):
        super(Graphic, self).__init__(parent)
        xpath = self._parent.xpath('sld:Graphic', namespaces=SLDNode._nsmap)
        if len(xpath) < 1:
            self._node = self._parent.makeelement('{%s}Graphic' % SLDNode._nsmap['sld'], nsmap=SLDNode._nsmap)
            self._parent.append(self._node)
        else:
            self._node = xpath[0]

        setattr(self.__class__, 'Mark', SLDNode.makeproperty('sld', self._node, cls=Mark))
        setattr(self.__class__, 'Opacity', SLDNode.makeproperty('sld', self._node, name='Opacity'))
        setattr(self.__class__, 'Size', SLDNode.makeproperty('sld', self._node, name='Size'))
        setattr(self.__class__, 'Rotation', SLDNode.makeproperty('sld', self._node, name='Rotation'))


class PointSymbolizer(SLDNode):
    def __init__(self, parent):
        super(PointSymbolizer, self).__init__(parent)
        xpath = self._parent.xpath('sld:PointSymbolizer', namespaces=SLDNode._nsmap)
        if len(xpath) < 1:
            self._node = self._parent.makeelement('{%s}PointSymbolizer' % SLDNode._nsmap['sld'], nsmap=SLDNode._nsmap)
            self._parent.append(self._node)
        else:
            self._node = xpath[0]

        setattr(self.__class__, 'Graphic', SLDNode.makeproperty('sld', self._node, cls=Graphic))


class PropertyCriterion(SLDNode):
    def __init__(self, parent, name):
        super(PropertyCriterion, self).__init__(parent)
        xpath = self._parent.xpath('ogc:'+name, namespaces=SLDNode._nsmap)
        if len(xpath) < 1:
            self._node = self._parent.makeelement('{%s}%s' % (SLDNode._nsmap['ogc'], name), nsmap=SLDNode._nsmap)
            self._parent.append(self._node)
        else:
            self._node = xpath[0]

        setattr(self.__class__, 'PropertyName', SLDNode.makeproperty('ogc', self._node, name='PropertyName'))
        setattr(self.__class__, 'Literal', SLDNode.makeproperty('ogc', self._node, name='Literal'))


class Filter(SLDNode):
    def __init__(self, parent):
        super(Filter, self).__init__(parent)
        xpath = self._parent.xpath('ogc:Filter', namespaces=SLDNode._nsmap)
        if len(xpath) == 1:
            self._node = xpath[0]
        else:
            self._node = self._parent.makeelement('{%s}Filter' % SLDNode._nsmap['ogc'], nsmap=SLDNode._nsmap)

    def __add__(self, other):
        if not self._node.getparent() is None:
            self._node.getparent().remove(self._node)
        elem = self._node.makeelement('{%s}And' % SLDNode._nsmap['ogc'])
        elem.append(copy.copy(self._node[0]))
        elem.append(copy.copy(other._node[0]))

        f = Filter(self._parent)
        f._node.append(elem)

        return f

    def __or__(x, y):
        elem = x._node.makeelement('{%s}Or' % x._nsmap['ogc'])
        elem.append(copy.copy(x._node[0]))
        elem.append(copy.copy(y._node[0]))

        f = Filter(x._parent)
        f._node.append(elem)

        return f

    def __getattr__(self, name):
        if not name.startswith('PropertyIs'):
            raise AttributeError('Property name must be one of: PropertyIsEqualTo, PropertyIsNotEqualTo, PropertyIsLessThan, PropertyIsLessThanOrEqualTo, PropertyIsGreaterThan, PropertyIsGreaterThanOrEqualTo, PropertyIsLike.')
        xpath = self._node.xpath('ogc:'+name, namespaces=SLDNode._nsmap)
        if len(xpath) == 0:
            return None

        return PropertyCriterion(self._node, name)

    def __setattr__(self, name, value):
        if not name.startswith('PropertyIs'):
            object.__setattr__(self, name, value)
            return

        xpath = self._node.xpath('ogc:'+name, namespaces=SLDNode._nsmap)
        if len(xpath) > 0:
            xpath[0] = value
        else:
            elem = self._node.makeelement('{%s}%s' % (SLDNode._nsmap['ogc'], name), nsmap=SLDNode._nsmap)
            self._node.append(elem)

    def __delattr__(self, name):
        xpath = self._node.xpath('ogc:'+name, namespaces=SLDNode._nsmap)
        if len(xpath) > 0:
            self._node.remove(xpath[0])


class Rule(SLDNode):
    def __init__(self, parent, index, title=None):
        super(Rule, self).__init__(parent)
        self._node = self._parent.xpath('sld:Rule', namespaces=SLDNode._nsmap)[index]

        setattr(self.__class__, 'Title', SLDNode.makeproperty('sld', self._node, name='Title'))
        setattr(self.__class__, 'Filter', SLDNode.makeproperty('ogc', self._node, cls=Filter))
        setattr(self.__class__, 'PolygonSymbolizer', SLDNode.makeproperty('sld', self._node, cls=PolygonSymbolizer))
        setattr(self.__class__, 'LineSymbolizer', SLDNode.makeproperty('sld', self._node, cls=LineSymbolizer))
        setattr(self.__class__, 'TextSymbolizer', SLDNode.makeproperty('sld', self._node, cls=TextSymbolizer))
        setattr(self.__class__, 'PointSymbolizer', SLDNode.makeproperty('sld', self._node, cls=PointSymbolizer))

    def normalize(self):
        order = ['sld:Title','ogc:Filter','sld:PolygonSymbolizer', 
            'sld:LineSymbolizer', 'sld:TextSymbolizer', 'sld:PointSymbolizer']
        for item in order:
            xpath = self._node.xpath(item, namespaces=SLDNode._nsmap)
            for xitem in xpath:
                # move this to the end
                self._node.remove(xitem)
                self._node.append(xitem)

        # no need to normalize children

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
            prop = PropertyCriterion(rfilter._node, ftype)
            prop.PropertyName = propname
            if not value is None:
                prop.Literal = value
            setattr(rfilter, ftype, prop)

        return rfilter

    def create_symbolizer(self, stype):
        if stype is None:
            return None
        
        return self.create_element('sld', stype + 'Symbolizer')
        

class Rules(SLDNode):
    def __init__(self, parent):
        super(Rules, self).__init__(parent)
        self._node = None
        self._nodes = self._parent.xpath('sld:Rule', namespaces=SLDNode._nsmap)

    def normalize(self):
        for i,rnode in enumerate(self._nodes):
            rule = Rule(self._parent, i-1)
            rule.normalize()

    def __len__(self):
        return len(self._nodes)

    def __getitem__(self, key):
        rule = Rule(self._parent, key)
        return rule

    def __setitem__(self, key, value):
        if isinstance(value, Rule):
            self._nodes.replace(self._nodes[key], value._node)
        elif isinstance(value, Element):
            self._nodes.replace(self._nodes[key], value)
   
    def __delitem__(self, key):
        self._nodes.remove(self._nodes[key])


class FeatureTypeStyle(SLDNode):
    def __init__(self, parent):
        super(FeatureTypeStyle, self).__init__(parent)
        self._node = self._parent.xpath('sld:FeatureTypeStyle', namespaces=SLDNode._nsmap)[0]

    def normalize(self):
        if not self.Rules is None:
            self.Rules.normalize()

    @property
    def Rules(self):
        return Rules(self._node)

    def create_rule(self, title, symbolizer=None):
        elem = self._node.makeelement('{%s}Rule' % SLDNode._nsmap['sld'], nsmap=SLDNode._nsmap)
        self._node.append(elem)

        rule = Rule(self._node, len(self._node)-1)
        rule.Title = title

        if symbolizer is None:
            symbolizer = PointSymbolizer

        sym = symbolizer(rule._node)
        if symbolizer == PointSymbolizer:
            gph = Graphic(sym._node)
            mrk = Mark(gph._node)
            mrk.WellKnownName = 'square'
            fill = Fill(mrk._node)
            fill.create_cssparameter('fill', '#ff0000')

        elif symbolizer == LineSymbolizer:
            stroke = Stroke(sym._node)
            stroke.create_cssparameter('stroke', '#0000ff')

        elif symbolizer == PolygonSymbolizer:
            fill = Fill(sym._node)
            fill.create_cssparameter('fill', '#AAAAAA')
            stroke = Stroke(sym._node)
            stroke.create_cssparameter('stroke', '#000000')
            stroke.create_cssparameter('stroke-width', '1')
            
        return rule


class UserStyle(SLDNode):
    def __init__(self, parent):
        super(UserStyle, self).__init__(parent)
        self._node = self._parent.xpath('sld:UserStyle', namespaces=SLDNode._nsmap)[0]

        setattr(self.__class__, 'Title', SLDNode.makeproperty('sld', self._node, name='Title'))
        setattr(self.__class__, 'Abstract', SLDNode.makeproperty('sld', self._node, name='Abstract'))
        setattr(self.__class__, 'FeatureTypeStyle', SLDNode.makeproperty('sld', self._node, cls=FeatureTypeStyle))

    def normalize(self):
        if not self.FeatureTypeStyle is None:
            self.FeatureTypeStyle.normalize()

    def create_featuretypestyle(self):
        return self.get_or_create_element('sld', 'FeatureTypeStyle')


class NamedLayer(SLDNode):
    def __init__(self, parent):
        super(NamedLayer, self).__init__(parent)
        self._node = self._parent.xpath('sld:NamedLayer', namespaces=SLDNode._nsmap)[0]

        setattr(self.__class__, 'UserStyle', SLDNode.makeproperty('sld', self._node, cls=UserStyle))
        setattr(self.__class__, 'Name', SLDNode.makeproperty('sld', self._node, name='Name'))

    def normalize(self):
        if not self.UserStyle is None:
            self.UserStyle.normalize()

    def create_userstyle(self):
        return self.get_or_create_element('sld', 'UserStyle')


class StyledLayerDescriptor(SLDNode):
    _cached_schema = None

    def __init__(self, sld_file=None):
        super(StyledLayerDescriptor, self).__init__(None)

        if StyledLayerDescriptor._cached_schema is None:
            #logging.debug('Storing new schema into cache.')
            localschema = NamedTemporaryFile(delete=False)
            schema_url = 'http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd'
            resp = urllib2.urlopen(schema_url)
            localschema.write(resp.read())
            resp.close()
            localschema.seek(0)

            theschema = parse(localschema)
            localschema.close()

            StyledLayerDescriptor._cached_schema = localschema.name
        else:
            #logging.debug('Fetching schema from cache.')
            localschema = open(StyledLayerDescriptor._cached_schema, 'r')
            theschema = parse(localschema)
            localschema.close()

        self._schema = XMLSchema(theschema)

        if not sld_file is None:
            self._node = parse(sld_file)

            if not self._schema.validate(self._node):
                logging.warn('SLD File "%s" does not validate against the SLD schema.', sld_file)
        else:
            self._node = Element("{%s}StyledLayerDescriptor" % SLDNode._nsmap['sld'], version="1.0.0", nsmap=SLDNode._nsmap)

        setattr(self.__class__, 'NamedLayer', SLDNode.makeproperty('sld', self._node, cls=NamedLayer))

    def __del__(self):
        if not StyledLayerDescriptor._cached_schema is None:
            #logging.debug('Clearing cached schema.')
            os.remove(StyledLayerDescriptor._cached_schema)
            StyledLayerDescriptor._cached_schema = None

    def __deepcopy__(self, memo):
        sld = StyledLayerDescriptor()
        sld._node = copy.deepcopy(self._node)
        return sld


    def normalize(self):
        if not self.NamedLayer is None:
            self.NamedLayer.normalize()


    def validate(self):
        if self._node is None or self._schema is None:
            if settings.DEBUG:
                logging.warn('The node or schema is empty, and cannot be validated.')
            return False

        is_valid = self._schema.validate(self._node)

        return is_valid


    @property
    def version(self):
        """
        Get the SLD version.
        """
        return self._node.getroot().get('version')

    @property
    def xmlns(self, ns=None):
        """
        Get the XML Namespace.
        """
        return self._node.getroot().nsmap[ns]

    def create_namedlayer(self, name):
        namedlayer = self.get_or_create_element('sld', 'NamedLayer')
        namedlayer.Name = name
        return namedlayer
