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

import pytest
from dojson.errors import MissingRule

from cds_dojson.marc21.fields.books.errors import UnexpectedValue, \
    MissingRequiredField
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
        '$schema': 'https://127.0.0.1:5000/schemas/series/series-v1.0.0.json',
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
                    [{
                        'title': 'Esl and applied linguistics professional'
                    }],
                'mode_of_issuance': 'SERIAL',
                '_migration': {'record_type': 'serial', 'children': []}
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
                    [{
                        'title': 'Springerbriefs in history'
                                 ' of science and technology'
                    }],
                'mode_of_issuance': 'SERIAL',
                'issn': '2211-4564',
                '_migration': {'record_type': 'serial', 'children': []}
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
                    [{
                        'title': 'Springerbriefs in history'
                                 ' of science and technology'
                    }],
                'mode_of_issuance': 'SERIAL',
                'issn': '2211-4564',
                '_migration': {'record_type': 'serial', 'children': []}
            },
            serial_model
        )

        with pytest.raises(MissingRule):
            check_transformation(
                """
                <datafield tag="490" ind1="1" ind2=" ">
                    <subfield code="a">Modesty Blaise / Peter O'Donnell</subfield>
                </datafield>
                """,
                {
                    'title':
                        [{
                            'title': 'Springerbriefs in history'
                                     ' of science and technology'
                        }],
                    '_migration': {'record_type': 'serial', 'children': []}
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
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                'number_of_volumes': '2',
                '_migration': {'record_type': 'multipart', 'volumes': [
                    {'title': 'Introduzione alla fisica meccanica',
                     'volume': 1},
                    {'title': 'Termologia, onde, relatività',
                     'volume': 2}
                ]}

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
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">2 v. ; 2 CD-ROM suppl</subfield>
            </datafield>
            """,
            {
                'title': {'title': 'La fisica di Amaldi',
                          'subtitle': 'idee ed esperimenti : con CD-ROM'
                          },
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                'number_of_volumes': '2',
                '_migration': {'record_type': 'multipart', 'volumes': [
                    {'title': 'Termologia, onde, relatività',
                     'volume': 2}
                ]}

            },
            multipart_model,
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
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">2 p ; 2 CD-ROM suppl</subfield>
            </datafield>
            """,
            {
                'title': {'title': 'La fisica di Amaldi',
                          'subtitle': 'idee ed esperimenti : con CD-ROM'
                          },
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                '_migration': {'record_type': 'multipart', 'volumes': [
                    {'title': 'Termologia, onde, relatività',
                     'volume': 2}
                ]}

            },
            multipart_model,
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
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">multi. p ; 2 CD-ROM suppl</subfield>
            </datafield>

            """,
            {
                'title': {'title': 'La fisica di Amaldi',
                          'subtitle': 'idee ed esperimenti : con CD-ROM'
                          },
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                '_migration': {'record_type': 'multipart', 'volumes': [
                    {'title': 'Termologia, onde, relatività',
                     'volume': 2}
                ]}

            },
            multipart_model,
        )

        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="245" ind1=" " ind2=" ">
                    <subfield code="a">La fisica di Amaldi</subfield>
                    <subfield code="b">idee ed esperimenti : con CD-ROM</subfield>
                </datafield>
                <datafield tag="246" ind1=" " ind2=" ">
                    <subfield code="a">v.2</subfield>
                    <subfield code="b">Termologia, onde, relatività</subfield>
                </datafield>
                <datafield tag="300" ind1=" " ind2=" ">
                    <subfield code="a">2 v. ; 2 CD-ROM suppl</subfield>
                </datafield>
                """,
                {
                    'title': {'title': 'La fisica di Amaldi',
                              'subtitle': 'idee ed esperimenti : con CD-ROM'
                              },
                    'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                    'number_of_volumes': '2',
                    '_migration': {'record_type': 'multipart', 'volumes': [

                    ]}

                },
                multipart_model,
            )

        with pytest.raises(MissingRequiredField):
            check_transformation(
                """
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
                    'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                    'number_of_volumes': '2',
                    '_migration': {'record_type': 'multipart', 'volumes': []}
                },
                multipart_model,
            )


def test_monograph_migration(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">1108052819</subfield>
                <subfield code="u">print version, paperback (v.3)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781108052818</subfield>
                <subfield code="u">print version, paperback (v.3)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781108052801</subfield>
                <subfield code="u">print version, paperback (v.2)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">1108052800</subfield>
                <subfield code="u">print version, paperback (v.2)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781108052825</subfield>
                <subfield code="u">print version, paperback (set)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781108052795</subfield>
                <subfield code="u">print version, paperback (v.1)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">1108052797</subfield>
                <subfield code="u">print version, paperback (v.1)</subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Wissenschaftliche Abhandlungen</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.1</subfield>
                <subfield code="p">1865-1874</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.2</subfield>
                <subfield code="p">1875-1881</subfield>
            </datafield>
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="n">v.3</subfield>
                <subfield code="p">1882-1905</subfield>
            </datafield>
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">3 v</subfield>
            </datafield>
            """,
            {
                '_migration': {'volumes': [
                    {
                        'volume': 3,
                        'isbn': '1108052819',
                        'physical_description':
                            'print version, paperback',
                    },
                    {
                        'volume': 3,
                        'isbn': '9781108052818',
                        'physical_description':
                            'print version, paperback',
                    },
                    {
                        'volume': 2,
                        'isbn': '9781108052801',
                        'physical_description':
                            'print version, paperback',
                    },
                    {
                        'volume': 2,
                        'isbn': '1108052800',
                        'physical_description':
                            'print version, paperback',
                    },
                    {
                        'volume': 1,
                        'isbn': '9781108052795',
                        'physical_description':
                            'print version, paperback',
                    },
                    {
                        'volume': 1,
                        'isbn': '1108052797',
                        'physical_description':
                            'print version, paperback',
                    },
                    {
                        'title': '1865-1874',
                        'volume': 1
                    },
                    {
                        'title': '1875-1881',
                        'volume': 2
                    },
                    {
                        'title': '1882-1905',
                        'volume': 3
                    },
                ],
                    'record_type': 'multipart',
                },
                "title": {'title': 'Wissenschaftliche Abhandlungen'},
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                'number_of_volumes': '3',
                'isbns': ['9781108052825'],
                'physical_description': 'print version, paperback',
            }, multipart_model)


def test_monograph_invalid_volume_migration(app):
    with app.app_context():
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9788808175366</subfield>
                <subfield code="u">print version, paperback (v.1)</subfield>
                </datafield>
                <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9788808247049</subfield>
                <subfield code="u">print version, paperback (v.2)</subfield>
                </datafield>
                <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9788808047038</subfield>
                <subfield code="u">print version, paperback (v.2, CD-ROM)</subfield>
                </datafield>
                """,
                {}, multipart_model)


def test_monograph_invalid_volume_migration_no_description(app):
    """Test invalid multipart volume (https://cds.cern.ch/record/287517)."""
    with app.app_context():
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">1560810726</subfield>
                <subfield code="u">v.13</subfield>
                </datafield>
                """,
                {}, multipart_model)
