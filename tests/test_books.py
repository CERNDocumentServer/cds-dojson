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

from cds_dojson.marc21.fields.books.errors import UnexpectedValue, \
    ManualMigrationRequired, MissingRequiredField
from cds_dojson.marc21.fields.books.values_mapping import mapping, MATERIALS
from cds_dojson.marc21.models.books.book import model
from cds_dojson.marc21.utils import create_record


marcxml = ("""<collection xmlns="http://www.loc.gov/MARC21/slim">"""
           """<record>{0}</record></collection>""")


def test_mapping():
    with pytest.raises(UnexpectedValue):
        assert mapping(MATERIALS, 'softwa', raise_exception=True) == 'software'


def check_transformation(marcxml_body, json_body):
    blob = create_record(marcxml.format(marcxml_body))
    record = model.do(blob, ignore_missing=False)
    expected = {
        '$schema': {
            '$ref': ('records/books/book/book-v.0.0.1.json')
        }
    }
    expected.update(**json_body)
    assert record == expected


def test_subject_classification(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="082" ind1="0" ind2="4">
                <subfield code="a">515.353</subfield>
                <subfield code="2">23</subfield>
            </datafield>
            """, {
                'subject_classification': [
                    {'value': '515.353',
                     'schema': 'Dewey'}
                ]
            })
        check_transformation(
            """
            <datafield tag="050" ind1=" " ind2="4">
                <subfield code="a">QA76.642</subfield>
            </datafield>
            """, {
                'subject_classification': [
                    {'value': 'QA76.642',
                     'schema': 'LoC'}
                ]
            })
        check_transformation(
            """
            <datafield tag="050" ind1=" " ind2="4">
                <subfield code="a">QA76.642</subfield>
            </datafield>
            <datafield tag="082" ind1=" " ind2=" ">
                <subfield code="a">005.275</subfield>
            </datafield>
            """, {
                'subject_classification': [
                    {'value': 'QA76.642',
                     'schema': 'LoC'},
                    {'value': '005.275',
                     'schema': 'Dewey'},
                ]
            })
        check_transformation(
            """
            <datafield tag="080" ind1=" " ind2=" ">
                <subfield code="a">528</subfield>
            </datafield>
            """, {
                'subject_classification': [
                    {'value': '528',
                     'schema': 'UDC'}
                ]
            })
        check_transformation(
            """
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="a">25040.40</subfield>
            </datafield>
            """, {

                'subject_classification': [
                    {'value': '25040.40',
                     'schema': 'ICS'}
                ]
            })
        check_transformation(
            """
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="a">13.75.Jz</subfield>
            </datafield>
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="a">13.60.Rj</subfield>
            </datafield>
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="a">14.20.Jn</subfield>
            </datafield>
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">PACS</subfield>
                <subfield code="a">25.80.Nv</subfield>
            </datafield>
            """, {
                'keywords': [
                    {'name': '13.75.Jz', 'source': 'PACS'},
                    {'name': '13.60.Rj', 'source': 'PACS'},
                    {'name': '14.20.Jn', 'source': 'PACS'},
                    {'name': '25.80.Nv', 'source': 'PACS'},
                ]
            }
        )
        check_transformation(
            """
            <datafield tag="084" ind1=" " ind2=" ">
                <subfield code="2">CERN Yellow Report</subfield>
                <subfield code="a">CERN-2018-003-CP</subfield>
            </datafield>
            """,
            {}
        )


def test_acquisition(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="916" ind1=" " ind2=" ">
                <subfield code="s">h</subfield>
                <subfield code="w">201829</subfield>
            </datafield>
            """, {
                'acquisition_source': {'datetime': '2018-07-16'},
            })
        check_transformation(
            """
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">SPR201701</subfield>
            </datafield>
            """, {
                'acquisition_source': {'datetime': '2017-01-01',
                                       'source': 'SPR'},
            })
        check_transformation(
            """
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">random text</subfield>
            </datafield>
            """, {
                '_private_notes': [
                    {'value': 'random text'},
                ]
            })
        with pytest.raises(ManualMigrationRequired):
            check_transformation(
                """
                <datafield tag="916" ind1=" " ind2=" ">
                    <subfield code="s">h</subfield>
                    <subfield code="w">201829</subfield>
                </datafield>
                <datafield tag="595" ind1=" " ind2=" ">
                    <subfield code="a">SPR201701</subfield>
                </datafield>
                """, {
                    'acquisition_source': {'datetime': '2018-07-16'},
                })


def test_collections(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="b">LEGSERLIB</subfield>
            </datafield>
            """, {
                '_collections': ['LEGSERLIB'],
            })
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">LEGSERLIB</subfield>
            </datafield>
            """, {
                '_collections': ['LEGSERLIB'],
            })
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">LEGSERLIB</subfield>
            </datafield>
            """, {
                '_collections': ['LEGSERLIB'],
            })
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">LEGSERLIBINTLAW</subfield>
            </datafield>
            """,
            {
                '_collections': ['LEGSERLIBINTLAW'],
            }
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">BOOKSHOP</subfield>
            </datafield>
            """,
            {
                '_collections': ['BOOKSHOP'],
            }
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">BOOKSHOP</subfield>
            </datafield>
            """,
            {
                '_collections': ['BOOKSHOP'],
            }
        )
        check_transformation(
            """
            <datafield tag="697" ind1="C" ind2=" ">
                <subfield code="a">LEGSERLIBLEGRES</subfield>
            </datafield>
            """,
            {
                '_collections': ['LEGSERLIBLEGRES'],
            }
        )


