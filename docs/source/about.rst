.. _about:

About
=====

This Sphinx extension (named "sphinx-filltableref", parsed as "fill table ref") 
enables creating “summary” tables of data that link to other pages which contain “source” tables
that specify where the data is from (the reference) and can also describe the data values in more detail.

The extension defines two Sphinx directives:  The “tblrender” directive is used to specify what the
summary table looks like (row and column labels and titles), but not the referenced data values.
The “tbldata” directive is used to specify the data values 
along with the source (reference).  When a document is processed, information
specified in both types of directives are combined: data values from the tbldata directives are
used to fill in the summary table specified in the “tblrender” directive.  The
values filled-in link to the "source" tables specified by the tbldata directive
that display the citation for the values.
 

This extension requires extension:
`sphinxcontrib-bibtexpdflink <http://sphinxcontrib-bibtexpdflink.readthedocs.org/en/latest/>`_.
The reason for this requrement, is that in order to generate the citations and references, this
extension requires extensions: 
`sphinxcontrib-bibtex <http://sphinxcontrib-bibtex.readthedocs.org/en/latest/>`_ 
and `sphinxcontrib-bibtex2 <https://github.com/mcmtroffaes/sphinxcontrib-bibtex/tree/develop/sphinxcontrib/bibtex2>`_,
and both of those are installed automatically by sphinxcontrib-bibtexpdflink.  Also sphinxcontrib-bibtexpdflink
allow links to PDF of papers and notes for each reference, which can be quite useful.


*scratch*


this extension is setup to require extension

The installation of that extension (sphinxcontrib-bibtexpdflink) results in the sphinxcontrib-bibtex and
sphinxcontrib-bibtex2 extensions both being installed since they are required by sphinxcontrib-bibtexpdflink.


This Sphinx extension (named "sphinx-filltableref", parsed as "fill table ref") creates tables
that contain data values that are from publications and includes links after the values to other
pages which have tables that again show the values along with a citation to the source publications.
This enables creating “summary” tables of data that link to other pages which contain “source” tables
that specify where the data is from (the reference) and can also describe the data values in more detail.

It results in the generation of the
summary table with filled-in data values and links to the other pages that specify the data source
(using the “tbldata” directives).


creates tables
that contain data values that are from publications and includes links after the values to other
pages which have tables that again show the values along with a citation to the source publications.
This 


The extension defines two Sphinx directives:  The “tblrender” directive is used to specify what the
summary table looks like (row and column labels and titles).  It results in the generation of the
summary table with filled-in data values and links to the other pages that specify the data source.
The “tbldata” directive is used to specify the source of the data values (which are used to fill in
the summary table) along with the citation.  Each tbldata directive results in the generation of a
table that shows the values and citations (to publications) specified by that directive.



 to produce a filled-in summary tabe at the location
of the “tbldata” directive, and The two directives work togther Each tbldata directive results in the
generation of a table that shows the values and citations (to publications) specified by that directive.
