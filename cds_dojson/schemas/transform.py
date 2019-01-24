# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2016, 2017 CERN.
#
# CERN Document Server is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# CERN Document Server is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CERN Document Server; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.
"""Create compiled version of JSON schemas."""

import copy

import six
from jsonref import JsonRef


def compile_schema(schema, base_uri='', in_place=False):
    """Resolve references in schema.

    It is assumed that schemas have already been validated for backward
    compatibility before transforming.

    :param schema: Schema that is currently processed.
    :param base_uri: URI of the currently processed schema.
                     If not provided it will use default.
    :param in_place: If set to False it will not modify given schema.
                          Modified copy of the schema will be returned.
    """
    if not in_place:
        schema = copy.deepcopy(schema)

    return _compile_all_of(JsonRef.replace_refs(schema, base_uri=base_uri))


def _compile_all_of(schema):
    """Go through the schema an compile the ``allOf`` rules."""
    if isinstance(schema, dict):
        if 'allOf' in schema:
            all_of = schema.pop('allOf')
            schema = merge_dicts(schema, *all_of)
        for key, value in six.iteritems(schema):
            schema[key] = _compile_all_of(value)
    elif isinstance(schema, list):
        for i, value in enumerate(schema):
            schema[i] = _compile_all_of(value)
    return schema


def merge_dicts(base, *others):
    """Merge the 'second' multiple-dictionary into the 'first' one."""
    new = copy.deepcopy(base)
    for other in others:
        for k, v in other.items():
            if isinstance(v, dict) and v:
                ret = merge_dicts(new.get(k, dict()), v)
                new[k] = ret
            else:
                new[k] = other[k]
    return new