def test_document_type(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            """, {
                'document_type': ['BOOK'],
            })
        check_transformation(
            """
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">21</subfield>
            </datafield>
            """, {
                'document_type': ['BOOK'],
            })
        check_transformation(
            """
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">42</subfield>
            </datafield>
            """, {
                'document_type': ['PROCEEDINGS'],
            })
        check_transformation(
            """
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">43</subfield>
            </datafield>
            """, {
                'document_type': ['PROCEEDINGS'],
            })
        check_transformation(
            """
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            <datafield tag="690" ind1="C" ind2=" ">
                <subfield code="a">REPORT</subfield>
            </datafield>
            """,
            {'document_type': ['BOOK', 'REPORT']}
        )


def test_document_type_collection(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="b">LEGSERLIB</subfield>
            </datafield>
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">BOOK</subfield>
            </datafield>
            """, {
                '_collections': ['LEGSERLIB'],
                'document_type': ['BOOK'],
            })
        check_transformation(
            """
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="a">LEGSERLIB</subfield>
            </datafield>
            <datafield tag="980" ind1=" " ind2=" ">
                <subfield code="b">BOOK</subfield>
            </datafield>
            """, {
                '_collections': ['LEGSERLIB'],
                'document_type': ['BOOK'],
            })


def test_urls(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="960" ind1=" " ind2=" ">
                <subfield code="a">42</subfield>
            </datafield>
            <datafield tag="8564" ind1=" " ind2=" ">
                <subfield code="u">cds.cern.ch</subfield>
            </datafield>
            """, {
                'document_type': ['PROCEEDINGS'],
                'urls': [{'value': 'cds.cern.ch'}],
            })
        check_transformation(
            """
            <datafield tag="8564" ind1=" " ind2=" ">
                <subfield code="u">cds.cern.ch</subfield>
            </datafield>
            """, {
                'urls': [{'value': 'cds.cern.ch'}],
            })
        with pytest.raises(ManualMigrationRequired):
            check_transformation(
                """
                <datafield tag="8564" ind1=" " ind2=" ">
                    <subfield code="u">cds.cern.ch</subfield>
                    <subfield code="y">description</subfield>
                </datafield>
                """, {
                    'urls': [{'value': 'cds.cern.ch',
                              'description': 'description'}],
                })


def test_acquisition_email(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="859" ind1=" " ind2=" ">
                <subfield code="f">karolina.przerwa@cern.ch</subfield>
            </datafield>
            """, {
                'acquisition_source': {'email': 'karolina.przerwa@cern.ch'},
            })
        check_transformation(
            """
            <datafield tag="916" ind1=" " ind2=" ">
                <subfield code="s">h</subfield>
                <subfield code="w">201829</subfield>
            </datafield>
            <datafield tag="859" ind1=" " ind2=" ">
                <subfield code="f">karolina.przerwa@cern.ch</subfield>
            </datafield>
            """, {
                'acquisition_source': {'datetime': '2018-07-16',
                                       'email': 'karolina.przerwa@cern.ch'},
            })


def test_authors(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Frampton, Paul H</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Glashow, Sheldon Lee</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Van Dam, Hendrik</subfield>
                <subfield code="e">ed.</subfield>
            </datafield>
            <datafield tag="100" ind1=" " ind2=" ">
                <subfield code="a">Seyfert, Paul</subfield>
                <subfield code="0">AUTHOR|(INSPIRE)INSPIRE-00341737</subfield>
                <subfield code="0">AUTHOR|(SzGeCERN)692828</subfield>
                <subfield code="0">AUTHOR|(CDS)2079441</subfield>
                <subfield code="u">CERN</subfield>
                <subfield code="m">paul.seyfert@cern.ch</subfield>
            </datafield>
            <datafield tag="720" ind1=" " ind2=" ">
                <subfield code="a">Neubert, Matthias</subfield>
            </datafield>
            <datafield tag="100" ind1=" " ind2=" ">
                <subfield code="a">John Doe</subfield>
                <subfield code="u">CERN</subfield>
                <subfield code="u">Univ. Gent</subfield>
            </datafield>
            <datafield tag="100" ind1=" " ind2=" ">
                <subfield code="a">Jane Doe</subfield>
                <subfield code="u">CERN</subfield>
                <subfield code="u">Univ. Gent</subfield>
            </datafield>
            """, {
                'authors': [
                    {
                        'full_name': 'Frampton, Paul H',
                        'role': 'editor',
                        'alternative_names': 'Neubert, Matthias'
                    },
                    {
                        'full_name': 'Glashow, Sheldon Lee',
                        'role': 'editor'
                    },
                    {
                        'full_name': 'Van Dam, Hendrik',
                        'role': 'editor'
                    },
                    {
                        'full_name': 'Seyfert, Paul',
                        'affiliations': ['CERN'],
                    },
                    {
                        'full_name': 'John Doe',
                        'affiliations': ['CERN', 'Univ. Gent'],
                    },
                    {
                        'full_name': 'Jane Doe',
                        'affiliations': ['CERN', 'Univ. Gent'],
                    }
                ],
            })


# better example to be provided
def test_corporate_author(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="710" ind1=" " ind2=" ">
                <subfield code="a"> Springer</subfield>
            </datafield>
            """, {
                'corporate_authors': ['Springer'],
            })
        check_transformation(
            """
            <datafield tag="110" ind1=" " ind2=" ">
                <subfield code="a">Marston, R M</subfield>
            </datafield>
            """, {
                'corporate_authors': [
                    'Marston, R M',
                ],
            })


