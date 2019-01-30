# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017, 2018 CERN.
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
"""Books fields."""

from __future__ import absolute_import, print_function, unicode_literals

from dojson.utils import filter_values, for_each_value

from cds_dojson.marc21.fields.utils import clean_val
from cds_dojson.marc21.models.books.book import model


@model.over('title', '(^245__)')
@filter_values
def title(self, key, value):
    """Translates titles."""
    return {
        'title': clean_val('a', value, str, req=True),
        'subtitle': clean_val('b', value, str),
    }


@model.over('alternative_titles', '(^246__)')
@for_each_value
@filter_values
def alternative_titles(self, key, value):
    """Translates alternative titles."""
    return {
        'title': clean_val('a', value, str, req=True),
        'subtitle': clean_val('b', value, str),
    }
