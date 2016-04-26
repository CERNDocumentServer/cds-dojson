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

"""Album model."""

from ...overdo import OverdoJSONSchema
from .default import model as cds_marc21


class CDSAlbum(OverdoJSONSchema):
    """Translation Index for CDS Albums."""

    __query__ = '999__.a:ALBUM'

    __schema__ = 'records/album-v1.0.0.json'

model = CDSAlbum(bases=(cds_marc21, ),
                 entry_point_group='cds_dojson.marc21.album')


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
