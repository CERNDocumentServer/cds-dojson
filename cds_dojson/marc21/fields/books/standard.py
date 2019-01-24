# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017, 2018, 2019  CERN.
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
"""Standards fields."""
from __future__ import unicode_literals

from dojson.utils import filter_values, for_each_value

from cds_dojson.marc21.fields.utils import clean_val
from cds_dojson.marc21.models.books.standard import model


@model.over('title_translations', '^246__')
@for_each_value
@filter_values
def title_translations(self, key, value):
    """Translates title translations."""
    return {
        'title': clean_val('a', value, str, req=True),
        'language': 'en',
        'subtitle': clean_val('b', value, str),
    }
