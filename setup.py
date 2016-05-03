# -*- coding: utf-8 -*-
#
# This file is part of DoJSON
# Copyright (C) 2015 CERN.
#
# DoJSON is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""CDS DoJSON extension"""

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
    'coverage>=4.0',
    # 'invenio-jsonschemas>=1.0.0a2',
    'isort>=4.2.2',
    'mock>=1.0.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=2.1.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
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
        'setuptools>=17.1',
    ],
    install_requires=[
        'dojson>=1.2.1',
        'invenio-query-parser>=0.5.0',
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 5 - Production/Stable',
    ],
    tests_require=tests_require,
    entry_points={
        'cds_dojson.marc21.models': [
            'album = cds_dojson.marc21.models.album:model',
            'default = cds_dojson.marc21.models.default:model',
            'image = cds_dojson.marc21.models.image:model',
            'video = cds_dojson.marc21.models.video:model',
        ],
        'cds_dojson.marc21.default': [
            'bd01x09x = cds_dojson.marc21.fields.default.bd01x09x',
            'bd2xx = cds_dojson.marc21.fields.default.bd2xx',
            'bd5xx = cds_dojson.marc21.fields.default.bd5xx',
            'bd6xx = cds_dojson.marc21.fields.default.bd6xx',
            'bd7xx = cds_dojson.marc21.fields.default.bd7xx',
            'bd8xx = cds_dojson.marc21.fields.default.bd8xx',
            'bd9xx = cds_dojson.marc21.fields.default.bd9xx',
        ],
        'cds_dojson.marc21.album': [
            'album = cds_dojson.marc21.fields.album'
        ],
        'cds_dojson.marc21.image': [
            'image = cds_dojson.marc21.fields.image'
        ],
        'cds_dojson.marc21.video': [
            'video = cds_dojson.marc21.fields.video'
        ],
        'cds_dojson.to_marc21.models': [
            'album = cds_dojson.to_marc21.models.album:model',
            'default = cds_dojson.to_marc21.models.default:model',
            'image = cds_dojson.to_marc21.models.image:model',
            'video = cds_dojson.to_marc21.models.video:model',
        ],
        'cds_dojson.to_marc21.default': [
            'bd01x09x = cds_dojson.to_marc21.fields.default.bd01x09x',
            'bd2xx = cds_dojson.to_marc21.fields.default.bd2xx',
            'bd5xx = cds_dojson.to_marc21.fields.default.bd5xx',
            'bd6xx = cds_dojson.to_marc21.fields.default.bd6xx',
            'bd7xx = cds_dojson.to_marc21.fields.default.bd7xx',
            'bd8xx = cds_dojson.to_marc21.fields.default.bd8xx',
            'bd9xx = cds_dojson.to_marc21.fields.default.bd9xx',
        ],
        'cds_dojson.to_marc21.album': [
            'album = cds_dojson.to_marc21.fields.album'
        ],
        'cds_dojson.to_marc21.image': [
            'image = cds_dojson.to_marc21.fields.image'
        ],
        'cds_dojson.to_marc21.video': [
            'video = cds_dojson.to_marc21.fields.video'
        ],
        # DoJSON entry points
        'dojson.cli.rule': [
            'cds_marc21 = cds_dojson.marc21:marc21',
            'cds_to_marc21 = cds_dojson.to_marc21:to_marc21'
        ],
        'dojson.cli.load': [
            'cds_marcxml = cds_dojson.marc21.utils:load',
        ],
    }
)
