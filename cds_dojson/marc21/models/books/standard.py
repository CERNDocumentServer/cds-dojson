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
"""Book model."""

from __future__ import unicode_literals

from ..base import model as cds_base
from .base import CDSOverdoBookBase
from .base import model as books_base


class CDSStandard(CDSOverdoBookBase):
    """Translation Index for CDS Books."""

    __query__ = '690C_:STANDARD -980__:DELETED'

    __schema__ = 'records/books/book/book-v.0.0.1.json'

    __ignore_keys__ = {

        '003',
        '005',
        '020__q',
        '0248_a',
        '0248_p',
        '050__b',
        '050_4b',
        '082002',
        '082042',
        '0820_2',
        '082__2',
        '340__a',
        '541__9',
        '650172',
        '65017a',
        '650272',
        '65027a',
        '694__9',
        '694__a',
        '852__c',
        '852__h',
        '916__d',
        '916__e',
        '916__y',
        '940__u',
        '961__c',
        '961__h',
        '961__l',
        '961__x',
        '963__a',
        '964__a',
        '981__a',
    }

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Set schema after translation depending on the model."""
        json = super(CDSStandard, self).do(
            blob=blob,
            ignore_missing=ignore_missing,
            exception_handlers=exception_handlers)
        json['$schema'] = {'$ref': self.__class__.__schema__}
        return json


model = CDSStandard(
    bases=(books_base, cds_base, ),
    entry_point_group='cds_dojson.marc21.book')
