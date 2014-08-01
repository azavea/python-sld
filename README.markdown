python-sld
==========

A python library for reading, writing, and manipulating SLD files.

Requirements
============

The lxml library is required for XML parsing and XML Schema validation. This 
requirement is listed in requirements.txt, and may be installed using pip with
this command:

    > sudo pip install -r requirements.txt

Installation
============

    > easy_install python-sld

    OR

    > pip install python-sld

Usage
=====

Using python-sld to create SLD documents is as easy as instantiating a 
StyledLayerDescriptor class object.

    from sld import StyledLayerDescriptor
    mysld = StyledLayerDescriptor()

You may also read an existing SLD document in by passing it as a parameter:

    from sld import StyledLayerDescriptor
    mysld = StyledLayerDescriptor('mysld.sld')

Addition of most elements are performed on the parent element, since they are
related to parent nodes in order to preserve compliance:

    nl = mysld.create_namedlayer()
    ustyle = nl.create_style()

A couple class objects represent collections of nodes, such as Rules and 
CssParameters. They are properties of their parent classes (FeatureTypeStyle
and Fill/Stroke/Font respectively). They behave as python lists, and you
can access any of their items using a python list pattern:

    fts = ustyle.create_featuretypestyle()
    rule1 = fts.Rules[0]
    print len(fts.Rules)
    fts.Rules[0] = rule1

Filter objects are pythonic, and when combined with the '+' operator, they
become ogc:And filters.  When combined with the '|' operator, they become
ogc:Or filters.

    from sld import Filter

    filter_1 = Filter(rule)
    # set filter 1 properties

    filter_2 = Filter(rule)
    # set filter 2 properties

    rule.Filter = filter_1 + filter_2

You may also construct a filter from an expression when using the create_filter
method on the Rule object:

    filter = rule.create_filter('population', '>', '100')


Implementation
==============

At the current time, python-sld does ''not'' support the full SLD 
specification. The current implementation supports the following SLD elements:

  - StyledLayerDescriptor
  - NamedLayer
  - Name (of NamedLayer)
  - UserStyle
  - Title (of UserStyle and Rule)
  - Abstract
  - FeatureTypeStyle
  - Rule
  - ogc:Filter
  - ogc:And
  - ogc:Or
  - ogc:PropertyIsNotEqualTo
  - ogc:PropertyIsLessThan
  - ogc:PropertyIsLessThanOrEqualTo
  - ogc:PropertyIsEqualTo
  - ogc:PropertyIsGreaterThanOrEqualTo
  - ogc:PropertyIsGreaterThan
  - ogc:PropertyIsLike
  - ogc:PropertyName
  - ogc:Literal
  - MinScaleDenominator
  - MaxScaleDenominator
  - PointSymbolizer
  - LineSymbolizer
  - PolygonSymbolizer
  - TextSymbolizer
  - Mark
  - Graphic
  - Fill
  - Stroke
  - Font
  - CssParameter

Support
=======

If you have any problems or questions, please visit the python-sld project on
github: https://github.com/azavea/python-sld/

Contributors
============

@[ewsterrenburg](https://github.com/ewsterrenburg)

