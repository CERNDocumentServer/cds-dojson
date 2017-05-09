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

from ..models.base import model as marc21


@marc21.over('recid', '^001')
def recid(self, key, value):
    """Record Identifier."""
    return value


@marc21.over('agency_code', '^003')
def agency_code(self, key, value):
    """Control number identifier"""
    return value


@marc21.over('modification_date', '^005')
def modification_date(self, key, value):
    """Date and Time of Latest Transaction."""
    return value
