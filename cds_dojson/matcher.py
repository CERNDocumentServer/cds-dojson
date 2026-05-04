# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
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
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.

"""Query parser."""

import logging

import importlib_metadata
import pypeg2
from dojson.contrib.marc21 import model as default
from invenio_query_parser.parser import Main as parser
from invenio_query_parser.walkers.match_unit import MatchUnit
from invenio_query_parser.walkers.pypeg_to_ast import PypegConverter

# Cache of (name, model, parsed_query_ast) tuples keyed by entry_point_group.
# Entry points and their query ASTs are static for the lifetime of a process,
# so scanning importlib_metadata and re-parsing pypeg2 queries on every call
# was the dominant cost (~84s for 1320 calls).
_models_cache = {}


class Query(object):
    """Query object."""

    def __init__(self, query):
        """Init."""
        self._query = query
        # Parse once at construction time; re-parsing on every match() call
        # via a @property was the other half of the cost.
        tree = pypeg2.parse(query, parser, whitespace="")
        self._parsed = tree.accept(PypegConverter())

    @property
    def query(self):
        """Return the pre-parsed query AST."""
        return self._parsed

    def match(self, record, user_info=None):
        """Return True if record match the query."""
        return self.query.accept(MatchUnit(record))


def _load_models(entry_point_group):
    """Load and cache entry point models for a given group."""
    if entry_point_group not in _models_cache:
        entrypoints = set(importlib_metadata.entry_points(group=entry_point_group))
        models = []
        for ep in entrypoints:
            model = ep.load()
            models.append((ep.name, model, Query(model.__query__)))
        _models_cache[entry_point_group] = models
    return _models_cache[entry_point_group]


def matcher(record, entry_point_group):
    """Matcher for DoJSON models.

    Using ``invenio-query-parser`` and ``MatchUnit`` walker decide which of the
    DoJSON models will be use depending on the content of the record.

    :param record: Something that looks like a python dictionary

    :returns: a model instance
    """
    logger = logging.getLogger(__name__ + ".dojson_matcher")

    _matches = []
    for name, model, query in _load_models(entry_point_group):
        if query.match(record):
            logger.info("Model `{0}` found matching the query {1}.".format(
                name, model
            ))
            _matches.append([name, model])
    try:
        if len(_matches) > 1:
            logger.error(
                ("Found more than one matches `{0}`, we'll use {1}"
                 " for record {2}.").format(
                    _matches, default, record
                )
            )
            return default
        return _matches[0][1]
    except IndexError:
        logger.warning(
            "Model *not* found, fallback to default {0} for record {1}".format(
                default, record
            )
        )
        return default
