About
=====


This Sphinx extension (named "sphinx-filltableref", parsed as "fill table ref") creates tables
that contain data values that are from publications and includes links after the values to other
pages which have tables that again show the values along with a citation to the source publications.
This enables creating “summary” tables of data that link to other pages which contain “source” tables
that specify where the data is from (the reference) and can also describe the data values in more detail.

The extension defines two Sphinx directives:  The “tblrender” directive is used to specify what the
summary table looks like (row and column labels and titles).  It results in the generation of the
summary table with filled-in data values and links to the other pages that specify the data source.
The “tbldata” directive is used to specify the source of the data values (which are used to fill in
the summary table) along with the citation.  Each tbldata directive results in the generation of a
table that shows the values and citations (to publications) specified by that directive.

To generate the citations and references, this extension requires extensions:
`sphinxcontrib-bibtex <http://sphinxcontrib-bibtex.readthedocs.org/en/latest/>`_ 
and `sphinxcontrib-bibtex2 <https://github.com/mcmtroffaes/sphinxcontrib-bibtex/tree/develop/sphinxcontrib/bibtex2>`_.
In order to get both of those extensions installed automatically, and to allow links to PDF of papers and notes
for each reference, this extension is setup to require extension
`sphinxcontrib-bibtexpdflink <http://sphinxcontrib-bibtexpdflink.readthedocs.org/en/latest/>`_.
The installation of that extension (sphinxcontrib-bibtexpdflink) results in the sphinxcontrib-bibtex and
sphinxcontrib-bibtex2 extensions both being installed since they are required by sphinxcontrib-bibtexpdflink.