def test_collaborations(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="710" ind1=" " ind2=" ">
                <subfield code="5">PH-EP</subfield>
            </datafield>
            <datafield tag="710" ind1=" " ind2=" ">
                <subfield code="g">ATLAS Collaboration</subfield>
            </datafield>
            """,
            {'collaborations': [{'value': 'PH-EP'}, {'value': 'ATLAS'}]}
        )


def test_publication_info(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="c">1692-1695</subfield>
                <subfield code="n">10</subfield>
                <subfield code="y">2007</subfield>
                <subfield code="p">Radiat. Meas.</subfield>
                <subfield code="v">42</subfield>
            </datafield>
            <datafield tag="962" ind1=" " ind2=" ">
                <subfield code="n">BOOK</subfield>
            </datafield>
            """,
            {
                'publication_info': [{
                    'page_start': 1692,
                    'page_end': 1695,
                    'year': 2007,
                    'journal_title': 'Radiat. Meas.',
                    'journal_issue': '10',
                    'journal_volume': '42',
                    'material': 'BOOK',
                }]
            }
        )
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="c">1692-1695</subfield>
                <subfield code="n">10</subfield>
                <subfield code="y">2007</subfield>
                <subfield code="p">Radiat. Meas.</subfield>
                <subfield code="v">42</subfield>
            </datafield>
            <datafield tag="962" ind1=" " ind2=" ">
                <subfield code="n">fsihfifri</subfield>
            </datafield>
            """,
            {
                'publication_info': [{
                    'page_start': 1692,
                    'page_end': 1695,
                    'year': 2007,
                    'journal_title': 'Radiat. Meas.',
                    'journal_issue': '10',
                    'journal_volume': '42',
                    'cern_conference_code': 'fsihfifri',
                }]
            }
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="773" ind1=" " ind2=" ">
                    <subfield code="c">10-95-5</subfield>
                    <subfield code="n">10</subfield>
                    <subfield code="y">2007</subfield>
                    <subfield code="p">Radiat. Meas.</subfield>
                    <subfield code="v">42</subfield>
                </datafield>
                """,
                {
                    'publication_info': [{
                        'page_start': 1692,
                        'page_end': 1695,
                        'year': 2007,
                        'journal_title': 'Radiat. Meas.',
                        'journal_issue': '10',
                        'journal_volume': '42',
                    }]
                }
            )
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="o">1692 numebrs text etc</subfield>
                <subfield code="x">Random text</subfield>
            </datafield>
            """,
            {
                'publication_info': [
                    {'pubinfo_freetext': '1692 numebrs text etc Random text'}
                ]
            }
        )
        check_transformation(
            """
            <datafield tag="962" ind1=" " ind2=" ">
                <subfield code="b">2155631</subfield>
                <subfield code="n">genoa20160330</subfield>
                <subfield code="k">1</subfield>
            </datafield>
            """,
            {
                'publication_info': [
                    {'page_start': 1,
                     'cern_conference_code': 'genoa20160330',
                     'parent_record':
                         {'$ref': 'https://cds.cern.ch/record/2155631'}}
                ]
            }
        )
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="c">1692-1695</subfield>
                <subfield code="n">10</subfield>
                <subfield code="y">2007</subfield>
                <subfield code="p">Radiat. Meas.</subfield>
                <subfield code="o">1692 numebrs text etc</subfield>
                <subfield code="x">Random text</subfield>
            </datafield>
            """,
            {
                'publication_info': [{
                    'page_start': 1692,
                    'page_end': 1695,
                    'year': 2007,
                    'journal_title': 'Radiat. Meas.',
                    'journal_issue': '10',
                    'pubinfo_freetext': '1692 numebrs text etc Random text',
                }]
            }
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="773" ind1=" " ind2=" ">
                    <subfield code="c">1692-1695-2000</subfield>
                    <subfield code="n">10</subfield>
                    <subfield code="y">2007</subfield>
                    <subfield code="p">Radiat. Meas.</subfield>
                    <subfield code="o">1692 numebrs text etc</subfield>
                    <subfield code="x">Random text</subfield>
                </datafield>
                """,
                {
                    'publication_info': [{
                        'page_start': 1692,
                        'page_end': 1695,
                        'year': 2007,
                        'journal_title': 'Radiat. Meas.',
                        'journal_issue': '10',
                        'pubinfo_freetext': '1692 numebrs '
                                            'text etc Random text',
                    }]
                }
            )


def test_related_record(app):
    with app.app_context():
        with pytest.raises(ManualMigrationRequired):
            check_transformation(
                """
                <datafield tag="775" ind1=" " ind2=" ">
                    <subfield code="b">Test text</subfield>
                    <subfield code="c">Random text</subfield>
                    <subfield code="w">748392</subfield>
                </datafield>
                """,
                {
                    'related_records': [
                        {'record':
                            {'$ref': 'https://cds.cern.ch/record/748392'}}
                    ]
                }
            )
        with pytest.raises(ManualMigrationRequired):
            check_transformation(
                """
                <datafield tag="787" ind1=" " ind2=" ">
                    <subfield code="i">Random text</subfield>
                    <subfield code="w">7483924</subfield>
                </datafield>
                """,
                {
                    'related_records': [
                        {'record':
                            {'$ref': 'https://cds.cern.ch/record/7483924'}}
                    ]
                }
            )
        check_transformation(
            """
            <datafield tag="775" ind1=" " ind2=" ">
                <subfield code="w">7483924</subfield>
            </datafield>
            <datafield tag="787" ind1=" " ind2=" ">
                <subfield code="w">748</subfield>
            </datafield>
            """,
            {
                'related_records': [
                    {'record': {'$ref': 'https://cds.cern.ch/record/7483924'}},
                    {'record': {'$ref': 'https://cds.cern.ch/record/748'}}
                ]
            }
        )


def test_accelerator_experiments(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">CERN LHC</subfield>
                <subfield code="e">ATLAS</subfield>
            </datafield>
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">CERN LHC</subfield>
                <subfield code="e">CMS</subfield>
            </datafield>
            """,
            {
                'accelerator_experiments': [
                    {'accelerator': 'CERN LHC',
                     'experiment': 'ATLAS'},
                    {'accelerator': 'CERN LHC',
                     'experiment': 'CMS'}
                ]
            }
        )


