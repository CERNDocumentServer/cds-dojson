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

from itertools import chain
from pathlib import Path

from jsonresolver import JSONResolver
from jsonresolver.contrib.jsonschema import ref_resolver_factory
from jsonschema import validate as _validate

from cds_dojson.utils import MementoDict


def mock_path_to_url(self, path):
    """Mock the ``path_to_url`` method from InvenioJSONSchemasState."""
    return path


def json_resolver(schema):
    """Test ``json_resolver``."""
    json_resolver = JSONResolver(
        plugins=[
            "demo.json_resolver",
        ]
    )
    resolver_cls = ref_resolver_factory(json_resolver)
    return resolver_cls.from_schema(schema)


def validate(json):
    """Wrap jsonchema.validate for convenience."""
    return _validate(
        json,
        json["$schema"],
        resolver=json_resolver(json["$schema"]),
        # types={'array': (list, tuple)}
    )


def load_fixture_file(file_name):
    """Read the content of a file and return it."""
    return (Path(__file__).parent / "fixtures" / file_name).read_bytes()


def mock_contributor_fetch(info):
    """Mock contributor fetch."""
    name = info.get("a")
    author_info = dict()
    if name == "Test User":
        author_info = dict(
            name="User, Test",
            lastname="User",
            recid="123456789",
            email="tuser@cern.ch",
            firstname="Test",
            cernccid="987654",
        )
    elif name == "Test User 2":
        author_info = dict(
            name="User, Test 2",
            lastname="User 2",
            recid="2123456789",
            email="tuser2@cern.ch",
            firstname="Test 2",
            cernccid="9876542",
        )
    else:
        return info

    return MementoDict(list(chain(info.items(), author_info.items())))
