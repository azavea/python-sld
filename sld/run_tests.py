#!/usr/bin/python
"""
Testing fixture for StyledLayerDescriptor library.

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
import unittest, sys, logging
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-v', '--verbose', dest='verbosity',
        help='Logging verbosity.', action='store_true', default=False)

    (options, args) = parser.parse_args()

    loglevel = logging.WARNING
    if options.verbosity:
        loglevel = logging.DEBUG

    logging.basicConfig(format='%(message)s',level=loglevel)

    sys.path.insert(0, '..')

    import sld.test
    unittest.main(sld.test)
