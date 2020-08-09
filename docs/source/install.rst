.. _installation:

Installation
============

Install the extension with:

.. code-block:: shell

    $ pip install --index-url https://test.pypi.org/simple/ sphinxcontrib-filltableref

(This installs from Test PyPI).


The package is not yet on the real PyPI, but when it is, the installation command will be:


.. code-block:: shell

    $ pip install sphinxcontrib-filltableref


Configuring
-----------

Add the extension to the Sphinx ``conf.py`` file (along with extensions
sphinxcontrib.bibtexpdflink, sphinxcontrib.bibtex, and sphinxcontrib.bibtex2):

.. code-block:: shell

    extensions = [
        "sphinxcontrib.bibtex",
        "sphinxcontrib.bibtex2",
        "sphinxcontrib.bibtexpdflink",
        "sphinxcontrib.filltableref"
        ]


If it's desired to allow the citations to include links to PDF files and note files
(which is the purpose of the sphinxcontrib-bibtexpdflink extension), add the locations of the
PDF and notes file directories using config variables *bibtexpdflink_note_dir*
and *bibtexpdflink_pdf_dir* as describe in the
`documentation for sphinxcontrib-bibtexpdflink <https://sphinxcontrib-bibtexpdflink.readthedocs.io/>`_.
