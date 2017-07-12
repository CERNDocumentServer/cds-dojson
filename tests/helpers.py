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
# along with Invenio; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Test utilities."""

import os

import pkg_resources
from jsonresolver import JSONResolver
from jsonresolver.contrib.jsonschema import ref_resolver_factory
from jsonschema import validate as _validate


def mock_path_to_url(self, path):
    """Mock the ``paht_to_utl method from InvenioJSONSchemasState."""
    return path


def json_resolver(schema):
    """Test ``json_resolver``."""
    json_resolver = JSONResolver(plugins=[
        'demo.json_resolver',
    ])
    resolver_cls = ref_resolver_factory(json_resolver)
    return resolver_cls.from_schema(schema)


def validate(json):
    """Wrap jsonchema.validate for convenience."""
    return _validate(
        json,
        json['$schema'],
        resolver=json_resolver(json['$schema']),
        types={'array': (list, tuple)})


def load_fixture_file(file_name):
    """Read the content of a file and return it."""
    return pkg_resources.resource_string(__name__,
                                         os.path.join('fixtures',
                                                      file_name))
