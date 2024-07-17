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

from cds_dojson.marc21.fields.books.errors import MissingRequiredField, UnexpectedValue
from cds_dojson.marc21.models.books.base import get_migration_dict
from cds_dojson.marc21.models.books.multipart import model as multipart_model
from cds_dojson.marc21.models.books.serial import model as serial_model
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
                    [
                        'Esl and applied linguistics professional'
                    ],
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
                    [
                        'Springerbriefs in history'
                        ' of science and technology'
                    ],
                'mode_of_issuance': 'SERIAL',
                'identifiers': [{'scheme': 'ISSN', 'value': '2211-4564'}],
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
                    [
                        'Springerbriefs in history'
                        ' of science and technology'
                    ],
                'mode_of_issuance': 'SERIAL',
                'identifiers': [{'scheme': 'ISSN', 'value': '2211-4564'}],
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
                        [
                            'Springerbriefs in history'
                            ' of science and technology'
                        ],
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
                'title': 'La fisica di Amaldi',
                'alternative_titles': [
                    {
                        'value': 'idee ed esperimenti : con CD-ROM',
                        'type': 'SUBTITLE'
                    }
                ],
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                'number_of_volumes': '2',
                '_migration': {
                    **get_migration_dict(),
                    'record_type': 'multipart', 'volumes': [
                        {'title': 'Introduzione alla fisica meccanica',
                         'volume': '1'},
                        {'title': 'Termologia, onde, relatività',
                         'volume': '2'}
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
                'title': 'La fisica di Amaldi',
                'alternative_titles': [
                    {
                        'value': 'idee ed esperimenti : con CD-ROM',
                        'type': 'SUBTITLE'
                    }
                ],
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                'number_of_volumes': '2',
                '_migration': {
                    **get_migration_dict(),
                    'record_type': 'multipart', 'volumes': [
                        {'title': 'Termologia, onde, relatività',
                         'volume': '2'}
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
                'title': 'La fisica di Amaldi',
                'alternative_titles': [
                    {
                        'value': 'idee ed esperimenti : con CD-ROM',
                        'type': 'SUBTITLE'
                    }
                ],
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                '_migration': {
                    **get_migration_dict(),
                    'record_type': 'multipart', 'volumes': [
                        {'title': 'Termologia, onde, relatività',
                         'volume': '2'}
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
                'title': 'La fisica di Amaldi',
                'alternative_titles': [
                    {
                        'value': 'idee ed esperimenti : con CD-ROM',
                        'type': 'SUBTITLE'
                    }
                ],
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                '_migration': {
                    **get_migration_dict(),
                    'record_type': 'multipart', 'volumes': [
                        {'title': 'Termologia, onde, relatività', 'volume': '2'}
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
                    'title': 'La fisica di Amaldi',
                    'alternative_titles': [
                        {'value': 'idee ed esperimenti : con CD-ROM',
                         'type': 'SUBTITLE'}
                    ],
                    'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                    'number_of_volumes': '2',
                    '_migration': {
                        **get_migration_dict(),
                        'record_type': 'multipart', 'volumes': []}
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
                    'title': 'La fisica di Amaldi',
                    'alternative_titles': [
                        {'value': 'idee ed esperimenti : con CD-ROM',
                         'type': 'SUBTITLE'}
                    ],
                    'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                    'number_of_volumes': '2',
                    '_migration': {**get_migration_dict(), 'record_type': 'multipart', 'volumes': []}
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
                '_migration': {
                    **get_migration_dict(),
                    'volumes': [
                        {
                            'volume': '3',
                            'isbn': '1108052819',
                            'physical_description': 'print version, paperback',
                            'is_electronic': False,
                        },
                        {
                            'volume': '3',
                            'isbn': '9781108052818',
                            'physical_description':
                                'print version, paperback',
                            'is_electronic': False,
                        },
                        {
                            'volume': '2',
                            'isbn': '9781108052801',
                            'physical_description':
                                'print version, paperback',
                            'is_electronic': False,
                        },
                        {
                            'volume': '2',
                            'isbn': '1108052800',
                            'physical_description':
                                'print version, paperback',
                            'is_electronic': False,
                        },
                        {
                            'volume': '1',
                            'isbn': '9781108052795',
                            'physical_description':
                                'print version, paperback',
                            'is_electronic': False,
                        },
                        {
                            'volume': '1',
                            'isbn': '1108052797',
                            'physical_description':
                                'print version, paperback',
                            'is_electronic': False,
                        },
                        {
                            'title': '1865-1874',
                            'volume': '1'
                        },
                        {
                            'title': '1875-1881',
                            'volume': '2'
                        },
                        {
                            'title': '1882-1905',
                            'volume': '3'
                        },
                    ],
                    'record_type': 'multipart',
                },
                'title': 'Wissenschaftliche Abhandlungen',
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                'number_of_volumes': '3',
                'identifiers': [{'scheme': 'ISBN', 'value': '9781108052825'}],
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


def test_monograph_volume_migration_no_description(app):
    """Test multipart volume without description (https://cds.cern.ch/record/287517)."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
            <subfield code="a">1560810726</subfield>
            <subfield code="u">v.13</subfield>
            </datafield>
            """,
            {'_migration': {
                **get_migration_dict(),
                'record_type': 'multipart',
                'volumes': [{'is_electronic': False,
                             'isbn': '1560810726',
                             'volume': '13'}]},
                'mode_of_issuance': 'MULTIPART_MONOGRAPH'}, multipart_model)


def test_monograph_with_electronic_isbns(app):
    """Test multipart monographs with electronic isbns."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">0817631852</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">0817631852</subfield>
                <subfield code="u">print version (v.2)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">0817631879</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9780817631857</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9780817631871</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781461239406</subfield>
                <subfield code="b">electronic version (v.2)</subfield>
                <subfield code="u">electronic version (v.2)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781461251545</subfield>
                <subfield code="b">electronic version (v.1)</subfield>
                <subfield code="u">electronic version (v.1)</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781461295891</subfield>
                <subfield code="u">print version (v.1)</subfield>
            </datafield>
            """,
            {
                'identifiers': [
                    {'scheme': 'ISBN', 'value': '0817631852'},
                    {'scheme': 'ISBN', 'value': '0817631879'},
                    {'scheme': 'ISBN', 'value': '9780817631857'},
                    {'scheme': 'ISBN', 'value': '9780817631871'},

                ],
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                '_migration': {
                    **get_migration_dict(),
                    'record_type': 'multipart',
                    'volumes': [
                        {
                            'is_electronic': False,
                            'physical_description': 'print version',
                            'volume': '2',
                            'isbn': '0817631852'
                        },
                        {
                            'is_electronic': True,
                            'physical_description': 'electronic version',
                            'volume': '2',
                            'isbn': '9781461239406'
                        },
                        {
                            'is_electronic': True,
                            'physical_description': 'electronic version',
                            'volume': '1',
                            'isbn': '9781461251545'
                        },
                        {
                            'is_electronic': False,
                            'physical_description': 'print version',
                            'volume': '1',
                            'isbn': '9781461295891'
                        },
                    ],
                },
            }, multipart_model
        )


def test_monograph_volume_migration_doi(app):
    """Test multipart volume with DOIs attached to volumes."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="024" ind1="7" ind2=" ">
            <subfield code="2">DOI</subfield>
            <subfield code="a">10.1007/978-3-030-49613-5</subfield>
            <subfield code="q">ebook (v.1)</subfield>
            </datafield>
            """,
            {
                '_migration':
                {
                    **get_migration_dict(),
                    'record_type': 'multipart',
                    'volumes': [{
                        'doi': '10.1007/978-3-030-49613-5',
                        'material': 'ebook',
                        'source': None,
                        'volume': '1'
                    }]
                },
                'mode_of_issuance': 'MULTIPART_MONOGRAPH'
            },
            multipart_model)


def test_monograph_volume_barcode(app):
    """Test multipart volume with barcodes (= items)."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="088" ind1=" " ind2=" ">
            <subfield code="n">pt.A</subfield>
            <subfield code="x">73-0089-0</subfield>
            </datafield>
            """,
            {
                '_migration':
                {
                    **get_migration_dict(),
                    'record_type': 'multipart',
                    'volumes': [{'barcode': '73-0089-0', 'volume': 'A'}]
                },
                'mode_of_issuance': 'MULTIPART_MONOGRAPH'
            },
            multipart_model)


def test_monograph_volume_url(app):
    """Test multipart volume with urls."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="856" ind1="4" ind2=" ">
            <subfield code="u">https://cds.cern.ch/auth.py?r=EBLIB_P_1890382</subfield>
            <subfield code="y">ebook (v.1)</subfield>
            </datafield>
            """,
            {
                '_migration':
                {
                    **get_migration_dict(),
                    'record_type': 'multipart',
                    'volumes': [{
                        'description': 'ebook',
                        'url': 'https://cds.cern.ch/auth.py?r=EBLIB_P_1890382',
                        'volume': '1'}]
                },
                'mode_of_issuance': 'MULTIPART_MONOGRAPH'
            },
            multipart_model)


def test_monograph_legacy_representation(app):
    """Test multipart representation in CDS."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="596" ind1=" " ind2=" ">
            <subfield code="a">MULTIVOLUMES-1</subfield>
            </datafield>
            <datafield tag="597" ind1=" " ind2=" ">
            <subfield code="a">Vol965</subfield>
            </datafield>
            """,
            {
                '_migration':
                {
                    **get_migration_dict(),
                    'record_type': 'multipart',
                    'multipart_id': 'Vol965',
                    'multivolume_record_format': True,
                },
                'mode_of_issuance': 'MULTIPART_MONOGRAPH'
            },
            multipart_model)


def test_monograph_legacy_report_number(app):
    """Test multipart representation in CDS."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="088" ind1=" " ind2=" ">
            <subfield code="a">IAEA-INIS-20-REV-0-D</subfield>
            </datafield>
            """,
            {
                '_migration':
                {
                    **get_migration_dict(),
                    'record_type': 'multipart',
                },
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                'identifiers': [{'scheme': 'report_number', 'value': 'IAEA-INIS-20-REV-0-D'}]
            },
            multipart_model)


def test_monograph_series_authors(app):
    """Test multipart authors."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Mehra, Jagdish</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Rechenberg, Helmut</subfield>
            </datafield>
            """,
            {
                '_migration':
                {
                    **get_migration_dict(),
                    'record_type': 'multipart',
                    'authors': [
                        {
                            'full_name': 'Mehra, Jagdish',
                            'roles': ['AUTHOR']
                        },
                        {
                            'full_name': 'Rechenberg, Helmut',
                            'roles': ['AUTHOR']
                        }],
                },
                'mode_of_issuance': 'MULTIPART_MONOGRAPH',
                'authors': ['Mehra, Jagdish', 'Rechenberg, Helmut']
            },
            multipart_model)