def test_isbns(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630814434</subfield>
                <subfield code="q">(electronic bk.)</subfield>
                <subfield code="u">electronic version</subfield>
                <subfield code="b">electronic version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630811051</subfield>
                <subfield code="u">electronic version</subfield>
            </datafield>
            """, {
                'isbns': [{
                    'value': '9781630814434',
                    'medium': 'electronic version',
                }, {
                    'value': '9781630811051',
                    'medium': 'electronic version',
                }],
            })
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">0691090858</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9780691090856</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781400889167</subfield>
                <subfield code="q">(electronic bk.)</subfield>
                <subfield code="u">electronic version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="u">electronic version</subfield>
                <subfield code="z">9780691090849</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="u">electronic version</subfield>
                <subfield code="z">9780691090849</subfield>
            </datafield>
            """,
            {'isbns': [
                {'value': '0691090858'},
                {'value': '9780691090856'},
                {'value': '9781400889167', 'medium': 'electronic version'},
                {'value': '9780691090849', 'medium': 'electronic version'},
            ],
            }
        )
        with pytest.raises(ManualMigrationRequired):
            check_transformation(
                """
                <datafield tag="020" ind1=" " ind2=" ">
                    <subfield code="q">(electronic bk.)</subfield>
                    <subfield code="u">electronic version</subfield>
                    <subfield code="b">electronic version</subfield>
                </datafield>
                <datafield tag="020" ind1=" " ind2=" ">
                    <subfield code="u">electronic version</subfield>
                </datafield>
                """, {
                    'isbns': [{
                        'medium': 'electronic version',
                    }, {
                        'medium': 'electronic version',
                    }],
                })
        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630814434</subfield>
                <subfield code="q">(electronic bk.)</subfield>
                <subfield code="u">electronic version</subfield>
                <subfield code="b">electronic version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630811051</subfield>
                <subfield code="u">electronic version (v.1)</subfield>
            </datafield>
            """, {
                'isbns': [{
                    'value': '9781630814434',
                    'medium': 'electronic version',
                }, {
                    'value': '9781630811051',
                    'medium': 'electronic version',
                }],
                'volume': '(v.1)',
            })

        check_transformation(
            """
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630814434</subfield>
                <subfield code="q">(electronic bk.)</subfield>
                <subfield code="u">description</subfield>
                <subfield code="b">electronic version</subfield>
            </datafield>
            <datafield tag="020" ind1=" " ind2=" ">
                <subfield code="a">9781630811051</subfield>
                <subfield code="u">electronic version (v.1)</subfield>
            </datafield>
            """, {
                'isbns': [{
                    'value': '9781630814434',
                    'description': 'description',
                }, {
                    'value': '9781630811051',
                    'medium': 'electronic version',
                }],
                'volume': '(v.1)',
            })

        with pytest.raises(ManualMigrationRequired):
            check_transformation(
                """
                <datafield tag="020" ind1=" " ind2=" ">
                    <subfield code="a">9781630814434</subfield>
                    <subfield code="q">(electronic bk.)</subfield>
                    <subfield code="u">electronic version (v.2)</subfield>
                    <subfield code="b">electronic version</subfield>
                </datafield>
                <datafield tag="020" ind1=" " ind2=" ">
                    <subfield code="a">9781630811051</subfield>
                    <subfield code="u">electronic version (v.1)</subfield>
                </datafield>
                """, {
                    'isbns': [{
                        'value': '9781630814434',
                        'medium': 'electronic version',
                    }, {
                        'value': '9781630811051',
                        'medium': 'electronic version',
                    }],
                    'volume': '(v.1)',
                })


def test_report_numbers(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1808.02335</subfield>
            </datafield>
            """, {
                'arxiv_eprints': [{
                    'value': 'arXiv:1808.02335',
                }],
            })
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="a">hep-th/9509119</subfield>
            </datafield>
            """, {
                'report_numbers': [{
                    'value': 'hep-th/9509119',
                }],
            })
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1808.02335</subfield>
                <subfield code="c">hep-ex</subfield>
            </datafield>
            """, {
                'arxiv_eprints': [{
                    'value': 'arXiv:1808.02335',
                    'categories': ['hep-ex'],
                }],
            })

        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="z">CERN-THESIS-2018-004</subfield>
            </datafield>
            """, {
                'report_numbers': [{
                    'value': 'CERN-THESIS-2018-004', 'hidden': True
                }],
            })

        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">CERN-ISOLDE-2018-001</subfield>
            </datafield>
            """, {
                'report_numbers': [{
                    'value': 'CERN-ISOLDE-2018-001', 'hidden': True
                }],
            })

        check_transformation(
            """
            <datafield tag="088" ind1=" " ind2=" ">
                <subfield code="a">NAPAC-2016-MOPOB23</subfield>
            </datafield>
            <datafield tag="088" ind1=" " ind2=" ">
                <subfield code="9">ATL-COM-PHYS-2018-980</subfield>
            </datafield>
            <datafield tag="088" ind1=" " ind2=" ">
                <subfield code="z">ATL-COM-PHYS-2017</subfield>
            </datafield>
            """, {
                'report_numbers': [
                    {'value': 'NAPAC-2016-MOPOB23'},
                    {'value': 'ATL-COM-PHYS-2018-980', 'hidden': True},
                    {'value': 'ATL-COM-PHYS-2017', 'hidden': True},
                ],
            })

        with pytest.raises(MissingRequiredField):
            check_transformation(
                """
                <datafield tag="037" ind1=" " ind2=" ">
                    <subfield code="x">hep-th/9509119</subfield>
                </datafield>
                """, {
                    'report_numbers': [{
                        'value': 'hep-th/9509119',
                    }],
                })


