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

import pytest
from cds_dojson.marc21.models.base import model


@pytest.mark.parametrize(
    'marcxml_to_json', [('base.xml', model)], indirect=True)
def test_base_model(app, marcxml_to_json):
    """Test base model."""
    record = marcxml_to_json
    assert record['recid'] == 1495143
    assert record['agency_code'] == 'SzGeCERN'
    assert record['modification_date'] == '20170316170631.0'
