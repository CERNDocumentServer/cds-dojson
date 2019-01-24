# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017 CERN.
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
"""Common fields."""

from __future__ import absolute_import, print_function

from dojson.utils import IgnoreKey, filter_values, for_each_value, \
    force_list, ignore_value

from ..models.base import model
from .utils import clean_val


@model.over('recid', '^001')
def recid(self, key, value):
    """Record Identifier."""
    return int(value)


@model.over('agency_code', '^003')
def agency_code(self, key, value):
    """Control number identifier."""
    return 'SzGeCERN'


@model.over('keywords', '^6531_')
@for_each_value
@filter_values
def keywords(self, key, value):
    """Keywords."""
    return {
        'name': clean_val('a', value, str),
        'source': value.get('9') or value.get('g'),  # Easier to solve here
    }


@model.over('videos', '^774')
@for_each_value
def videos(self, key, value):
    """Videos."""
    return {
        '$ref': value.get('u')
    }


@model.over('modified_by', '^937__')
@ignore_value
def modified_by(self, key, value):
    """Modified by."""
    return value.get('s')
