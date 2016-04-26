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

"""Image model."""

from ...overdo import OverdoJSONSchema
from .default import model as cds_marc21


class CDSImage(OverdoJSONSchema):
    """Translation Index for CDS Images."""

    __query__ = '999__.a:IMAGE'

    __schema__ = 'records/image-v1.0.0.json'

model = CDSImage(bases=(cds_marc21, ),
                 entry_point_group='cds_dojson.marc21.image')


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
