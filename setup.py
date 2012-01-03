"""
Setup script for python-sld.

License
=======
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

import os, subprocess
from setuptools import setup, Command

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

class RunTests(Command):
    description = "Run the unittest suite for python-sld."
    user_options = [('verbose', 'v', 'Logging verbosity.')]
    extra_env = {}
    extra_args = []

    def run(self):
        os.chdir('sld')
        args = ['./run_tests.py']
        if self.verbose == 2:
            args.append('-v')

        subprocess.call(args)

    def initialize_options(self):
        self.verbose = 1

    def finalize_options(self):
        pass

setup(
    name = "python-sld",
    version = "1.0.6",
    author = "David Zwarg",
    author_email = "dzwarg@azavea.com",
    description = ("A simple python library that enables dynamic SLD creation and manipulation."),
    license = "Apache 2.0",
    keywords = "ogc sld geo geoserver mapserver osgeo",
    url = "http://github.com/azavea/python-sld/",
    requires = ["lxml"],
    packages = ["sld","sld.test"],
    package_data = {"sld.test": ["style.sld"]},
    long_description = read('README.markdown'),
    cmdclass = { 'test': RunTests },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: GIS"
    ]
)
