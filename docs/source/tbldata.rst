.. _tbldata:

tbldata
=======

The *tbldata* directive (abbreviation for "table data") is used to specify data values
that are included in to the summary table (defined by the :ref:`tblrender` directive)
along with citation(s) to publications from which the values were found.  There can
be multiple *tbldata* directives for each *tblrender* directive (each *tbldata*
directive specifying additional data values).  The *tbldata* directive has the
following format:

.. code-block:: bnf

   
   .. tbldata:: <table_name>
      :id_prefix: <id_prefix>
   
      <row title>   | <expanded col title>   | Value       | Reference
      <row label-a> | <col label a>          | <value a>   | <reference a>
      <row label-b> | <col label b>          | <value b>   | <reference b>
      <row label-c> | <col label c>          | <value c>   | <reference c>
          .               .                       .             .
          .               .                       .             .
          .               .                       .             .


   Text describing the data (optional)
   

   .. footbibliography::


The entities in angle brackets are:

<table_name>
   Name of the summary table (used in the :ref:`tblrender` directive).

<id_prefix>
   A short prefix (for example 'a', 'b', 'gr') which will be used to make an id
   (e.g. a1, a2, a3 ...) associated with the row in the table.  It will be displayed as the link
   after the data value in the summary table and link to the source table.  The prefix
   should be unique for each source table.

<row title>
   The row title specified in the :ref:`tblrender` directive.

<expanded col title>
   Either the :ref:`<expanded_col_title> <tblrender_expanded_col_title>` 
   or the :ref:`<col title> <tblrender_col_title>` specified in the :ref:`tblrender` directive.
   (Either one is allowed, whatever seems most understandable should be used).

<row label-a>
   A <row label> in the summary table.

<col label a>
   A <col label> in the summary table.

<value a>
   A value to be inserted into the summary table for the specified <row label-a> and <col label a>.

<reference a>
   A reference (bibtex citation id) or a list of references, seperated by spaces or commas.


An example is shown below:

.. code-block:: rst


   .. tbldata:: table_loebner_fig2a
      :id_prefix: b
   
      Source cell | Cell count or Target cell   | Value       | Reference
      basket      | Cell count                  | 7.5x10^6    | LoebnerEE-1989
      basket      | purkinje                    | 9, 7.5x10^6 | LoebnerEE-1989
   
   
   Some text describing basket cells.
   
   
   .. footbibliography::
   


This is combined with the :ref:`tblrender_example` *tblrender* directive on the previous page to generate:


.. tbldata:: table_loebner_fig2a
   :id_prefix: b

   Source cell | Cell count or Target cell   | Value       | Reference
   basket      | Cell count                  | 7.5x10^6    | LoebnerEE-1989
   basket      | purkinje                    | 9, 7.5x10^6 | LoebnerEE-1989


Some text describing basket cells.


.. footbibliography::
   
