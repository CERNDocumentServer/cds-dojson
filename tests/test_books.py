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
import pytest

from cds_dojson.marc21.fields.books.errors import UnexpectedValue, \
    ManualMigrationRequired
from cds_dojson.marc21.models.books.book import model
from cds_dojson.marc21.utils import create_record

marcxml = ("""<collection xmlns="http://www.loc.gov/MARC21/slim">"""
           """<record>{0}</record></collection>""")


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
            <datafield tag="720" ind1=" " ind2=" ">
                <subfield code="a">Neubert, Matthias</subfield>
            </datafield>
            """, {
                'authors': [{'full_name': 'Frampton, Paul H',
                             'role': 'editor',
                             'alternative_names': 'Neubert, Matthias'},
                            {'full_name': 'Glashow, Sheldon Lee',
                             'role': 'editor'},
                            {'full_name': 'Van Dam, Hendrik',
                             'role': 'editor'},
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
                'corporate_author': {
                    'corporate_author': ['Marston, R M'],
                },
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


def test_report_numbers(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="037" ind1=" " ind2=" ">
                <subfield code="9">9</subfield>
                <subfield code="a">a</subfield>
            </datafield>
            """, {
                'report_numbers': [{
                    'value': 'a',
                }],
            })

        check_transformation(
            """
            <datafield tag="088" ind1=" " ind2=" ">
              <subfield code="a">13.140</subfield>
            </datafield>
            <datafield tag="088" ind1=" " ind2=" ">
                <subfield code="9">ATL-COM-SOFT-2018-088</subfield>
            </datafield>
            """, {
                'report_numbers': [{

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

        # check_transformation(
        #     """
        #     <datafield tag="035" ind1=" " ind2=" ">
        #         <subfield code="9">CERCER</subfield>
        #         <subfield code="a">2365039</subfield>
        #     </datafield>
        #     """, {
        #         'external_system_identifiers': [{
        #             'schema': 'EBL',
        #             'value': '5231528',
        #         }],
        #     })

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

        check_transformation(
            """
            <datafield tag="024" ind1="7" ind2=" ">
                <subfield code="2">ASIN</subfield>
                <subfield code="a">9402409580</subfield>
            </datafield>
            """, {
                'external_system_identifiers': [{
                    'value': '9402409580',
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


def test_languages(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="041" ind1=" " ind2=" ">
                <subfield code="a">eng</subfield>
            </datafield>
            """, {
                'languages': [{
                    'languages': ['eng'],
                }],
            })


# def test_subject_classification(app):
#     with app.app_context():
#         check_transformation(
#             """
#             <datafield tag="050" ind1=" " ind2="4">
#                 <subfield code="a">QA171 .H355 2018</subfield>
#             </datafield>
#             <datafield tag="080" ind1=" " ind2=" ">
#                 <subfield code="a">512.77</subfield>
#             </datafield>
#             <datafield tag="080" ind1=" " ind2=" ">
#                 <subfield code="a">512.64</subfield>
#             </datafield>
#             <datafield tag="082" ind1=" " ind2=" ">
#                 <subfield code="a">512/.2</subfield>
#             </datafield>
#             """, {
#                 'subject_classification': {

#                 },
#             })


# def test_conference_info(app):
#     with app.app_context():
#         check_transformation(
#             """

#             """, {
#                 'conference_info': {

#                 },
#             })


# def test_title_translations(app):
#     with app.app_context():
#         check_transformation(
#             """
#             <datafield tag="242" ind1=" " ind2=" ">
#                 <subfield code="a">la</subfield>
#                 <subfield code="a">so</subfield>
#                 <subfield code="a">su</subfield>
#                 <subfield code="a">ti</subfield>
#             </datafield>
#             """, {
#                 'title_translations': [{
#                     'language': 'la',
#                     'source': 'so',
#                     'subtitle': 'su',
#                     'title': 'ti',
#                 }],
#             })


def test_editions(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="250" ind1=" " ind2=" ">
                <subfield code="a">3rd ed.</subfield>
            </datafield>
            """, {
                'editions': [{
                    'editions': ['3rd ed.'],
                }],
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
                'preprint_date': {
                    'preprint_date': '19 Jan 2016',
                },
            })


def test_number_of_pages(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="300" ind1=" " ind2=" ">
                <subfield code="b">373 p</subfield>
            </datafield>
            """, {
                'number_of_pages': {
                    'number_of_pages': 373,
                },
            })


def test_book_series(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="490" ind1=" " ind2=" ">
                <subfield code="a">CISM International Centre</subfield>
                <subfield code="v">490</subfield>
                <subfield code="x">0317-8471</subfield>
            </datafield>
            """, {
                'book_series': {
                    'title': 'CISM International Centre',
                    'volume': '490',
                    'issn': '0317-8471',
                },
            })


# def test_thesis_info(app):
#     with app.app_context():
#         check_transformation(
#             """
#             <datafield tag="502" ind1=" " ind2=" ">
#                 <subfield code="a">PhD</subfield>
#                 <subfield code="b">Uppsala U.</subfield>
#                 <subfield code="c">1972</subfield>
#             </datafield>
#             """, {
#                 'thesis_info': {
#                     'date': 'd',
#                     'defense_date': 'a',
#                     'degree_type': 'b',
#                     'institutions': [{
#                         'name': '',
#                         'record': 'elements/json_reference.json',  # FIXME
#                         'curated_relation': True,
#                     }],
#                 },
#             })


# def test_table_of_content(app):
#     with app.app_context():
#         check_transformation(
#             """
#             <datafield tag="505" ind1="0" ind2=" ">
#                 <subfield code="a">I Quantitative...</subfield>
#             </datafield>
#             <datafield tag="505" ind1="0" ind2=" ">
#                 <subfield code="a">I Modelling of Transport...</subfield>
#             </datafield>
#             """, {
#                 'table_of_content': [

#                 ]
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
                <subfield code="z">a</subfield>
                <subfield code="c">c</subfield>
                <subfield code="f">f</subfield>
            </datafield>
            """, {
                'funding_info': [{
                    'agency': 'a',
                    'grant_number': 'c',
                    'project_number': 'f',
                }]
            })


def test_license(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="540" ind1=" " ind2=" ">
                <subfield code="3">3</subfield>
                <subfield code="a">a</subfield>
                <subfield code="b">b</subfield>
                <subfield code="u">u</subfield>
            </datafield>

            """, {
                'license': [{
                    'material': '3',
                    'license': 'a',
                    'imposing': 'b',
                    'url': 'u',
                }]
            })


def test_copyright(app):
    with app.app_context():
        check_transformation(
            """
            <datafield tag="542" ind1=" " ind2=" ">
                <subfield code="3">3</subfield>
                <subfield code="d">d</subfield>
                <subfield code="f">f</subfield>
                <subfield code="g">g</subfield>
                <subfield code="u">u</subfield>
            </datafield>
            """, {
                'copyright': [{
                    'material': '3',
                    'holder': 'd',
                    'statement': 'f',
                    'year': 'g',
                    'url': 'u',
                }]
            })


# <datafield tag="595" ind1=" " ind2=" ">
# <subfield code="a">Engineering</subfield>
# </datafield>
# <datafield tag="595" ind1=" " ind2=" ">
# <subfield code="a">SPR201504</subfield>
# </datafield>