def test_dois(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">DOI</subfield>
                <subfield code="a">10.1007/978-1-4613-0247-6</subfield>
                <subfield code="q">data</subfield>
                <subfield code="9">source</subfield>
            </datafield>
            """, {
                'dois': [{
                    'source': 'source',
                    'material': 'data',
                    'value': '10.1007/978-1-4613-0247-6',
                }],
            })


def test_external_system_identifiers(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">EBL</subfield>
                <subfield code="a">5231528</subfield>
            </datafield>
            """, {
                'external_system_identifiers': [{
                    'schema': 'EBL',
                    'value': '5231528',
                }],
            })

        check_transformation(
            """
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">inspire-cnum</subfield>
                <subfield code="a">2365039</subfield>
            </datafield>
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">Random</subfield>
                <subfield code="a">2365039</subfield>
            </datafield>
            """, {
                'inspire_cnum': '2365039',
                'external_system_identifiers': [{
                    'schema': 'Random',
                    'value': '2365039',
                }],
            })

        check_transformation(
            """
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">Random</subfield>
                <subfield code="a">2365039</subfield>
            </datafield>
            """, {
                'external_system_identifiers': [{
                    'schema': 'Random',
                    'value': '2365039',
                }],
            })
        check_transformation(
            """
            <datafield tag="035" ind1=" " ind2=" ">
                <subfield code="9">CERCER</subfield>
                <subfield code="a">2365039</subfield>
            </datafield>
            """, {
            })

        check_transformation(
            """
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">ASIN</subfield>
                <subfield code="a">9402409580</subfield>
                <subfield code="9">DLC</subfield>
            </datafield>
            """, {
                'external_system_identifiers': [{
                    'value': '9402409580',
                    'schema': 'DLC'
                }],
            })
        check_transformation(
            """
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">DOI</subfield>
                <subfield code="a">10.1007/s00269-016-0862-1</subfield>
            </datafield>
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">DOI</subfield>
                <subfield code="a">10.1103/PhysRevLett.121.052004</subfield>
            </datafield>
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">DOI</subfield>
                <subfield code="9">arXiv</subfield>
                <subfield code="a">10.1103/PhysRevLett.121.052004</subfield>
                <subfield code="q">publication</subfield>
            </datafield>
            """, {
                'dois': [
                    {'value': '10.1007/s00269-016-0862-1'},
                    {'value': '10.1103/PhysRevLett.121.052004'},
                    {'value': '10.1103/PhysRevLett.121.052004',
                     'material': 'publication',
                     'source': 'arXiv',
                     }
                ],
            })
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="024" ind1="7" ind2=" ">
                    <subfield code="2">ASINss</subfield>
                    <subfield code="a">9402409580</subfield>
                    <subfield code="9">DLC</subfield>
                </datafield>
                """, {
                    'external_system_identifiers': [{
                        'value': '9402409580',
                        'schema': 'DLC'
                    }],
                })
        check_transformation(
            """
            <datafield tag="036" ind1=" " ind2=" ">
                <subfield code="9">DLC</subfield>
                <subfield code="a">92074207</subfield>
            </datafield>
            """, {
                'external_system_identifiers': [{
                    'schema': 'DLC',
                    'value': '92074207',
                }],
            })


def test_arxiv_eprints(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1209.5665</subfield>
                <subfield code="c">math-ph</subfield>
            </datafield>
            """, {
                'arxiv_eprints': [{
                    'categories': ['math-ph'],
                    'value': 'arXiv:1209.5665',
                }],
            })
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1209.5665</subfield>
                <subfield code="c">math-ph</subfield>
            </datafield>
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">arXiv:1209.5665</subfield>
                <subfield code="c">math.GT</subfield>
            </datafield>
            """, {
                'arxiv_eprints': [{
                    'categories': ['math-ph', 'math.GT'],
                    'value': 'arXiv:1209.5665',
                }],
            })
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="037" ind1=" " ind2=" ">
                    <subfield code="9">arXiv</subfield>
                    <subfield code="a">arXiv:1209.5665</subfield>
                    <subfield code="c">math-phss</subfield>
                </datafield>
                """, {
                    'arxiv_eprints': [{
                        'categories': ['math-ph'],
                        'value': 'arXiv:1209.5665',
                    }],
                })


def test_languages(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">eng</subfield>
            </datafield>
            """, {
                'languages': ['en'],
            })
        # with pytest.raises(UnexpectedValue):
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">english</subfield>
            </datafield>
            """, {
                'languages': ['en'],
            })
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">fre</subfield>
            </datafield>
            """, {
                'languages': ['fr'],
            })
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">pl</subfield>
            </datafield>
            """, {
                'languages': ['pl'],
            })
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">ger</subfield>
            </datafield>
            """, {
                'languages': ['de'],
            })
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="041" ind1=" " ind2=" ">
                    <subfield code="a">xxxxxxxx</subfield>
                </datafield>
                """, {
                    'languages': ['de'],
                })


