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
"""Common RDM fields."""

from dateutil import parser
from dojson.errors import IgnoreKey

from cds_dojson.marc21.fields.books.errors import ManualMigrationRequired
from cds_dojson.marc21.fields.utils import clean_val, out_strip
from cds_dojson.marc21.models.base import model


@model.over('preprint_date', '^269__')     # item, RDM?!
@out_strip
def preprint_date(self, key, value):
    """Translates preprint_date fields."""
    date = clean_val('c', value, str)
    if date:
        try:
            date = parser.parse(date)
            return date.date().isoformat()
        except (ValueError, AttributeError):
            raise ManualMigrationRequired(subfield='c')
    else:
        raise IgnoreKey('preprint_date')
