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
# along with Invenio; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test cds dojson to marc21."""

from __future__ import absolute_import

RECORD_SIMPLE = """<record>
  <datafield tag="100" ind1=" " ind2=" ">
      <subfield code="a">Donges, Jonathan F</subfield>
        </datafield>
    </record>"""


def test_image():
    """Test image model from XML into JSON."""
    from dojson.contrib.marc21.utils import create_record
    from cds_dojson.marc21.models.default import model as marc21
    from cds_dojson.to_marc21.models.default import model as to_marc21

    blob = create_record(RECORD_SIMPLE)
    data = marc21.do(blob)
    back_blob = to_marc21.do(data)
    assert blob == back_blob
