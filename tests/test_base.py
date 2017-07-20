# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
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
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.
"""Base model tests."""

import os

import pkg_resources
from cds_dojson.marc21.models.base import model
from cds_dojson.marc21.utils import create_record


def test_base_model(app):
    """Test base model."""
    marcxml = pkg_resources.resource_string(__name__,
                                            os.path.join(
                                                'fixtures', 'base.xml'))

    with app.app_context():
        blob = create_record(marcxml)
        assert model.missing(blob) == {'001', '003', '005'}

        record = model.do(blob)
        assert record['recid'] == 1495143
        assert record['agency_code'] == 'SzGeCERN'
        assert not model.missing(blob)
