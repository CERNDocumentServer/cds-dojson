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

import pkg_resources
import pypeg2
from dojson.contrib.marc21 import model as default
from invenio_query_parser.parser import Main as parser
from invenio_query_parser.walkers.match_unit import MatchUnit
from invenio_query_parser.walkers.pypeg_to_ast import PypegConverter


class Query(object):
    """Query object."""

    def __init__(self, query):
        """Init."""
        self._query = query

    @property
    def query(self):
        """Parse query string using given grammar."""
        tree = pypeg2.parse(self._query, parser, whitespace="")
        return tree.accept(PypegConverter())

    def match(self, record, user_info=None):
        """Return True if record match the query."""
        return self.query.accept(MatchUnit(record))


def matcher(record, entry_point_group):
    """Matcher for DoJSON models.

    Using ``invenio-query-parser`` and ``MatchUnit`` walker decide which of the
    DoJSON models will be use depending on the content of the record.

    :param record: Something that looks like a python dictionary

    :returns: a model instance
    """
    logger = logging.getLogger(__name__ + ".dojson_matcher")

    _matches = []
    for entry_point in pkg_resources.iter_entry_points(entry_point_group):
        model = entry_point.load()
        query = Query(model.__query__)

        if query.match(record):
            logger.info("Model `{0}` found matching the query {1}.".format(
                entry_point.name, model
            ))
            _matches.append([entry_point.name, model])

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
