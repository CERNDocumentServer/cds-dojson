# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
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
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.

from cds_dojson.marc21.models import album, default, image, video
from cds_dojson.matcher import matcher


def test_marc21_matcher():
    """Test CDS DoJSON matcher."""
    album_blob = {'999__': {'a': 'ALBUM'}}
    cern_blob = {'690C_': {'a': 'CERN'}}
    duplicated_blob = {'999__': [{'a': 'IMAGE'}, {'a': 'ALBUM'}]}
    image_blob = {'999__': {'a': 'IMAGE'}}
    no_match_blob = {'000__': {'z': 'odd'}}
    video_blob = {'980__': {'a': 'PUBLVIDEOMOVIE'}}

    assert album.model == matcher(album_blob, 'cds_dojson.marc21.models')
    assert default.model == matcher(cern_blob, 'cds_dojson.marc21.models')
    assert default.model == matcher(
        duplicated_blob, 'cds_dojson.marc21.models')
    assert default.model == matcher(no_match_blob, 'cds_dojson.marc21.models')
    assert image.model == matcher(image_blob, 'cds_dojson.marc21.models')
    assert video.model == matcher(video_blob, 'cds_dojson.marc21.models')
