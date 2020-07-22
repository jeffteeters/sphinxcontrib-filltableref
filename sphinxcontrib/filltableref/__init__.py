"""
    sphinxcontrib.filltableref
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Fill tables with values that are linked to references.

    :copyright: Copyright 2020 by Jeff Teeters <jeff@teeters.us>
    :license: BSD, see LICENSE for details.
"""

import pbr.version

if False:
    # For type annotations
    from typing import Any, Dict  # noqa
    from sphinx.application import Sphinx  # noqa

__version__ = pbr.version.VersionInfo(
    'filltableref').version_string()


def setup(app):
    # type: (Sphinx) -> Dict[unicode, Any]
    return {'version': __version__, 'parallel_read_safe': True}
