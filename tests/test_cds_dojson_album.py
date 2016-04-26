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

"""Test cds dojson album records."""

from __future__ import absolute_import

import json

from click.testing import CliRunner
from dojson.contrib.marc21.utils import create_record

from cds_dojson.marc21.models.album import model as marc21
from cds_dojson.matcher import matcher
from cds_dojson.to_marc21.models.album import model as to_marc21


CDS_ALBUM = """
<record>
  <controlfield tag="001">2054964</controlfield>
  <controlfield tag="003">SzGeCERN</controlfield>
  <controlfield tag="005">20150928110024.0</controlfield>
  <datafield tag="963" ind1=" " ind2=" ">
    <subfield code="a">PUBLIC</subfield>
  </datafield>
  <datafield tag="960" ind1=" " ind2=" ">
    <subfield code="a">116</subfield>
  </datafield>
  <datafield tag="961" ind1=" " ind2=" ">
    <subfield code="c">20050915</subfield>
    <subfield code="h">1520</subfield>
    <subfield code="l">MMD01</subfield>
    <subfield code="x">20040702</subfield>
  </datafield>
  <datafield tag="970" ind1=" " ind2=" ">
    <subfield code="a">000030391MMD</subfield>
  </datafield>
  <datafield tag="980" ind1=" " ind2=" ">
    <subfield code="a">PHOTOARC</subfield>
  </datafield>
  <datafield tag="999" ind1=" " ind2=" ">
    <subfield code="a">ALBUM</subfield>
  </datafield>
  <datafield tag="245" ind1=" " ind2=" ">
    <subfield code="a">Assembly tool for BEBC expansion system</subfield>
  </datafield>
  <datafield tag="260" ind1=" " ind2=" ">
    <subfield code="c">1970</subfield>
  </datafield>
  <datafield tag="541" ind1=" " ind2=" ">
    <subfield code="e">Rubrique: Date Planche:9 70 De:479 A:502</subfield>
  </datafield>
  <datafield tag="595" ind1=" " ind2=" ">
    <subfield code="9">11142014-37_191-8-70_300-10-70-6cmx6cm</subfield>
  </datafield>
  <datafield tag="650" ind1="1" ind2="7">
    <subfield code="2">SzGeCERN</subfield>
    <subfield code="a">Industry and Technology</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782445</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782446</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782447</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="n">Cover</subfield>
    <subfield code="r">1782448</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782449</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782450</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782451</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782452</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782453</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782454</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782455</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782456</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782457</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782458</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782459</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782460</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782461</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782462</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782463</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782464</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782465</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782466</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782467</subfield>
  </datafield>
  <datafield tag="774" ind1=" " ind2=" ">
    <subfield code="a">IMAGE</subfield>
    <subfield code="r">1782468</subfield>
  </datafield>
  <datafield tag="596" ind1=" " ind2=" ">
    <subfield code="a">Updated 774 values on run 1443157298</subfield>
  </datafield>
  <datafield tag="269" ind1=" " ind2=" ">
    <subfield code="c">Sep 1970</subfield>
  </datafield>
  <datafield tag="924" ind1=" " ind2=" ">
    <subfield code="t">40</subfield>
  </datafield>
  <datafield tag="500" ind1=" " ind2=" ">
    <subfield code="a">Album with images scanned from original photo negatives</subfield>
  </datafield>
  <datafield tag="340" ind1=" " ind2=" ">
    <subfield code="a">FILM</subfield>
  </datafield>
  <datafield tag="340" ind1=" " ind2=" ">
    <subfield code="a">Neg NB 6 x 6</subfield>
  </datafield>
  <datafield tag="923" ind1=" " ind2=" ">
    <subfield code="p">CERN PS</subfield>
    <subfield code="r">PHILIPPS</subfield>
  </datafield>
</record>
"""


def test_album():
    """Test album model from XML into JSON"""
    blob = create_record(CDS_ALBUM)
    model = matcher(blob, 'cds_dojson.marc21.models')

    assert model == marc21

    data = model.do(blob)
    assert data['physical_medium'][1][
        'material_base_and_configuration'] == ('Neg NB 6 x 6', )
    assert data['images'][3]['$ref'] == 'http://cds.cern.ch/record/1782448'
    assert data['images'][3]['relation'] == 'Cover'
    assert data['imprint'][0]['complete_date'] == 'Sep 1970'
    assert data['place_of_photo'] == [
        {'place': 'CERN PS', 'requester': 'PHILIPPS'}]

    # Check that no fields are missing their model
    assert model.missing(blob) == []


def test_identity_check():
    """Test image model from XML into JSON."""
    blob = create_record(CDS_ALBUM)
    data = marc21.do(blob)
    back_blob = to_marc21.do(data)
    assert blob == back_blob


def test_cli_do_cds_marc21_from_xml():
    """Test MARC21 loading from XML."""
    from dojson import cli

    runner = CliRunner()

    with runner.isolated_filesystem():
        with open('record.xml', 'wb') as f:
            f.write(CDS_ALBUM.encode('utf-8'))

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
        assert data['physical_medium'][1][
            'material_base_and_configuration'] == ['Neg NB 6 x 6']

        # Check the parent album (CDSImage)
        assert data['images'][3]['$ref'] == 'http://cds.cern.ch/record/1782448'
        assert data['images'][3]['relation'] == 'Cover'

        # Check the imprint (CDSMarc21)
        assert data['imprint'][0]['complete_date'] == 'Sep 1970'


def test_jsonschema():
    """Test jsonschema."""
    blob = create_record(CDS_ALBUM)
    model = matcher(blob, 'cds_dojson.marc21.models')
    data = model.do(blob)

    assert '$schema' in data
    assert data['$schema'] == {
        '$ref': 'records/album-v1.0.0.json'}
