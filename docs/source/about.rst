.. _about:

About
=====

This Sphinx extension (named "sphinx-filltableref", parsed as "fill table ref") 
enables creating “summary” tables of data that link to other pages which contain “source” tables
that specify where the data is from (the reference) and can also describe the data values in more detail.

The extension defines two Sphinx directives:  The :ref:`tblrender` directive is used to specify what the
summary table looks like (row and column labels and titles), but not the referenced data values.
The :ref:`tbldata` directive is used to specify the data values 
along with the source (reference).  When a document is processed, information
specified in both types of directives are combined: data values from the *tbldata* directives are
used to fill in the summary table specified in the *tblrender* directive.  The
values filled-in link to the "source" tables specified by the *tbldata* directive
that display the citation for the values.
 

This extension requires extension:
`sphinxcontrib-bibtexpdflink <http://sphinxcontrib-bibtexpdflink.readthedocs.org/en/latest/>`_.
The reason for this requrement, is that in order to generate the citations and references, this
extension requires extensions: 
`sphinxcontrib-bibtex <http://sphinxcontrib-bibtex.readthedocs.org/en/latest/>`_ 
and `sphinxcontrib-bibtex2 <https://github.com/mcmtroffaes/sphinxcontrib-bibtex/tree/develop/sphinxcontrib/bibtex2>`_,
and both of those are installed automatically by sphinxcontrib-bibtexpdflink.  Also sphinxcontrib-bibtexpdflink
allows having a link to a PDF file and notes for each reference, which can be quite useful.

