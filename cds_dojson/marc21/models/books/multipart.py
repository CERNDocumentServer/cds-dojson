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
"""Series model."""
from __future__ import unicode_literals

from ..base import model as cds_base
from .base import model as books_base
from .base import CDSOverdoBookBase, COMMON_IGNORE_FIELDS


class CDSMultipart(CDSOverdoBookBase):
    """Translation Index for CDS Books."""

    __query__ = '(690C_:BOOK OR 690C_:"YELLOW REPORT" OR ' \
                '690C_:BOOKSUGGESTION OR 980__:PROCEEDINGS OR 980__:PERI OR ' \
                '697C_:LEGSERLIB OR 697C_:"ENGLISH BOOK CLUB" -980__:DELETED)'\
                'AND 246__:/[a-zA-Z0-9]+/ '

    __schema__ = 'https://127.0.0.1:5000/schemas/series/series-v1.0.0.json'

    __model_ignore_keys__ = {
        '505__a',
        '505__t',
        '5050_a',
        '5050_t',
        '021__a',
        '021__b',
        '490__a',
        '490__b',
        '490__c',
    }

    __ignore_keys__ = COMMON_IGNORE_FIELDS | __model_ignore_keys__

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Set schema after translation depending on the model."""
        json = super(CDSMultipart, self).do(
            blob=blob,
            ignore_missing=ignore_missing,
            exception_handlers=exception_handlers)
        json['$schema'] = self.__class__.__schema__

        json['_record_type'] = 'multipart'
        return json


model = CDSMultipart(
    bases=(cds_base, ),
    entry_point_group='cds_dojson.marc21.series')
