# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
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
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.

"""Query parser."""

import pypeg2

from invenio_query_parser.walkers.pypeg_to_ast import PypegConverter
from invenio_query_parser.parser import Main as parser
from invenio_query_parser.walkers.match_unit import MatchUnit


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