def test_editions(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="250" ind1=" " ind2=" ">
                <subfield code="a">3rd ed.</subfield>
            </datafield>
            """, {
                'editions': [
                    '3rd ed.'
                ],
            })


def test_imprints(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="260" ind1=" " ind2=" ">
                <subfield code="a">Sydney</subfield>
                <subfield code="b">Allen &amp; Unwin</subfield>
                <subfield code="c">2013</subfield>
                <subfield code="g">2015</subfield>
            </datafield>
            """, {
                'imprints': [{
                    'place': 'Sydney',
                    'publisher': 'Allen & Unwin',
                    'date': '2013',
                    'reprint': '2015',
                }],
            })


def test_preprint_date(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="269" ind1=" " ind2=" ">
                <subfield code="a">Geneva</subfield>
                <subfield code="b">CERN</subfield>
                <subfield code="c">19 Jan 2016</subfield>
            </datafield>
            """, {
                'preprint_date': '2016-01-19',
            })
        check_transformation(
            """
            <datafield tag="269" ind1=" " ind2=" ">
                <subfield code="a">Geneva</subfield>
                <subfield code="b">CERN</subfield>
            </datafield>
            """, {

            })
        with pytest.raises(ManualMigrationRequired):
            check_transformation(
                """
                <datafield tag="269" ind1=" " ind2=" ">
                    <subfield code="a">Geneva</subfield>
                    <subfield code="b">CERN</subfield>
                    <subfield code="c">33 Jan 2016</subfield>
                </datafield>
                """, {
                    'preprint_date': '2016-01-19',
                })


def test_number_of_pages(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">373 p</subfield>
            </datafield>
            """, {
                'number_of_pages': 373,
            })
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a">480 p. ; 1 CD-ROM suppl</subfield>
            </datafield>
            """, {
                'number_of_pages': 480,
            })
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="a"></subfield>
            </datafield>
            """, {

            })
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="300" ind1=" " ind2=" ">
                    <subfield code="a">p</subfield>
                </datafield>
                """, {

                })

# for book series model
# def test_book_series(app):
#     with app.app_context():
#         check_transformation(
#             """
#             <datafield tag="490" ind1=" " ind2=" ">
#                 <subfield code="a">CISM International Centre</subfield>
#                 <subfield code="v">490</subfield>
#                 <subfield code="x">0317-8471</subfield>
#             </datafield>
#             """, {
#                 'book_series': {
#                     'title': 'CISM International Centre',
#                     'volume': '490',
#                     'issn': '0317-8471',
#                 },
#             })


def test_abstracts(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="520" ind1=" " ind2=" ">
                <subfield code="a">The publication...</subfield>
            </datafield>
            <datafield tag="520" ind1=" " ind2=" ">
                <subfield code="a">Does application...</subfield>
            </datafield>
            """, {
                'abstracts': [
                    'The publication...',
                    'Does application...',
                ],
            })


def test_funding_info(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="536" ind1=" " ind2=" ">
                <subfield code="a">CERN Technical Student Program</subfield>
            </datafield>
            <datafield tag="536" ind1=" " ind2=" ">
                <subfield code="a">FP7</subfield>
                <subfield code="c">654168</subfield>
                <subfield code="f">AIDA-2020</subfield>
                <subfield code="r">openAccess</subfield>
            </datafield>
            """, {
                'funding_info': [
                    {
                        'agency': 'CERN Technical Student Program',
                    },
                    {
                        'agency': 'FP7',
                        'grant_number': '654168',
                        'project_number': 'AIDA-2020',
                        'openaccess': True,
                    },
                ]
            })
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="536" ind1=" " ind2=" ">
                    <subfield code="a">CERN Technical Student Program</subfield>
                </datafield>
                <datafield tag="536" ind1=" " ind2=" ">
                    <subfield code="a">FP7</subfield>
                    <subfield code="c">654168</subfield>
                    <subfield code="f">AIDA-2020</subfield>
                    <subfield code="r">openAccedafss</subfield>
                </datafield>
                """, {
                    'funding_info': [
                        {
                            'agency': 'CERN Technical Student Program',
                        },
                        {
                            'agency': 'FP7',
                            'grant_number': '654168',
                            'project_number': 'AIDA-2020',
                            'openaccess': True,
                        },
                    ]
                })


def test_license(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="540" ind1=" " ind2=" ">
                <subfield code="b">arXiv</subfield>
            <subfield code="u">
                http://arxiv.org/licenses/nonexclusive-distrib/1.0/
            </subfield>
            </datafield>
            <datafield tag="540" ind1=" " ind2=" ">
                <subfield code="3">Preprint</subfield>
                <subfield code="a">CC-BY-4.0</subfield>
            </datafield>
            <datafield tag="540" ind1=" " ind2=" ">
                <subfield code="3">Publication</subfield>
                <subfield code="a">CC-BY-4.0</subfield>
                <subfield code="f">SCOAP3</subfield>
                <subfield code="g">DAI/7161287</subfield>
            </datafield>
            """, {
                'licenses': [
                    {
                        'imposing': 'arXiv',
                        'url': 'http://arxiv.org/licenses/nonexclusive-distrib/1.0/',
                    },
                    {
                        'license': 'CC-BY-4.0',
                        'material': 'preprint',
                    },
                    {
                        'license': 'CC-BY-4.0',
                        'material': 'publication',
                        'funder': 'SCOAP3',
                        'admin_info': 'DAI/7161287',
                    }
                ]
            })


