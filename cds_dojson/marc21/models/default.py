# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
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
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""CDS MARC21 model."""

from dojson.contrib.marc21 import marc21

from ...overdo import OverdoJSONSchema


class CDSMarc21(OverdoJSONSchema):
    """Translation Index for CDS specific MARC21."""

    __query__ = '690C_.a:CERN'

    __schema__ = 'records/default-v1.0.0.json'


model = CDSMarc21(bases=(marc21, ),
                  entry_point_group='cds_dojson.marc21.default')


@model.over('__order__', '__order__', override=True)
def order(self, key, value):
    """Preserve order of datafields."""
    order = []
    for field in value:
        name = model.index.query(field)
        if name:
            name = name[0]
        else:
            name = field
        order.append(name)

    return order
