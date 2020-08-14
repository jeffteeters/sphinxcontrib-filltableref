**************
LoebnerEE-1989
**************

Notes about :cite:`LoebnerEE-1989` :footcite:`LoebnerEE-1989` .


Figure 2 in the paper provides data about the number of cells of different types in the cat cerebellum.

The number of cells of each type given in the figure is:

+-----------+-----------------+
| Cell type | Number of cells |
+===========+=================+
| basket    | 7.5x10^6        |
+-----------+-----------------+
| golgi     | 4.2x10^5        |
+-----------+-----------------+
| granule   | 2.2x10^9        |
+-----------+-----------------+
| purkinje  | 1.3x10^6        |
+-----------+-----------------+
| stellate  | 2.1x10^7        |
+-----------+-----------------+


This data is included in the example summary table using the following :ref:`tbldata` directive.
(The basket cell data is not included because it is provided in the other example *tbldata*
directive.)

.. code-block:: rst

   .. tbldata:: table_loebner_fig2a
      :id_prefix: n
   
      Source cell | Cell count or Target cell   | Value       | Reference
      golgi       | Cell count                  | 4.2x10^5    | LoebnerEE-1989
      granule     | Cell count                  | 2.2x10^9    | LoebnerEE-1989
      purkinje    | Cell count                  | 1.3x10^6    | LoebnerEE-1989
      stellate    | Cell count                  | 2.1x10^7    | LoebnerEE-1989
   
   
   .. footbibliography::
   

It is rendered as:


.. tbldata:: table_loebner_fig2a
   :id_prefix: n

   Source cell | Cell count or Target cell   | Value       | Reference
   golgi       | Cell count                  | 4.2x10^5    | LoebnerEE-1989
   granule     | Cell count                  | 2.2x10^9    | LoebnerEE-1989
   purkinje    | Cell count                  | 1.3x10^6    | LoebnerEE-1989
   stellate    | Cell count                  | 2.1x10^7    | LoebnerEE-1989



.. footbibliography::






