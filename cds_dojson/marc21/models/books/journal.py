# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2020 CERN.
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
"""Journal model."""

from __future__ import unicode_literals

from ..base import model as cds_base
from .base import COMMON_IGNORE_FIELDS, CDSOverdoBookBase
from .base import model as books_base


class CDSJournal(CDSOverdoBookBase):
    """Translation Index for CDS Books."""

    __query__ = '980__:PERI -980__:DELETED -980__:MIGRATED'

    __schema__ = 'https://127.0.0.1:5000/schemas/series/series-v1.0.0.json'

    __model_ignore_keys__ = {
        '080__a',
        '020__C',
        '080__c',
        '030__a',
        '030__9',
        '044__a',
        '044__b',
        '222__a',
        '310__a',
        '938__a',
        '044__a',
        '246_39',
        '85641m',
        '85641g',
        '85641n',
        '8564_8',   # not clear, some ID from legacy
        '8564_s',   # timestamp of files
        '8564_x',   # icon uri
        '6531_9',
        '246_3i',
        '650__a',
        '690C_a',
        '938__p',
        '938__f',
        '939__a',
        '939__d',
        '939__u',
        '939__v',
        '6531_a',
        '780__i',   # label of relation continues
        '780__t',   # title of relation continues
        '785__i',   # label of relation continued by
        '785__t',   # title of relation continued by
        '85641y',
        '866__g',
        '866__x',
        '933__a',
        '962__n',
        '960__a',
        '960__c',
        '980__a',
        '980__b',
    }

    __ignore_keys__ = COMMON_IGNORE_FIELDS | __model_ignore_keys__

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Set schema after translation depending on the model."""
        json = super(CDSJournal, self).do(
            blob=blob,
            ignore_missing=ignore_missing,
            exception_handlers=exception_handlers)
        json['$schema'] = self.__class__.__schema__
        if '_migration' not in json:
            json['_migration'] = {}

        json['_migration'].setdefault('record_type', 'journal')
        json['_migration'].setdefault('volumes', [])
        json['_migration'].setdefault('is_multipart', False)
        json['_migration'].setdefault('has_related', False)
        json['_migration'].setdefault('items', [])
        json['_migration'].setdefault('electronic_items', [])
        json['_migration'].setdefault('relation_previous', None)
        json['_migration'].setdefault('relation_next', None)

        return json


model = CDSJournal(
    bases=(),
    entry_point_group='cds_dojson.marc21.series')
