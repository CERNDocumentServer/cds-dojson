# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# CDS-Doson is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-Dojson exceptions module."""


class ModelMissingException(Exception):
    """CDSDoJSONException class."""

    description = "[Record did not match any available model]"


class MultipleModelsException(Exception):
    """CDSDoJSONException class."""

