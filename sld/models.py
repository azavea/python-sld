from lxml.etree import parse, XMLSchema, XMLSyntaxError
import urllib2
from tempfile import NamedTemporaryFile
import os, copy

class StyledLayerDescriptor:
    def __init__(self, sld_file):
        schema_url = 'http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd'
        resp = urllib2.urlopen(schema_url)
        localschema = NamedTemporaryFile(delete=False)
        localschema.write(resp.read())
        resp.close
        localschema.close()

        theschema = parse(localschema.name)

        self._schema = XMLSchema(theschema)

        self._style = parse(sld_file)

        self._schema.validate(self._style)

        self._nsmap = self._style.getroot().nsmap
        ns = self._nsmap.pop(None)
        self._nsmap['sld'] = ns

        os.remove(localschema.name)

    @property
    def version(self):
        """
        Get the SLD version.
        """
        return self._style.getroot().get('version')

    @property
    def xmlns(self):
        """
        Get the XML Namespace.
        """
        return self._style.getroot().get('xmlns')

    @property
    def NamedLayer(self):
        return NamedLayer(self._style, self._nsmap)


class SLDNode(object):
    def __init__(self, parent, nsmap):
        self._parent = parent
        self._nsmap = nsmap
        

class NamedLayer(SLDNode):
    def __init__(self, parent, nsmap):
        super(NamedLayer, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('sld:NamedLayer', namespaces=self._nsmap)[0]

    @property
    def Name(self):
        return self._node.xpath('sld:Name', namespaces=self._nsmap)[0].text

    @property
    def UserStyle(self):
        return UserStyle(self._node, self._nsmap)


class UserStyle(SLDNode):
    def __init__(self, parent, nsmap):
        super(UserStyle, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('sld:UserStyle', namespaces=self._nsmap)[0]

    def get_title(self):
        xpath = self._node.xpath('sld:Title', namespaces=self._nsmap)
        if len(xpath) > 0:
            return xpath[0].text
        return None

    def set_title(self, title):
        xpath = self._node.xpath('sld:Title', namespaces=self._nsmap)
        if len(xpath) > 0:
            xpath[0].text = title
        else:
            elem = self._node.makeelement('{%s}Title' % self._nsmap['sld'], nsmap=self._nsmap)
            self._node.append(elem)

    def del_title(self):
        xpath = self._node.xpath('sld:Title', namespaces=self._nsmap)
        if len(xpath) > 0:
            self._node.remove(xpath[0])

    Title = property(get_title, set_title, del_title, "The Title of the UserStyle")

    def get_abstract(self):
        xpath = self._node.xpath('sld:Abstract', namespaces=self._nsmap)
        if len(xpath) > 0:
            return xpath[0].text
        else:
            return None

    def set_abstract(self, abstract):
        xpath = self._node.xpath('sld:Abstract', namespaces=self._nsmap)
        if len(xpath) > 0:
            xpath[0].text = abstract
        else:
            elem = self._node.makeelement('{%s}Abstract' % self._nsmap['sld'], nsmap=self._nsmap)
            self._node.append(elem)

    def del_abstract(self):
        xpath = self._node.xpath('sld:Abstract', namespaces=self._nsmap)
        if len(xpath) > 0:
            self._node.remove(xpath[0])

    Abstract = property(get_abstract, set_abstract, del_abstract, "The Abstract of the UserStyle")

    @property
    def FeatureTypeStyle(self):
        return FeatureTypeStyle(self._node, self._nsmap)


class FeatureTypeStyle(SLDNode):
    def __init__(self, parent, nsmap):
        super(FeatureTypeStyle, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('sld:FeatureTypeStyle', namespaces=self._nsmap)[0]

    @property
    def Rules(self):
        return Rules(self._node, self._nsmap)


class Rules(SLDNode):
    def __init__(self, parent, nsmap):
        super(Rules, self).__init__(parent, nsmap)
        self._nodes = self._parent.xpath('sld:Rule', namespaces=self._nsmap)

    def __len__(self):
        return len(self._nodes)

    def __getitem__(self, key):
        return Rule(self._parent, self._nsmap, key)

    def __setitem__(self, key, value):
        if isinstance(value, Rule):
            self._nodes.replace(self._nodes[key], value.toelem())
        else:
            self._nodes.replace(self._nodes[key], value)
   
    def __delitem__(self, key):
        self._nodes.remove(self._nodes[key])


class Rule(SLDNode):
    def __init__(self, parent, nsmap, index):
        super(Rule, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('sld:Rule', namespaces=self._nsmap)[index]

    def toelem(self):
        return self._node

    def get_title(self):
        xpath = self._node.xpath('sld:Title', namespaces=self._nsmap)
        if len(xpath) > 0:
            return xpath[0].text
        return None

    def set_title(self, title):
        xpath = self._node.xpath('sld:Title', namespaces=self._nsmap)
        if len(xpath) > 0:
            xpath[0].text = title
        else:
            elem = self._node.makeelement('{%s}Title' % self._nsmap['sld'], nsmap=self._nsmap)
            self._node.append(elem)

    def del_title(self):
        xpath = self._node.xpath('sld:Title', namespaces=self._nsmap)
        if len(xpath) > 0:
            self._node.remove(xpath[0])

    Title = property(get_title, set_title, del_title, "The Title of the Rule")

    @property
    def Filter(self):
        return Filter(self._node, self._nsmap)

    @property
    def PolygonSymbolizer(self):
        return PolygonSymbolizer(self._node, self._nsmap)

    @property
    def LineSymbolizer(self):
        return LineSymbolizer(self._node, self._nsmap)
      

class Filter(SLDNode):
    def __init__(self, parent, nsmap):
        super(Filter, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('ogc:Filter', namespaces=self._nsmap)[0]

    def __add__(x, y):
        elem = x._node.makeelement('{%s}And' % x._nsmap['ogc'])
        elem.append(copy.copy(x._node[0]))
        elem.append(copy.copy(y._node[0]))
        return elem

    def __or__(x, y):
        elem = x._node.makeelement('{%s}Or' % x._nsmap['ogc'])
        elem.append(copy.copy(x._node[0]))
        elem.append(copy.copy(y._node[0]))
        return elem

    def __getattr__(self, name):
        if not name.startswith('PropertyIs'):
            print name
            raise AttributeError('Property name must be one of: PropertyIsEqualTo, PropertyIsNotEqualTo, PropertyIsLessThan, PropertyIsLessThanOrEqualTo, PropertyIsGreaterThan, PropertyIsGreaterThanOrEqualTo, PropertyIsBetween, PropertyIsLike, PropertyIsNull.')
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
            elem = self._node.makeelement('{%s}'+name % self._nsmap['ogc'], nsmap=self._nsmap)
            self._node.append(elem)

    def __delattr__(self, name):
        xpath = self._node.xpath('ogc:'+name, namespaces=self._nsmap)
        if len(xpath) > 0:
            self._node.remove(xpath[0])


class PolygonSymbolizer(SLDNode):
    def __init__(self, parent, nsmap):
        super(PolygonSymbolizer, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('sld:PolygonSymbolizer', namespaces=self._nsmap)[0]

 
class LineSymbolizer(SLDNode):
    def __init__(self, parent, nsmap):
        super(LineSymbolizer, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('sld:LineSymbolizer', namespaces=self._nsmap)[0]


class PropertyCriterion(SLDNode):
    def __init__(self, parent, nsmap, name):
        super(PropertyCriterion, self).__init__(parent, nsmap)
        self._node = self._parent.xpath('ogc:'+name, namespaces=self._nsmap)[0]

    @property
    def PropertyName(self):
        return self._node.xpath('ogc:PropertyName', namespaces=self._nsmap)[0]

    @property
    def Literal(self):
        return self._node.xpath('ogc:Literal', namespaces=self._nsmap)[0]
