# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2015, 2017 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""CDS DoJSON extension."""

import os
import re

from setuptools import setup

# Get the version string.  Cannot be done with import!
with open(os.path.join('cds_dojson', 'version.py'), 'rt') as f:
    version = re.search(
        '__version__\s*=\s*"(?P<version>.*)"\n',
        f.read()
    ).group('version')

tests_require = [
    'check-manifest>=0.25',
    'coverage>=5.3,<6',
    'invenio-jsonschemas>=1.0.0a5,<1.1.2',
    'jsonpatch>=1.11',
    'jsonref>=0.1',
    'jsonresolver>=0.1.0',
    'jsonschema>=2.5.1',
    'mock>=1.3.0',
    'pydocstyle>=1.0.0',
    'pycodestyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=2.10.1',
    'pytest-isort>=1.2.0',
    'pytest-pep8>=1.0.6',
    'pytest>=4.0.0,<5',
    'pycountry>=17.5.14,<19',
]

extras_require = {
    'docs': [
        'Sphinx>=1.3',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    extras_require['all'].extend(reqs)

setup(
    name='cds-dojson',
    version=version,
    url='http://github.com/CERNDocumentServer/cds-dojson/',
    license='BSD',
    author='CERN Document Server Team',
    author_email='cds-support@cern.ch',
    description=__doc__,
    long_description=open('README.rst').read(),
    packages=['cds_dojson'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    setup_requires=[
        'pytest-runner>=2.6.2',
    ],
    install_requires=[
        'arrow>=0.7.0',
        'dojson>=1.3.2',
        'invenio-query-parser>=0.5.0',
        'requests>=2.17.3',
        'pycountry>=17.5.14,<19',
    ],
    extras_require=extras_require,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 5 - Production/Stable',
    ],
    tests_require=tests_require,
    entry_points={
        'cds_dojson.marc21.models': [
            'videos_video = cds_dojson.marc21.models.videos.video:model',
            'videos_project = cds_dojson.marc21.models.videos.project:model'
        ],
        'cds_dojson.marc21.base': [
            'base = cds_dojson.marc21.fields.base'
        ],
        'cds_dojson.marc21.video': [
            'video = cds_dojson.marc21.fields.videos.video',
            'project = cds_dojson.marc21.fields.videos.project',
        ],
        # DoJSON entry points
        'console_scripts': [
            'cds-dojson=cds_dojson.cli:cli',
        ],
        'dojson.cli.rule': [
            'cds_marc21 = cds_dojson.marc21:marc21',
            'cds_to_marc21 = cds_dojson.to_marc21:to_marc21'
        ],
        'dojson.cli.load': [
            'cds_marcxml = cds_dojson.marc21.utils:load',
        ],
        'invenio_jsonschemas.schemas': [
            'cds = cds_dojson.schemas',
        ],

    }
)
