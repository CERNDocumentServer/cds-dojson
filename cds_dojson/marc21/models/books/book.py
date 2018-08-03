# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
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
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Video model."""

from cds_dojson.overdo import OverdoJSONSchema
from cds_dojson.marc21.fields.base import model as cds_base


class CDSBook(OverdoJSONSchema):
    """Translation Index for CDS Videos."""

    __query__ = ''

    __schema__ = 'records/books/book/book-v.0.0.1.json'

    __ignore_keys__ = {
        '020__q',
    }

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Set schema after translation depending on the model."""
        json = super(CDSBook, self).do(
            blob=blob,
            ignore_missing=ignore_missing,
            exception_handlers=exception_handlers)
        json['$schema'] = {'$ref': self.__class__.__schema__}

        return json


model = CDSBook(
    bases=(cds_base, ), entry_point_group='cds_dojson.marc21.book')
