# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2015 CERN.
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

from jsonresolver import JSONResolver
from jsonresolver.contrib.jsonschema import ref_resolver_factory


def mock_path_to_url(self, path):
    """Mock the ``paht_to_utl method from InvenioJSONSchemasState."""
    return path


def mock_get_schema(self, path):
    """Mock the ``get_schema`` method of InvenioJSONSchemasState."""
    with open(pkg_resources.resource_filename(
            'cds.modules.records.jsonschemas', path), 'r') as f:
        return json.load(f)


def json_resolver(schema):
    """Test ``json_resolver``."""
    json_resolver = JSONResolver(plugins=['demo.json_resolver', ])
    resolver_cls = ref_resolver_factory(json_resolver)
    return resolver_cls.from_schema(schema)
