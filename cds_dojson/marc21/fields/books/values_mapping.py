# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017, 2018 CERN.
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
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Book values mapping."""
from cds_dojson.marc21.fields.books.errors import UnexpectedValue

DOCUMENT_TYPE = {
    'PROCEEDINGS': ['PROCEEDINGS', '42', '43'],
    'BOOK': ['BOOK', '21'],
    'REPORT': ['REPORT']
}

AUTHOR_ROLE = {
    'editor': ['ED.', 'ED'],
    'supervisor': ['DIR.', 'DIR'],
    'ilustrator': ['ILL.', 'ILL'],
}

COLLECTION = {
    'BOOK SUGGESTION': ['BOOKSUGGESTION'],
    'LEGSERLIB': ['LEGSERLIB'],
    'YELLOW REPORT': ['YELLOW REPORT', 'YELLOWREPORT'],
    'CERN': ['CERN'],
    'DESIGN REPORT': ['DESIGN REPORT', 'DESIGNREPORT'],
    'BOOKSHOP': ['BOOKSHOP'],
    'LEGSERLIBINTLAW': ['LEGSERLIBINTLAW'],
    'LEGSERLIBCIVLAW': ['LEGSERLIBCIVLAW'],
    'LEGSERLIBLEGRES': ['LEGSERLIBLEGRES']
}

ACQUISITION_METHOD = {
    'submitter': ['h'],
    'batchuploader': ['n', 'm'],
}

MEDIUM_TYPES = [
    'ELECTRONIC VERSION',
    'PRINT VERSION',
    'PRINT VERSION, HARDBACK',
    'PRINT VERSION, PAPERBACK',
    'PRINT VERSION, SPIRAL-BOUND',
    'CD-ROM',
    'AUDIOBOOK',
    'DVD',
]

ARXIV_CATEGORIES = ['astro-ph', 'astro-ph.CO', 'astro-ph.EP', 'astro-ph.GA',
                    'astro-ph.HE', 'astro-ph.IM', 'astro-ph.SR', 'cond-mat',
                    'cond-mat.dis-nn', 'cond-mat.mes-hall',
                    'cond-mat.mtrl-sci', 'cond-mat.other',
                    'cond-mat.quant-gas', 'cond-mat.soft',
                    'cond-mat.stat-mech', 'cond-mat.str-el',
                    'cond-mat.supr-con', 'cs', 'cs.AI', 'cs.AR', 'cs.CC',
                    'cs.CE', 'cs.CG', 'cs.CL', 'cs.CR', 'cs.CV', 'cs.CY',
                    'cs.DB', 'cs.DC', 'cs.DL', 'cs.DM', 'cs.DS', 'cs.ET',
                    'cs.FL', 'cs.GL', 'cs.GR', 'cs.GT', 'cs.HC', 'cs.IR',
                    'cs.IT', 'cs.LG', 'cs.LO', 'cs.MA', 'cs.MM', 'cs.MS',
                    'cs.NA', 'cs.NE', 'cs.NI', 'cs.OH', 'cs.OS', 'cs.PF',
                    'cs.PL', 'cs.RO', 'cs.SC', 'cs.SD', 'cs.SE', 'cs.SI',
                    'cs.SY', 'econ', 'econ.EM', 'eess', 'eess.AS', 'eess.IV',
                    'eess.SP', 'gr-qc', 'hep-ex', 'hep-lat', 'hep-ph',
                    'hep-th', 'math', 'math-ph', 'math.AC', 'math.AG',
                    'math.AP', 'math.AT', 'math.CA', 'math.CO', 'math.CT',
                    'math.CV', 'math.DG', 'math.DS', 'math.FA', 'math.GM',
                    'math.GN', 'math.GR', 'math.GT', 'math.HO', 'math.IT',
                    'math.KT', 'math.LO', 'math.MG', 'math.MP', 'math.NA',
                    'math.NT', 'math.OA', 'math.OC', 'math.PR', 'math.QA',
                    'math.RA', 'math.RT', 'math.SG', 'math.SP', 'math.ST',
                    'nlin', 'nlin.AO', 'nlin.CD', 'nlin.CG', 'nlin.PS',
                    'nlin.SI', 'nucl-ex', 'nucl-th', 'physics',
                    'physics.acc-ph', 'physics.ao-ph', 'physics.app-ph',
                    'physics.atm-clus', 'physics.atom-ph', 'physics.bio-ph',
                    'physics.chem-ph', 'physics.class-ph', 'physics.comp-ph',
                    'physics.data-an', 'physics.ed-ph', 'physics.flu-dyn',
                    'physics.gen-ph', 'physics.geo-ph', 'physics.hist-ph',
                    'physics.ins-det', 'physics.med-ph', 'physics.optics',
                    'physics.plasm-ph', 'physics.pop-ph', 'physics.soc-ph',
                    'physics.space-ph', 'q-bio', 'q-bio.BM', 'q-bio.CB',
                    'q-bio.GN', 'q-bio.MN', 'q-bio.NC', 'q-bio.OT', 'q-bio.PE',
                    'q-bio.QM', 'q-bio.SC', 'q-bio.TO', 'q-fin', 'q-fin.CP',
                    'q-fin.EC', 'q-fin.GN', 'q-fin.MF', 'q-fin.PM', 'q-fin.PR',
                    'q-fin.RM', 'q-fin.ST', 'q-fin.TR', 'quant-ph', 'stat',
                    'stat.AP', 'stat.CO', 'stat.ME', 'stat.ML', 'stat.OT',
                    'stat.TH']

MATERIALS = [
    'addendum',
    'additional material',
    'data',
    'erratum',
    'editorial note',
    'preprint',
    'publication',
    'reprint',
    'software',
    'translation',
]


SUBJECT_CLASSIFICATION_EXCEPTIONS = \
    ['PACS', 'CERN LIBRARY', 'CERN YELLOW REPORT']


def mapping(field_map, val, raise_exception=False):
    """
    Maps the old value to a new one according to the map.

    important: the maps values must be uppercase, in order to catch all the
    possible values in the field
    :param field_map: one of the maps specified
    :param val: old value
    :param raise_exception if mapping should raise exception when value does
           not match
    :raises UnexpectedValue
    :return: output value matched in map
    """
    if isinstance(val, str):
        val = val.strip()
    if val:
        if isinstance(field_map, dict):
            for k, v in field_map.items():
                if val.upper() in v:
                    return k
        elif isinstance(field_map, list):
            if val in field_map:
                return val
        if raise_exception:
            raise UnexpectedValue
