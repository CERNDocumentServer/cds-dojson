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

from copy import deepcopy

from ..base import model as cds_base
from .base import COMMON_IGNORE_FIELDS, CDSOverdoBookBase, get_migration_dict
from .base import model as books_base


class CDSStandard(CDSOverdoBookBase):
    """Translation Index for CDS Books."""

    __query__ = '690C_:STANDARD OR 980__:STANDARD -980__:DELETED -980__:MIGRATED'

    __schema__ = 'https://127.0.0.1:5000/schemas/documents/document-v1.0.0.json'

    __ignore_keys__ = COMMON_IGNORE_FIELDS

    __json_init_dict__ = {'_migration': {**get_migration_dict()}}

    def do(self, blob, ignore_missing=True, exception_handlers=None):
        """Set schema after translation depending on the model."""
        json = super(CDSStandard, self).do(
            blob=blob,
            ignore_missing=ignore_missing,
            exception_handlers=exception_handlers,
            init_fields=deepcopy(self.__json_init_dict__),
        )

        json['$schema'] = self.__class__.__schema__
        return json


model = CDSStandard(
    bases=(books_base, cds_base,),
    entry_point_group='cds_dojson.marc21.book')
