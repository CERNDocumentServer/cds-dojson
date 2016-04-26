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

"""Test cds dojson image records."""

from __future__ import absolute_import

import json

from click.testing import CliRunner
from dojson.contrib.marc21.utils import create_record

from cds_dojson.marc21.models.image import model as marc21
from cds_dojson.matcher import matcher
from cds_dojson.to_marc21.models.image import model as to_marc21


CDS_IMAGE = """
<record>
  <controlfield tag="001">1782445</controlfield>
  <controlfield tag="005">20150925091440.0</controlfield>
  <datafield tag="037" ind1=" " ind2=" ">
    <subfield code="a">CERN-PHOTO-7009479</subfield>
  </datafield>
  <datafield tag="110" ind1=" " ind2=" ">
    <subfield code="a">CERN PhotoLab</subfield>
  </datafield>
  <datafield tag="245" ind1=" " ind2=" ">
    <subfield code="a">No caption</subfield>
  </datafield>
  <datafield tag="260" ind1=" " ind2=" ">
    <subfield code="c">1970</subfield>
  </datafield>
  <datafield tag="269" ind1=" " ind2=" ">
    <subfield code="a">Geneva</subfield>
    <subfield code="b">CERN</subfield>
    <subfield code="c">1970-9</subfield>
  </datafield>
  <datafield tag="300" ind1=" " ind2=" ">
    <subfield code="a">Photographic negative</subfield>
    <subfield code="c">6cmx6cm</subfield>
  </datafield>
  <datafield tag="500" ind1=" " ind2=" ">
    <subfield code="a">Image scanned from original photo negative on 14 Nov 2014</subfield>
    <subfield code="3">Box 37_191-8-70_300-10-70</subfield>
  </datafield>
  <datafield tag="541" ind1=" " ind2=" ">
    <subfield code="e">479-9-1970</subfield>
  </datafield>
  <datafield tag="595" ind1=" " ind2=" ">
    <subfield code="a">Archive Collection</subfield>
    <subfield code="s">Scanned by Contentra Technologies</subfield>
    <subfield code="9">11142014-37_191-8-70_300-10-70-6cmx6cm</subfield>
  </datafield>
  <datafield tag="596" ind1=" " ind2=" ">
    <subfield code="a">Updated 774 value on run 1443157342</subfield>
  </datafield>
  <datafield tag="690" ind1="C" ind2=" ">
    <subfield code="a">PHOTO</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">ALBUM</subfield>
    <subfield code="r">2054964</subfield>
  </datafield>
  <datafield tag="856" ind1="4" ind2=" ">
    <subfield code="s">1770303</subfield>
    <subfield code="u">http://cds.cern.ch/record/1782445/files/70-9-479.jpg</subfield>
    <subfield code="y">Image 70-9-479</subfield>
  </datafield>
  <datafield tag="856" ind1="4" ind2=" ">
    <subfield code="s">143713</subfield>
    <subfield code="u">http://cds.cern.ch/record/1782445/files/70-9-479.jpg?subformat=icon-640</subfield>
    <subfield code="x">icon-640</subfield>
  </datafield>
  <datafield tag="856" ind1="4" ind2=" ">
    <subfield code="s">411079</subfield>
    <subfield code="u">http://cds.cern.ch/record/1782445/files/70-9-479.jpg?subformat=icon-1440</subfield>
    <subfield code="x">icon-1440</subfield>
  </datafield>
  <datafield tag="856" ind1="4" ind2=" ">
    <subfield code="s">74003</subfield>
    <subfield code="u">http://cds.cern.ch/record/1782445/files/70-9-479.jpg?subformat=icon-180</subfield>
    <subfield code="x">icon-180</subfield>
  </datafield>
  <datafield tag="916" ind1=" " ind2=" ">
    <subfield code="s">n</subfield>
    <subfield code="w">201446</subfield>
  </datafield>
  <datafield tag="960" ind1=" " ind2=" ">
    <subfield code="a">86</subfield>
  </datafield>
  <datafield tag="963" ind1=" " ind2=" ">
    <subfield code="a">Public</subfield>
    <subfield code="b">notvisible</subfield>
  </datafield>
  <datafield tag="980" ind1=" " ind2=" ">
    <subfield code="a">PHOTOARCIMAGES</subfield>
  </datafield>
  <datafield tag="999" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
  </datafield>
</record>
"""


def test_image():
    """Test image model from XML into JSONi."""
    blob = create_record(CDS_IMAGE)
    model = matcher(blob, 'cds_dojson.marc21.models')

    assert model == marc21

    data = model.do(blob)
    # Check the control number (doJSON)
    assert data.get('control_number') == '1782445'

    # Check the parent album (CDSImage)
    assert data['album_parent'][0]['album_id'] == '2054964'

    # Check the imprint (CDSMarc21)
    assert data['imprint'][0]['place_of_publication'] == 'Geneva'

    # Check that no fields are missing their model
    assert model.missing(blob) == []


def test_identity_check():
    """Test image model from XML into JSON."""
    blob = create_record(CDS_IMAGE)
    data = marc21.do(blob)
    back_blob = to_marc21.do(data)
    assert blob == back_blob


def test_cli_do_cds_marc21_from_xml():
    """Test MARC21 loading from XML."""
    from dojson import cli

    runner = CliRunner()

    with runner.isolated_filesystem():
        with open('record.xml', 'wb') as f:
            f.write(CDS_IMAGE.encode('utf-8'))

        result = runner.invoke(
            cli.cli,
            ['-i', 'record.xml', '-l', 'cds_marcxml', 'missing', 'cds_marc21']
        )
        assert '' == result.output
        assert 0 == result.exit_code

        result = runner.invoke(
            cli.cli,
            ['-i', 'record.xml', '-l', 'cds_marcxml', 'do', 'cds_marc21']
        )
        data = json.loads(result.output)[0]

        # Check the control number (doJSON)
        assert data.get('control_number') == '1782445'

        # Check the parent album (CDSImage)
        assert data['album_parent'][0]['album_id'] == '2054964'

        # Check the imprint (CDSMarc21)
        assert data['imprint'][0]['place_of_publication'] == 'Geneva'


def test_jsonschema():
    """Test jsonschema."""
    blob = create_record(CDS_IMAGE)
    model = matcher(blob, 'cds_dojson.marc21.models')
    data = model.do(blob)

    assert '$schema' in data
    assert data['$schema'] == {
        '$ref': 'records/image-v1.0.0.json'}
