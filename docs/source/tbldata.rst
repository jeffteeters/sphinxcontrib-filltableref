tbldata
=======

The ``tbldata`` directive is used to specify data values that included in
to the summary table along with citation(s) to publications from which the values
were found.  It is used in the following way:

.. code-block:: rst

   
   .. tbldata:: <table_name>
      :valrefs: ["Source cell:basket", "Cell count", "7.5x10^6", "LoebnerEE-1989"],
                ["Source cell:basket", "Target cell:purkinje", "9, 7.5x10^6", "LoebnerEE-1989"],
                ["Source cell:basket", "Target cell:basket", "-", "-"]
      :id_prefix: <id_prefix>
   
      <row title>   | <expanded col title>   | Value       | Reference
      <row label-a> | <col label a>          | <value a>   | <reference a>
      <row label-b> | <col label b>          | <value b>   | <reference b>
      <row label-c> | <col label c>          | <value c>   | <reference c>
          .               .                       .             .
          .               .                       .             .
          .               .                       .             .


   <Text describing the data (optional)>
   

   .. footbibliography::


Where:

<table_name>
   is the name of the summary table (used in the ``tblrender`` directive.

<id_prefix>
   is a prefix (for example 'a', 'b', 'gr') which will be used to make an id associated
   with the row in the table.  (e.g. a1, a2, a3 ...).  It will be displayed as the link
   after the data value in the summary table and link to the source table.  The prefix
   should be unique for each source table.

<row title>
   is the row title specified in the ``tblrender`` directive.

<expanded col title>
   is a title formed by concatination the summary table <column label>s that are not an instance of the
   <col title> and the <col title> with all parts seperated by " or ".  An example is shown below.

<row label-a>
   A <row label> in the summary table.

<col label a>
   A <col label> in the summary table.

<value a>
   A value to be inserted into the summary table for the specified <row label-a> and <col label a>.

<reference a>
   A reference (bibtex citation id).  May also include a list of references, seperated by spaces or commas.


An example is shown below:


   .. tbldata:: table_loebner_fig2a
      :valrefs: ["Source cell:basket", "Cell count", "7.5x10^6", "LoebnerEE-1989"],
                ["Source cell:basket", "Target cell:purkinje", "9, 7.5x10^6", "LoebnerEE-1989"],
                ["Source cell:basket", "Target cell:basket", "-", "-"]
      :id_prefix: b
   
      Source cell | Cell count or Target cell   | Value       | Reference
      basket      | Cell count                  | 7.5x10^6    | LoebnerEE-1989
      basket      | purkinje                    | 9, 7.5x10^6 | LoebnerEE-1989
   
   
   Some text describing basket cells.
   
   
   .. footbibliography::
   


This is rendered as:


.. tbldata:: table_loebner_fig2a
   :valrefs: ["Source cell:basket", "Cell count", "7.5x10^6", "LoebnerEE-1989"],
             ["Source cell:basket", "Target cell:purkinje", "9, 7.5x10^6", "LoebnerEE-1989"],
             ["Source cell:basket", "Target cell:basket", "-", "-"]
   :id_prefix: b

   Source cell | Cell count or Target cell   | Value       | Reference
   basket      | Cell count                  | 7.5x10^6    | LoebnerEE-1989
   basket      | purkinje                    | 9, 7.5x10^6 | LoebnerEE-1989


Some text describing basket cells.


.. footbibliography::
   

