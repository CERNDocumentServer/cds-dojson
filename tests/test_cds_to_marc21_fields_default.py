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

import json

from click.testing import CliRunner
from dojson.contrib.marc21.utils import create_record

from cds_dojson.marc21.models.default import model as marc21
from cds_dojson.matcher import matcher
from cds_dojson.to_marc21.models.default import model as to_marc21


RECORD_SIMPLE = """
<record>
    <datafield tag="021" ind1=" " ind2=" ">
        <subfield code="a">ASTM-D-1876-08</subfield>
    </datafield>
    <datafield tag="035" ind1=" " ind2=" ">
        <subfield code="9">CERCER</subfield>
        <subfield code="a">0016553</subfield>
    </datafield>
    <datafield tag="088" ind1=" " ind2=" ">
        <subfield code="a">CERN-TC-PHYSICS-63-1</subfield>
        <subfield code="9">Not displayed</subfield>
    </datafield>
    <datafield tag="245" ind1=" " ind2=" ">
        <subfield code="a">Search for long-lived particles at LHC</subfield>
    </datafield>
    <datafield tag="269" ind1=" " ind2=" ">
        <subfield code="a">Geneva</subfield>
        <subfield code="b">CERN</subfield>
        <subfield code="c">19 Mar 1986</subfield>
    </datafield>
    <datafield tag="590" ind1=" " ind2=" ">
        <subfield code="a">Sumary</subfield>
        <subfield code="b">Expansion of sumary note</subfield>
    </datafield>
    <datafield tag="591" ind1=" " ind2=" ">
        <subfield code="a">Public</subfield>
        <subfield code="b">Public_b</subfield>
    </datafield>
    <datafield tag="594" ind1=" " ind2=" ">
        <subfield code="a">SLIDE</subfield>
    </datafield>
    <datafield tag="595" ind1=" " ind2=" ">
        <subfield code="9">11142014-37_191-8-70_300-10-70-6cmx6cm</subfield>
    </datafield>
    <datafield tag="596" ind1=" " ind2=" ">
        <subfield code="a">Updated 774 values on run 1443157298</subfield>
    </datafield>
    <datafield tag="690" ind1="C" ind2=" ">
        <subfield code="a">CERN</subfield>
    </datafield>
    <datafield tag="691" ind1=" " ind2=" ">
        <subfield code="a">DI Group = SL, Directorate Group</subfield>
    </datafield>
    <datafield tag="693" ind1=" " ind2=" ">
        <subfield code="a">CERN LHC</subfield>
        <subfield code="e">ATLAS</subfield>
    </datafield>
    <datafield tag="694" ind1=" " ind2=" ">
        <subfield code="9">INSPEC</subfield>
        <subfield code="a">A9880D (Theoretical cosmology)</subfield>
    </datafield>
    <datafield tag="695" ind1=" " ind2=" ">
        <subfield code="9">INSPEC</subfield>
        <subfield code="a">cosmology</subfield>
    </datafield>
    <datafield tag="695" ind1=" " ind2=" ">
        <subfield code="9">INSPEC</subfield>
        <subfield code="a">string-theory</subfield>
    </datafield>
    <datafield tag="710" ind1="1" ind2=" ">
        <subfield code="a">
            CERN. Geneva. Technical Inspection and Safety Commission
        </subfield>
    </datafield>
    <datafield tag="721" ind1=" " ind2=" ">
        <subfield code="a">personal name</subfield>
        <subfield code="1">nome personnel</subfield>
    </datafield>
    <datafield tag="859" ind1=" " ind2=" ">
        <subfield code="a">test@test.test</subfield>
    </datafield>
    <datafield tag="901" ind1=" " ind2=" ">
        <subfield code="u">Kyoto Univ.</subfield>
    </datafield>
    <datafield tag="901" ind1=" " ind2=" ">
        <subfield code="u">Hamburg U.</subfield>
        <subfield code="u">St. Petersburg Nuclear Physics Institute</subfield>
    </datafield>
    <datafield tag="916" ind1=" " ind2=" ">
        <subfield code="s">n</subfield>
        <subfield code="w">197800</subfield>
    </datafield>
    <datafield tag="960" ind1=" " ind2=" ">
        <subfield code="a">21</subfield>
    </datafield>
    <datafield tag="961" ind1=" " ind2=" ">
        <subfield code="c">20091001</subfield>
        <subfield code="h">1425</subfield>
        <subfield code="l">CER01</subfield>
        <subfield code="x">19900128</subfield>
    </datafield>
    <datafield tag="970" ind1=" " ind2=" ">
        <subfield code="a">000029716CER</subfield>
    </datafield>
    <datafield tag="980" ind1=" " ind2=" ">
        <subfield code="a">BOOK</subfield>
    </datafield>
    <datafield tag="980" ind1=" " ind2=" ">
        <subfield code="b">REPORT</subfield>
    </datafield>
    <datafield tag="964" ind1=" " ind2=" ">
        <subfield code="a">0001</subfield>
    </datafield>
    <datafield tag="903" ind1=" " ind2=" ">
        <subfield code="b">A</subfield>
    </datafield>
    <datafield tag="903" ind1="1" ind2=" ">
        <subfield code="a">Approval requested for number CERN-PH-EP-2015-278</subfield>
        <subfield code="b">CERN-PH-EP-2015-278</subfield>
        <subfield code="c">EPPHAPP</subfield>
        <subfield code="d">2015-10-05 15:54:04</subfield>
        <subfield code="e">2015-10-12 15:54:04</subfield>
        <subfield code="f">marek.gazdzicki@cern.ch</subfield>
        <subfield code="s">waiting</subfield>
    </datafield>
    <datafield tag="903" ind1="1" ind2=" ">
        <subfield code="a">Document approved</subfield>
        <subfield code="b">CERN-PH-EP-2015-278</subfield>
        <subfield code="c">EPPHAPP</subfield>
        <subfield code="d">2015-10-07 16:54:59</subfield>
        <subfield code="f">roger.forty@cern.ch</subfield>
        <subfield code="s">approved</subfield>
    </datafield>
    <datafield tag="905" ind1=" " ind2=" ">
        <subfield code="a">Imperial College London</subfield>
        <subfield code="k"/>
        <subfield code="l"/>
        <subfield code="m">Andrei.Golutvin@cern.ch</subfield>
        <subfield code="p">Golutvin, Andrey</subfield>
        <subfield code="q"/>
    </datafield>
    <datafield tag="906" ind1=" " ind2=" ">
        <subfield code="a">CERN</subfield>
        <subfield code="m">Richard.Jacobsson@cern.ch</subfield>
        <subfield code="p">Jacobsson, Richard</subfield>
    </datafield>
    <datafield tag="910" ind1=" " ind2=" ">
        <subfield code="f">Lindner, R</subfield>
    </datafield>
    <datafield tag="913" ind1=" " ind2=" ">
        <subfield code="c">81</subfield>
        <subfield code="t">PLACB</subfield>
        <subfield code="v">11</subfield>
    </datafield>
    <datafield tag="913" ind1=" " ind2=" ">
        <subfield code="c">1848</subfield>
        <subfield code="t">PHRVA</subfield>
        <subfield code="v">A23</subfield>
    </datafield>
    <datafield tag="925" ind1=" " ind2=" ">
        <subfield code="a">2011-12-31</subfield>
        <subfield code="b">2016-12-31</subfield>
    </datafield>
    <datafield tag="927" ind1="" ind2="">
        <subfield code="a">XX-YY-00-111</subfield>
    </datafield>
    <datafield tag="937" ind1=" " ind2=" ">
        <subfield code="a">Reviewed by</subfield>
        <subfield code="s">
            Gabancho, E. (;) Rossi, L.
        </subfield>
    </datafield>
    <datafield tag="962" ind1=" " ind2=" ">
        <subfield code="b">000025169</subfield>
        <subfield code="n">vienna850422</subfield>
    </datafield>
    <datafield tag="963" ind1=" " ind2=" ">
        <subfield code="a">PUBLIC</subfield>
    </datafield>
    <datafield tag="981" ind1=" " ind2=" ">
        <subfield code="a">2063472</subfield>
    </datafield>
    <datafield tag="993" ind1=" " ind2=" ">
        <subfield code="t">Power Converters</subfield>
    </datafield>
    <datafield tag="999" ind1="C" ind2="5">
        <subfield code="h">G. Ascoli</subfield>
        <subfield code="m">Partial Wave Analysis of the 3π Decay of the A2</subfield>
        <subfield code="o">1</subfield>
        <subfield code="s">Phys.Rev.Lett.,25,962</subfield>
        <subfield code="s">,962,965</subfield>
        <subfield code="y">1970</subfield>
    </datafield>
    <datafield tag="999" ind1="C" ind2="5">
        <subfield code="h">D. Aston</subfield>
        <subfield code="m">
            Evidence for two strangeonium resonances with JPC = 1++ and 1+- in K- p interactions at 11GeV/c
        </subfield>
        <subfield code="o">2</subfield>
        <subfield code="s">Phys.Lett.,B201,573</subfield>
        <subfield code="y">1988</subfield>
    </datafield>
    <datafield tag="999" ind1="C" ind2="6">
        <subfield code="a">0-0-0-3-0-0-1</subfield>
    </datafield>
    <datafield tag="999" ind1=" " ind2=" ">
        <subfield code="a">IMAGE</subfield>
    </datafield>
</record>
"""


def test_identity_check():
    """Test image model from XML into JSON."""
    blob = create_record(RECORD_SIMPLE)
    data = marc21.do(blob)
    back_blob = to_marc21.do(data)
    assert blob == back_blob


def test_jsonschema():
    """Test jsonschema."""
    blob = create_record(RECORD_SIMPLE)
    model = matcher(blob, 'cds_dojson.marc21.models')
    data = model.do(blob)

    assert '$schema' in data
    assert data['$schema'] == {
        '$ref': 'records/default-v1.0.0.json'}
