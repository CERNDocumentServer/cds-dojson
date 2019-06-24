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
"""Book fields tests."""

from __future__ import absolute_import, print_function, unicode_literals
from cds_dojson.marc21.models.books.serial import model as serial_model
from cds_dojson.marc21.models.books.multipart import model as multipart_model
from cds_dojson.marc21.utils import create_record

marcxml = ("""<collection xmlns="http://www.loc.gov/MARC21/slim">"""
           """<record>{0}</record></collection>""")


def check_transformation(marcxml_body, json_body, model=None):
    """Check transformation."""
    blob = create_record(marcxml.format(marcxml_body))
    record = model.do(blob, ignore_missing=False)
    expected = {
        '$schema': {
            '$ref': ('records/books/book/series-v.0.0.1.json')
        },
        '_record_type': 'series',
    }
    expected.update(**json_body)
    assert record == expected


def test_serial(app):
    """Test serials."""

    with app.app_context():

        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">Esl and applied linguistics professional</subfield>
            </datafield>
            """,
            {
                'title':
                    {
                        'title': 'Esl and applied linguistics professional'
                    },
                'mode_of_issuance': 'serial'
            },
            serial_model
        )

        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">Springerbriefs in history of science and technology</subfield>
                <subfield code="x">2211-4564</subfield>
            </datafield>
            """,
            {
                'title':
                    {
                        'title': 'Springerbriefs in history'
                                 ' of science and technology'
                    },
                'mode_of_issuance': 'serial',
                'issn': '2211-4564',
            },
            serial_model
        )

        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">Springerbriefs in history of science and technology</subfield>
                <subfield code="x">2211-4564</subfield>
            </datafield>
            """,
            {
                'title':
                    {
                        'title': 'Springerbriefs in history'
                                 ' of science and technology'
                    },
                'mode_of_issuance': 'serial',
                'issn': '2211-4564',
            },
            serial_model
        )


def test_monograph(app):
    """Test monographs."""

    with app.app_context():

        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">La fisica di Amaldi</subfield>
                <subfield code="b">idee ed esperimenti : con CD-ROM</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.1</subfield>
                <subfield code="p">Introduzione alla fisica meccanica</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.2</subfield>
                <subfield code="p">Termologia, onde, relatività</subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">2 v. ; 2 CD-ROM suppl</subfield>
            </datafield>
            """,
            {
                'title': {'title': 'La fisica di Amaldi',
                          'subtitle': 'idee ed esperimenti : con CD-ROM'
                          },
                'mode_of_issuance': 'multipart_monograph',
                'number_of_volumes': '2',

            },
            multipart_model
        )

        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">La fisica di Amaldi</subfield>
                <subfield code="b">idee ed esperimenti : con CD-ROM</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.2</subfield>
                <subfield code="p">Termologia, onde, relatività</subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">La fisica di Amaldi</subfield>
                <subfield code="b">idee ed esperimenti : con CD-ROM</subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">2 v. ; 2 CD-ROM suppl</subfield>
            </datafield>
            """,
            {
                'title': {'title': 'La fisica di Amaldi',
                          'subtitle': 'idee ed esperimenti : con CD-ROM'
                          },
                'mode_of_issuance': 'multipart_monograph',
                'number_of_volumes': '2',

            },
            multipart_model
        )