def test_copyright(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="542" ind1=" " ind2=" ">
                <subfield code="d">d</subfield>
                <subfield code="f">f</subfield>
                <subfield code="g">2013</subfield>
                <subfield code="u">u</subfield>
            </datafield>
            <datafield tag="542" ind1=" " ind2=" ">
                <subfield code="3">Preprint</subfield>
                <subfield code="d">CERN</subfield>
                <subfield code="g">2018</subfield>
            </datafield>
            <datafield tag="542" ind1=" " ind2=" ">
                <subfield code="f">This work is licensed.</subfield>
                <subfield code="u">http://creativecommons.org/licenses/by/4.0</subfield>
            </datafield>
            """, {
                'copyrights': [
                    {
                        'holder': 'd',
                        'statement': 'f',
                        'year': 2013,
                        'url': 'u',
                    },
                    {
                        'material': 'preprint',
                        'holder': 'CERN',
                        'year': 2018
                    },
                    {
                        'statement': 'This work is licensed.',
                        'url': 'http://creativecommons.org/licenses/by/4.0',
                    }
                ]
            })


def test_conference_info(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="111" ind1=" " ind2=" ">
                <subfield code="9">20040621</subfield>
                <subfield code="a">2nd Workshop on Science with
                 the New Generation of High Energy Gamma-ray Experiments:
                 between Astrophysics and Astroparticle Physics
                </subfield>
                <subfield code="c">Bari, Italy</subfield>
                <subfield code="d">21 Jun 2004</subfield>
                <subfield code="f">2004</subfield>
                <subfield code="g">bari20040621</subfield>
                <subfield code="n">2</subfield>
                <subfield code="w">IT</subfield>
                <subfield code="z">20040621</subfield>
            </datafield>
            <datafield tag="270" ind1=" " ind2=" ">
                <subfield code="m">arantza.de.oyanguren.campos@cern.ch
                </subfield>
            </datafield>
            """,
            {'conference_info': [
                {'title': """2nd Workshop on Science with
                 the New Generation of High Energy Gamma-ray Experiments:
                 between Astrophysics and Astroparticle Physics""",
                 'place': 'Bari, Italy',
                 'cern_conference_code': 'bari20040621',
                 'opening_date': '2004-06-21',
                 'series_number': 2,
                 'country_code': 'IT',
                 'closing_date': '2004-06-21',
                 'contact':
                    'arantza.de.oyanguren.campos@cern.ch'
                 }
            ]}
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="111" ind1=" " ind2=" ">
                    <subfield code="9">20040621</subfield>
                    <subfield code="a">2nd Workshop on Science with
                     the New Generation of High Energy Gamma-ray Experiments:
                     between Astrophysics and Astroparticle Physics
                    </subfield>
                    <subfield code="c">Bari, Italy</subfield>
                    <subfield code="d">21 Jun 2004</subfield>
                    <subfield code="f">2004</subfield>
                    <subfield code="g">bari20040621</subfield>
                    <subfield code="n">2</subfield>
                    <subfield code="w">ITALIA</subfield>
                    <subfield code="z">20040621</subfield>
                </datafield>
                <datafield tag="270" ind1=" " ind2=" ">
                    <subfield code="m">arantza.de.oyanguren.campos@cern.ch
                    </subfield>
                </datafield>
                """,
                {'conference_info': [
                    {'title': """2nd Workshop on Science with
                             the New Generation of High Energy Gamma-ray Experiments:
                             between Astrophysics and Astroparticle Physics""",
                     'place': 'Bari, Italy',
                     'cern_conference_code': 'bari20040621',
                     'opening_date': '2004-06-21',
                     'series_number': 2,
                     'country_code': 'IT',
                     'closing_date': '2004-06-21',
                     'contact':
                         'arantza.de.oyanguren.campos@cern.ch'
                     }
                ]}
            )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="111" ind1=" " ind2=" ">
                    <subfield code="9">2gtrw</subfield>
                    <subfield code="a">2nd Workshop on Science with
                     the New Generation of High Energy Gamma-ray Experiments:
                     between Astrophysics and Astroparticle Physics
                    </subfield>
                    <subfield code="c">Bari, Italy</subfield>
                    <subfield code="d">gbrekgk</subfield>
                    <subfield code="f">2004</subfield>
                    <subfield code="g">bari20040621</subfield>
                    <subfield code="n">2</subfield>
                    <subfield code="w">IT</subfield>
                    <subfield code="z">2treht</subfield>
                </datafield>
                <datafield tag="270" ind1=" " ind2=" ">
                    <subfield code="m">arantza.de.oyanguren.campos@cern.ch
                    </subfield>
                </datafield>
                """,
                {'conference_info': [
                    {'title': """2nd Workshop on Science with
                             the New Generation of High Energy Gamma-ray Experiments:
                             between Astrophysics and Astroparticle Physics""",
                     'place': 'Bari, Italy',
                     'cern_conference_code': 'bari20040621',
                     'opening_date': '2004-06-21',
                     'series_number': 2,
                     'country_code': 'IT',
                     'closing_date': '2004-06-21',
                     'contact':
                         'arantza.de.oyanguren.campos@cern.ch'
                     }
                ]}
            )
        with pytest.raises(MissingRequiredField):
            check_transformation(
                """
                <datafield tag="270" ind1=" " ind2=" ">
                    <subfield code="m">arantza.de.oyanguren.campos@cern.ch
                    </subfield>
                </datafield>
                """, {
                    'conference_info':
                        {'contact':
                            'arantza.de.oyanguren.campos@cern.ch'}}
            )


