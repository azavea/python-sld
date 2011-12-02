#!/usr/bin/python
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
