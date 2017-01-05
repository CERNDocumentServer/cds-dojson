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

import copy
import jsonschema
import six

from jsonresolver import JSONResolver
from jsonresolver.contrib.jsonschema import ref_resolver_factory


def compile_schema(schema, base_uri='', ref_resolver=None, in_place=False):
    """Resolve references in schema.

    It is assumed that schemas have already been validated for backward
    compatibility before transforming.

    :param schema: Schema that is currently processed.
    :param base_uri: URI of the currently processed schema.
                     If not provided it will use default.
    :param ref_resolver: Resolver used to retrieve referenced schemas.
                         If not provided it will use default.
    :param in_place: If set to False it will not modify given schema.
                          Modified copy of the schema will be returned.
    """
    if not in_place:
        schema = copy.deepcopy(schema)

    if ref_resolver is None:
        ref_resolver = jsonschema.RefResolver(
            base_uri=base_uri, referrer=schema)

    json_resolver = JSONResolver()
    resolver_cls = ref_resolver_factory(json_resolver)
    ref_refolver = resolver_cls.from_schema(schema)

    return _compile_all_of(_resolve_references_sub(schema, ref_resolver))


def _resolve_references_sub(schema, ref_resolver):
    """Go through the schema and resolve references.

    :param schema: Schema that is currently processed.
    :param ref_resolver: Resolver used to retrieve referenced schemas.
    """
    if isinstance(schema, dict):
        for key, json_value in six.iteritems(schema):
            if isinstance(json_value, dict) and '$ref' in json_value:
                    ref = json_value.pop('$ref', None)
                    schema[key] = ref_resolver.resolve(ref)[1]
            _resolve_references_sub(schema[key], ref_resolver)

    elif isinstance(schema, list):
        for i, schema_part in enumerate(schema):
            if '$ref' in schema_part:
                ref = schema_part.pop('$ref', None)
                schema[i] = ref_resolver.resolve(ref)[1]
            _resolve_references_sub(schema_part, ref_resolver)

    return schema


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