def test_title_translations(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="242" ind1=" " ind2=" ">
                <subfield code="9">submitter</subfield>
                <subfield code="a">Study of the impact of stacking on simple
                      hard diffraction events in CMS/LHC</subfield>
                <subfield code="b">Subtitle/LHC</subfield>
            </datafield>
            """,
            {'title_translations': [
                {'title': """Study of the impact of stacking on simple
                      hard diffraction events in CMS/LHC""",
                 'subtitle': 'Subtitle/LHC',
                 'language': 'en',
                 }]
             }
        )


def test_titles(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Incoterms 2010</subfield>
                <subfield code="b">les règles de l'ICC pour l'utilisation
                 des termes de commerce nationaux et internationaux
                </subfield>
            </datafield>
            <datafield tag="245" ind1=" " ind2=" ">
                <subfield code="a">Titre test</subfield>
            </datafield>
            """,
            {'titles': [
                {'title': 'Incoterms 2010',
                 'subtitle': u"""les règles de l'ICC pour l'utilisation
                 des termes de commerce nationaux et internationaux""",
                 },
                {'title': 'Titre test'}
            ]}
        )


def test_public_notes(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="500" ind1=" " ind2=" ">
            <subfield code="a">
            Translated from the 2nd American edition : Fluid mechanics :
            fundamentals and applications, 2nd ed., 2010
            </subfield>
            </datafield>
            <datafield tag="500" ind1=" " ind2=" ">
            <subfield code="a">No CD-ROM</subfield>
            </datafield>
            """,
            {'public_notes': [{
                'value': """Translated from the 2nd American edition : Fluid mechanics :
            fundamentals and applications, 2nd ed., 2010"""},
                {'value': 'No CD-ROM'},
            ]}
        )
        check_transformation(
            """
            <datafield tag="500" ind1=" " ind2=" ">
                <subfield code="9">arXiv</subfield>
                <subfield code="a">
                    Comments: Book, 380 p., 88 figs., 7 tables; 1st volume of three-volume book "Dark energy and dark matter in the Universe", ed. V. Shulga, Kyiv, Academperiodyka, 2013; ISBN 978-966-360-239-4, ISBN 978-966-360-240-0 (vol. 1). arXiv admin note: text overlap with arXiv:0706.0033, arXiv:1104.3029 by other authors
                </subfield>
            </datafield>
            """, {
                'public_notes': [
                    {'value': """Comments: Book, 380 p., 88 figs., 7 tables; 1st volume of three-volume book "Dark energy and dark matter in the Universe", ed. V. Shulga, Kyiv, Academperiodyka, 2013; ISBN 978-966-360-239-4, ISBN 978-966-360-240-0 (vol. 1). arXiv admin note: text overlap with arXiv:0706.0033, arXiv:1104.3029 by other authors""",
                     'source': 'arXiv',
                     },
                ]
            }
        )


def test_table_of_contents(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="505" ind1="0" ind2=" ">
                <subfield code="a">
                2nd Advanced School on Exoplanetary Science: Astrophysics of Exoplanetary Atmospheres -- Chapter 1: Modeling Exoplanetary Atmospheres, by Jonathan J. Fortney -- Chapter 2: Observational Techniques, by David Sing -- Chapter 3: Molecular spectroscopy for Exoplanets by Jonathan Tennyson -- Chapter 4: Solar system atmospheres by Davide Grassi.
                </subfield>
            </datafield>
            """,
            {'table_of_content': [
                '2nd Advanced School on Exoplanetary Science: Astrophysics of Exoplanetary Atmospheres',
                'Chapter 1: Modeling Exoplanetary Atmospheres, by Jonathan J. Fortney',
                'Chapter 2: Observational Techniques, by David Sing',
                'Chapter 3: Molecular spectroscopy for Exoplanets by Jonathan Tennyson',
                'Chapter 4: Solar system atmospheres by Davide Grassi.'
            ]}
        )
        with pytest.raises(UnexpectedValue):
            check_transformation(
                """
                <datafield tag="505" ind1="0" ind2=" ">
                    <subfield code="a">
                    </subfield>
                </datafield>
                """,
                {'table_of_content': [

                ]}
            )


def test_standard_numbers(app):
    """Tests standard number field translation."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="021" ind1=" " ind2=" ">
                <subfield code="a">FD-X-60-000</subfield>
            </datafield>
            <datafield tag="021" ind1=" " ind2=" ">
                <subfield code="a">NF-EN-13306</subfield>
            </datafield>
            <datafield tag="021" ind1=" " ind2=" ">
                <subfield code="b">BS-EN-ISO-6507-2</subfield>
            </datafield>
            """,
            {'standard_numbers': [
                {'value': 'FD-X-60-000', 'hidden': False},
                {'value': 'NF-EN-13306', 'hidden': False},
                {'value': 'BS-EN-ISO-6507-2', 'hidden': True},
            ]}
        )
        with pytest.raises(MissingRequiredField):
            check_transformation(
                """
                <datafield tag="021" ind1=" " ind2=" ">
                    <subfield code="c">FD-X-60-000</subfield>
                </datafield>
                """,
                {'standard_numbers': [
                    {'value': 'FD-X-60-000', 'hidden': False},
                    {'value': 'NF-EN-13306', 'hidden': False},
                    {'value': 'BS-EN-ISO-6507-2', 'hidden': True},
                ]}
            )


def test_book_series(app):
    """Tests book seris field translation."""
    with app.app_context():
        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">Minutes</subfield>
            </datafield>
            """, {
                'book_series':
                [
                    {'title': 'Minutes'},
                ]
            }
        )
        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">De Gruyter studies in mathematical physics</subfield>
                <subfield code="v">16</subfield>
            </datafield>
            """, {
                'book_series':
                [
                    {'title': 'De Gruyter studies in mathematical physics',
                     'volume': '16',
                     },
                ]
            }
        )
        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">Springer tracts in modern physics</subfield>
                <subfield code="v">267</subfield>
                <subfield code="x">0081-3869</subfield>
            </datafield>
            """, {
                'book_series':
                [
                    {'title': 'Springer tracts in modern physics',
                     'volume': '267',
                     'issn': '0081-3869',
                     },
                ]
            }
        )
