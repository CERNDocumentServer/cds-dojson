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
"""Video Project model."""

from ....overdo import OverdoJSONSchema
from ..base import model as cds_base


class CDSVideoProject(OverdoJSONSchema):
    """Translation Index for CDS Video Projects."""

    __query__ = '970__:project -980__:DELETED'

    __schema__ = 'records/videos/project/project-v1.0.0.json'

    __ignore_keys__ = {
        '005',
        '260__a',
        '260__c',
        '269__c',
        '5061_a',
        '690C_a',
        '774__o',
        '774__r',
        '937__c',
        '960__a',
        '961__c',
        '961__h',
        '961__l',
        '961__x',
        '980__a',
        '980__b',
        '981__a',
    }


model = CDSVideoProject(
    bases=(cds_base, ), entry_point_group='cds_dojson.marc21.video')
