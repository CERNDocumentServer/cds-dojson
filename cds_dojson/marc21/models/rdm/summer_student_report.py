# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2024 CERN.
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

"""CDS-RDM Summer student model."""

from __future__ import unicode_literals

from cds_dojson.marc21.models.rdm.base import CdsOverdo
from .base import model as base_model

class CMSSummerStudent(CdsOverdo):
    """Translation Index for CDS Books."""

    __query__ = "037__a:CERN-STUDENTS-Note*"

    __ignore_keys__ = {
        '65017a',
        '937__c',
        '960__a',
        '269__b',
        '6531_a',
        '906__p',
        '269__a',
        '100__0',
        '980__a',
        '260__c',
        '693__a',
        '710__5',
        '916__w',
        '690C_a',
        '595__a',
        '693__e',
        '650172',
        '916__s',
        '041__a',
        '937__s',
        '859__f',
        '6531_9',
        '520__a',
        '963__a',
        '710__a',
        '100__a',
        '100__m',
    }
    _default_fields = None


model = CMSSummerStudent(bases=(base_model,), entry_point_group="cds_dojson.marc21.summer_student_report")
