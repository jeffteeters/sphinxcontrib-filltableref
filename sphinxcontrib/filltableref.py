from docutils import nodes
from docutils.parsers.rst import Directive

# folloing for function parse_grid_table
import docutils.statemachine
import docutils.parsers.rst.tableparser

from sphinx.locale import _
from sphinx.util.docutils import SphinxDirective


# added going from todo to tbldata

from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles
import sys
import re
import pprint
pp = pprint.PrettyPrinter(indent=4)
import json
from sphinx.util.osutil import copyfile


# -- Added for APA style
# -- from: sphinxcontrib-bibtex/test/issue77

from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.labels.alpha import LabelStyle as AlphaLabelStyle
from pybtex.style.sorting import author_year_title


from pybtex.plugin import register_plugin
import os
from pybtex.style.template import (
    href, field, optional, sentence, words
)


class tbldata(nodes.Admonition, nodes.Element):
    pass


class tblrender(nodes.General, nodes.Element):
    pass


def visit_tbldata_node(self, node):
    self.visit_admonition(node)


def depart_tbldata_node(self, node):
    self.depart_admonition(node)

# utility functions
def get_table_name(d):
    # get table name from directive d
    table_name = d.arguments[0]
    assert len(table_name) > 0, "%s table_name must be present" % d
    assert re.search('\s', table_name) is None, "%s table_name must not contain white space: '%s'" % (d, table_name)
    return table_name

envinfokey = "tbldata_info"
def save_directive_info(env, key, info):
    # save directive info in environment
    global envinfokey
    assert key in ('tbldata', 'tblrender'), "save_directory_info, invalid key: %s" % key
    if not hasattr(env, envinfokey):
        # print("*** initializing envinfokey *** ")
        initial_value = {"tbldata":[], "tblrender":[]}
        setattr(env, envinfokey, initial_value)
    # print("saving info in env.%s[%s]" % (envinfokey, key))
    # pp.pprint(info)
    envinfo = getattr(env, envinfokey)
    envinfo[key].append(info)

def retrieve_directive_info(env, key):
    # retrieve info from environemnt 
    global envinfokey
    return env.envinfokey[key]


def make_tds(env):
    global envinfokey
    # convert envinfo (stored in: getattr(env, envinfokey)) to nested structures that
    # are used to make the tables and links
    #
    # Input (envinfo) contains:
    #
    # {'tbldata': [<ddi1>, <ddi2>, ...], 'tblrender': [ <rdi1>, <rdi2> ...]}
    # <ddi> ("data directive info") == { "docname": self.env.docname, "lineno": self.lineno, "table_name":table_name,
    #        "valrefs":valrefs, "target":target_node}  --- removed: "tbldata_node": tbldata_node.deepcopy() }
    #
    # <rdi> ("render directive info") == {"docname": self.env.docname, "table_name":table_name, "rows":rows, "cols":cols,
    #         "target": target_node}  --- removed:  "tblrender_node": tblrender_node.deepcopy()}
    #
    # Output (tds) - table data sorted, contains:
    #
    # { "tbldata":  # information from each tbldata directive, organized by table_name, row, col.
    #               # used when building the table 
    #     { <table_name>: { <row>: { <col>: [ <ddi-a>, <ddi-b> ... ], ... }, ... }, ... }
    #       where each <ddi> is the structure used in envinfo (but now accessable via row and column)
    #
    # { "tblrender":  # information from each tblrender directive, used for making link from tbldata directive node to table
    #     { <table_name>: [ <rdi>, ...], ... }
    #
    def get_tbldata_label(tag, table_name, fdocname, flineno, tri):
        # convert tag to title, label
        # tag is either "title:label", or label
        # if just label, need to find title.
        # do safety check for same title in table row and column
        # tri - table render info (from tds["tblrender"]["table_name"][0])
        if ":" in tag:
            title, label = tag.split(":")
            if title == tri['row_title']:
                if label not in tri['row_labels']:
                    print("ERROR: tbldata for table '%s' in %s line %s references '%s', but '%s' is not a "
                        "valid option for '%s' in "
                        "tblrender defined in file %s line %s" % (table_name, fdocname, flineno, tag, label,
                        title, tri["docname"], tri["lineno"]))
                    sys.exit("Aborting")
            elif title == tri['col_title'] or title == tri['expanded_col_title']:
               if label not in tri['col_labels']:
                    print("ERROR: tbldata for table '%s' in %s line %s references '%s', but '%s' is not a "
                        "valid option for '%s' in "
                        "tblrender defined in file %s line %s" % (table_name, fdocname, flineno, tag, label,
                        title, tri["docname"], tri["lineno"]))
                    sys.exit("Aborting")
            else:
                print("ERROR: tbldata for table '%s' in %s line %s references title '%s' which is not a "
                    "valid title; should be either:\n'%s' OR '%s' OR '%s'for\n"
                    "tblrender defined in file %s line %s" % (table_name, fdocname, flineno, title, tri["row_title"],
                    tri["col_title"], tri["expanded_col_title"], tri["docname"], tri["lineno"]))
                sys.exit("Aborting")
        else:
            label = tag
            inrows = label in tri['row_labels']
            incols = label in tri['col_labels']
            if inrows and incols:
                print("ERROR: tbldata for table '%s' in file %s line %s references '%s', which is ambiguous "
                    "since it could be either a '%s' or '%s' in "
                    "tblrender defined in file %s line %s" % (table_name, fdocname, flineno, label,
                    tri['row_title'], tri['col_title'], tri["docname"], tri["lineno"]))
                sys.exit("Aborting")
            if inrows:
                title = tri['row_title']
            elif incols:
                title = tri['col_title']
            else:
                print("tbldata for table '%s' in %s line %s references '%s' which is not a valid option for '%s' or '%s' "
                    "in tblrender defined in %s line %s" %(table_name, fdocname, flineno, tag, tri['row_title'],
                    tri['col_title'], tri["docname"], tri["lineno"]))
                sys.exit("Aborting")
        return [title, label]

    # start of mainline for function get_tds
    tds = {"tbldata": {}, "tblrender": {} }
    if not hasattr(env, envinfokey):
        # no envinfo, return empty tds structure
        return tds
    envinfo = getattr(env, envinfokey)
    # convert envinfo["tblrender"] to tds["tblrender"]
    for rdi in envinfo["tblrender"]:
        table_name = rdi["table_name"]
        if table_name not in tds["tblrender"]:
            tds["tblrender"][table_name] = []
        tds["tblrender"][table_name].append(rdi)
    # todo: check to make sure if more than one tblrender of the same table, the rows and cols match
    # print("tds before adding tbldata is:")
    # pp.pprint(tds)
    # convert envinfo["tbldata"] to tds["tbldata"]
    # print("starting make tds, envinfo=")
    # pp.pprint(envinfo)
    for ddi in envinfo["tbldata"]:
        table_name = ddi["table_name"]
        docname = ddi["docname"]
        lineno = ddi["lineno"]
        target = ddi["target"]
        valrefs = ddi["valrefs"]
        if table_name not in tds["tblrender"]:
            print("Error: Table '%s' referenced at %s line %s, but is not defined in a tblrender directive" % (
                table_name, docname, lineno))
            sys.exit("Aborting")
        # valrefs has format:
        # <list of: <row, col, val, reference> in JSON format, without outer enclosing []>                                                             
        # example:
        # ["basket", "cat", 234, "Albus-1989"], ["basket", "rat", 298, "Jones-2002"]
        # convert to JSON (add outer []) then decode to get values
        # print("valrefs=%s" % valrefs)
        # valrefs_decoded = json.loads( "[" + valrefs + "]" )
        tri = tds["tblrender"][table_name][0]
        for row_info in valrefs:
            tag1, tag2, value, reference, target_id = row_info
            title1, label1 = get_tbldata_label(tag1, table_name, docname, lineno, tri)
            title2, label2 = get_tbldata_label(tag2, table_name, docname, lineno, tri)
            if title1 == title2:
                print("Error: tbldata for table '%s', file %s line %s, row and column are both in '%s'.  Entry is:" % (
                    table_name, docname, lineno, title1))
                print("%s, %s, %s, %s" % (tag1, tag2, value, reference))
                sys.exit("Aborting")
            if title1 == tri["row_title"]:
                assert title2 in (tri["col_title"], tri['expanded_col_title'])
                row = label1
                col = label2
            else:
                assert title2 == tri["row_title"]
                assert title1 in (tri["col_title"], tri['expanded_col_title'])
                row = label2
                col = label1
            if table_name not in tds["tbldata"]:
                tds["tbldata"][table_name] = {}
            if row not in tds["tbldata"][table_name]:
                tds["tbldata"][table_name][row] = {}
            if col not in tds["tbldata"][table_name][row]:
                tds["tbldata"][table_name][row][col] = []
            ref_info = {"docname": docname, "lineno": lineno, "target":target, "valref": row_info}
            tds["tbldata"][table_name][row][col].append(ref_info)
    return tds


def purge_directive_info(app, env, docname):
    # def purge_tbldata(app, env, docname):
    global envinfokey
    if not hasattr(env, envinfokey):
        return
    envinfo = getattr(env, envinfokey)
    datainfo = [info for info in envinfo['tbldata']
        if info['docname'] != docname]
    renderinfo =[info for info in envinfo['tblrender']
                                if info['docname'] != docname]
    value = {'tbldata': datainfo, 'tblrender': renderinfo}
    setattr(env, envinfokey, value)


def make_target_node(env, prefix='tbldata'):
    target_id = "%s%d" % (prefix, env.new_serialno(prefix))
    target_node = nodes.target('','',ids=[target_id])
    return target_node


def render_rst(d, rst):
    # convert restructured text in rst to nodes for output for directive "d"
    # this copied from sphinxcontrib.datatemplates
    #     DataTemplateBase(rst.Directive) run method
    result = ViewList()
    data_source = d.env.docname
    for line in rst.splitlines():
        result.append(line, data_source)
    node = nodes.section()
    node.document = d.state.document
    nested_parse_with_titles(d.state, result, node)
    return node.children 

def parse_grid_table(text):
    # Clean up the input: get rid of empty lines and strip all leading and                                                                   
    # trailing whitespace.                                                                                                                   
    lines = filter(bool, (line.strip() for line in text.splitlines()))
    parser = docutils.parsers.rst.tableparser.GridTableParser()
    return parser.parse(docutils.statemachine.StringList(list(lines)))

def extract_gridtable_properties(tabledata):
    # get row and column titles and labels
    # Format of tabledata, from:
    # http://code.nabla.net/doc/docutils/api/docutils/parsers/rst/tableparser/docutils.parsers.rst.tableparser.GridTableParser.html
    # The first item is a list containing column widths (colspecs).
    # The second item is a list of head rows, and the third is a list of body rows.
    # Each row contains a list of cells. Each cell is either None (for a cell unused because of another cell’s span),
    # or a tuple. A cell tuple contains four items: the number of extra rows used by the cell in a vertical span
    # (morerows); the number of extra columns used by the cell in a horizontal span (morecols);
    # the line offset of the first line of the cell contents; and the cell contents, a list of lines of text.

    def slt(sl):
        # return text in StringList
        return " ".join(sl).strip()

    colwidths, headrows, bodyrows = tabledata
    num_cols = len(colwidths)
    num_headrows = len(headrows)
    assert num_headrows in (1, 2), "Must be one or two header rows, found: %s" % num_headrows
    if num_headrows == 2:
        head_col_types = ""
        for i in range(num_cols):
            if headrows[0][i] is not None:
                if headrows[1][i] is None:
                    head_col_types += "u"  # upper row only has content
                else:
                    head_col_types += "b"  # both upper and lower rows
            else:
                assert headrows[1][i] is not None, "both upper and lower header rows are None, should not happen"
                head_col_types += "l"  # lower row only has content
        # find index of first non-None in second header row
        ct_offset = next((i for i, v in enumerate(headrows[1]) if v is not None), -1)
        assert head_col_types[0] == "u", "First column of table with two hearder rows must span both columns"
        bc_index = head_col_types.find("b")
        if bc_index == -1:
            sys.exit("Two header rows in table, but no column with a column title (spaning both header rows)")
        if head_col_types[bc_index+1:] != "l"*(num_cols - bc_index - 1):
            sys.exit("Two header rows in table, but columns after column with title"
                " (spanning both header rows) are not all in lower row only.\nhead_col_types=%s, bc_index=%s\n"
                " head_col_types[bc_index+1:]='%s', 'l'*(num_cols - bc_index -1 )='%s'" %
                (head_col_types, bc_index, head_col_types[bc_index+1:], "l"*(num_cols - bc_index)))
        row_title = slt(headrows[0][0][3])
        col_labels = [ slt(headrows[0][i][3]) if head_col_types[i] == 'u'
                                                  else slt(headrows[1][i][3]) for i in range(1, num_cols) ]
        col_title_span_text = slt(headrows[0][bc_index][3])  # e.g. "Target cell"
        col_title_parts = [col_labels[i] for i in range(bc_index - 1)] + [ col_title_span_text ]
        expanded_col_title = " or ".join(col_title_parts)
        col_title = col_title_span_text
        row_labels = [slt(bodyrows[i][0][3]) for i in range (len(bodyrows))]
        # row_map = { row_labels[i]:i for i in range(len(row_labels))}
        # col_map = { col_labels[i]:i for i in range(len(col_labels))}
        # print("row_title='%s'" % row_title)
        # print("row_labels='%s'" % row_labels)
        # print("col_title='%s'" % col_title)
        # print("col_labels='%s'" % col_labels)
        # print("ct_offset='%s'" % ct_offset)
        # print("row_map=%s" % row_map)
        # print("col_map=%s" % col_map)
        gridtable_properties = { # "tabledata": tabledata,
            "row_title": row_title, "row_labels": row_labels,
            "col_title": col_title, "col_labels": col_labels,
            "expanded_col_title": expanded_col_title,
            "ct_offset": ct_offset }
            # "row_map":row_map, "col_map":col_map
    else:
        sys.exit("Grid table with only one header row not implemented")
    return gridtable_properties


def generate_grid_tabledata(di):
    # use directive info (di) to make grid tabledata structure (described in function extract_gridtable_properties)
    # that can be used to build table vi call to render_gridtable
    # This used if table specified by parameters (rows, cols, col_title, ct_offset) and not by
    # an explicit gridtable structure.
        # di - directive info (dictionary of info describing table)
    table_name = di['table_name']
    row_title = di["row_title"]
    row_labels = di["row_labels"]
    col_title = di["col_title"]
    col_labels = di["col_labels"]
    num_cols = len(col_labels) + 1  # plus 1 for row title
    ct_offset = di["ct_offset"]
    colwidths = [1] * num_cols  # generates list like: [1, 1, 1, ... ]
    hrow1 = []
    hrow2 = []
    for i in range(ct_offset):
        if i == 0:
            hrow1.append([1,0,1,[row_title, ]])
        else:
            hrow1.append([1,0,1,[col_labels[i-1], ]])
        hrow2.append(None)
    # add row title
    hrow1.append([0,num_cols-ct_offset-1,1,[col_title, ]])
    hrow2.append([0,0,1, [col_labels[ct_offset-1], ]])
    # complete headers
    for i in range(ct_offset, num_cols - 1):
        hrow1.append(None)
        hrow2.append([0,0,1, [col_labels[i],]])
    headrows = [hrow1, hrow2]
    # build body rows
    bodyrows = []
    for row_num in range(len(row_labels)):
        lineno = row_num * 2 + 3
        bodyrow = []
        bodyrow.append([0,0,lineno, [row_labels[row_num], ]])
        for i in range(1, num_cols):
            bodyrow.append( [0,0,lineno, ["", ]])
        bodyrows.append(bodyrow)
    tabledata = [colwidths, headrows, bodyrows] 
    return tabledata

# some code that was useful was adapted from:
# https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/docutils/docutils/parsers/rst/states.py#l1786
# def build_table_NOTUSED(tabledata, tableline, stub_columns=0, widths=None, classes=None):
# (but no longer used)


# class TblrenderDirective(Directive):
class TblrenderDirective(SphinxDirective):
    # tblrender directive specifies a table to render
    # format:
    # .. tblrender: <table_name>
    #    :description: <description of table>
    #    :rows: <row title>, <row labels>
    #    :cols: <col title>, <col labels>
    #    :expanded_col_title: <expanded_col_title>
    #    :ct_offset: <ct_offset>
    #    :'gridlayout: <gridtable>
    # example: (needs updating, see docs for latest)
    #.. tblrender: cell_counts
    #   :rows: "Cell type", "basket", "grannule"
    #   :cols: "species", "cat", "rat"
    required_arguments = 1
    option_spec = {
        'description': directives.unchanged_required,
        'rows': directives.unchanged,
        'cols': directives.unchanged,
        'expanded_col_title': directives.unchanged,
        'ct_offset': directives.unchanged,
        'gridlayout': directives.unchanged,
    }
    def run(self):
        table_name = get_table_name(self)
        description = self.options.get('description')
        rows = self.options.get('rows')
        cols = self.options.get('cols')
        expanded_col_title = self.options.get('expanded_col_title') # e.g.: Cell count or target cell
        if rows is not None or cols is not None:
            assert rows is not None and cols is not None and expanded_col_title is not None, ("If rows or cols"
                " specified, must specify all of: rows, cols, expanded_col_title")
            rows_decoded = json.loads( "[" + rows + "]" )
            row_title = rows_decoded[0]
            row_labels = rows_decoded[1:]
            cols_decoded = json.loads( "[" + cols + "]" )
            col_title = cols_decoded[0]
            col_labels = cols_decoded[1:]
            expanded_col_title = expanded_col_title.strip("'"+ '"' + " ")
            ct_offset = int(self.options.get('ct_offset', 1))  # number of columns to skip before adding col_title header
            ptable_properties = {"row_title":row_title, "row_labels":row_labels,
                "col_title":col_title, "col_labels":col_labels, "expanded_col_title":expanded_col_title,
                "ct_offset": ct_offset}
        else:
            ptable_properties = None
        gridlayout = self.options.get('gridlayout')
        if gridlayout is not None:
            # print("found gridlayout:\n%s" % gridlayout)
            grid_tabledata = parse_grid_table(gridlayout)
            # print("headrows=")
            # pp.pprint(grid_tabledata[1])
            # print("bodyrows=")
            # pp.pprint(grid_tabledata[2])
            gridtable_properties = extract_gridtable_properties(grid_tabledata)
            tableline = self.lineno  # a guess
            # grid_table_rst = build_table(grid_tabledata, tableline, widths="grid", stub_columns=1, classes="tblrender")
        else:
            # grid_table_rst = []
            gridtable_properties = None
            grid_tabledata = None
        if gridtable_properties is None and ptable_properties is None:
            sys.exit("Must specify row and col properties or a gridtable or both")
        # if both specified, use gridtable
        make_ptable = ptable_properties is not None and gridtable_properties is None
        if gridtable_properties is not None:
            if ptable_properties is not None:
                assert gridtable_properties["row_title"] == ptable_properties["row_title"]
                assert gridtable_properties["row_labels"] == ptable_properties["row_labels"]
                assert gridtable_properties["col_title"] == ptable_properties["col_title"]
                assert gridtable_properties["col_labels"] == ptable_properties["col_labels"]
                assert gridtable_properties["ct_offset"] == ptable_properties["ct_offset"]
                assert gridtable_properties["expanded_col_title"] == ptable_properties["expanded_col_title"], (
                    "expanded_col_title in: gridtable='%s', ptable='%s'" % (
                        gridtable_properties["expanded_col_title"], ptable_properties["expanded_col_title"]))        
            table_properties = gridtable_properties
        else:
            table_properties = ptable_properties
        tblrender_node = tblrender('')
        # add description to rst for table
        desc_rst = render_rst(self, "\n" + description + "\n\n")
        directive_info = {"docname": self.env.docname, "table_name":table_name,
             "desc_rst": desc_rst, "lineno": self.lineno,
             **table_properties,
             "grid_tabledata": grid_tabledata,
             "make_ptable": make_ptable
             }
        # save directive_info as attribute of object so is easy to retrieve in replace_tbldata_and_tblrender_nodes
        tblrender_node['directive_info'] = directive_info
        save_directive_info(self.env, 'tblrender', directive_info)
        nodes = desc_rst + [tblrender_node]
        return nodes

CSS_FILENAME = "filltableref.css"

def add_assets(app):
    app.add_css_file(CSS_FILENAME)
    # app.add_js_file(JS_FILENAME)

def copy_assets(app, exception):
    if app.builder.name not in ["html", "readthedocs"] or exception:
        return
    for filename in [CSS_FILENAME, ]: # JS_FILENAME]:
        copyfile(os.path.join(os.path.abspath(os.path.dirname(__file__)), filename),
                 os.path.join(app.builder.outdir, "_static", filename))

# from: https://groups.google.com/forum/#!msg/sphinx-users/Z-wcktOhIAc/pGDWO0yVBQAJ
# (not used)
# def html_page_context_NOT_USED(app, pagename, templatename, context, doctree):
#   """Add CSS string to HTML pages that contain code cells."""
   

class TbldataDirective(SphinxDirective):
    # tbldata directive specifies data to be included in a table, and also to be shown where the directive is
    # located (making a partial table).  Example format is:
    # .. tbldata: <table_name>
    #
    #    From Cell   |   To Cell  |  Value   |  Reference
    #    basket      |   # cells  |  367     |  Albus-1989
    #    basket      |   perkinje |  45,47   |  Loebner-1963
    #
    # .. tbldata: cell_counts
    #
    #    Cell Type   |   Species  |  Value   |  Reference
    #    Basket      |   Cat      |  234     |  Albus-1989
    #    Basket      |   Rat      |  298     |  Jones-2002
    #
    #
    # Previous style:
    #    :valrefs: <list of: <row, col, val, reference> in JSON format, without outer enclosing []>
    # example:
    # .. tbldata: cell_counts
    #    :valrefs: ["basket", "cat", 234, "Albus-1989"], ["basket", "rat", 298, "Jones-2002"]
    required_arguments = 1
    option_spec = {
        'valrefs': directives.unchanged,
        'id_prefix': directives.unchanged_required,
        'comment': directives.unchanged,
    }
    # this enables content in the directive
    # include content as comment?
    has_content = True
    def run(self):
        table_name = get_table_name(self)
        target_node = make_target_node(self.env)
        tbldata_node = tbldata()
        # valrefs = self.options.get('valrefs')
        content = self.content
        if len(content) == 0:
            msg = "No data provided for table %s" % table_name
            msg = nodes.Text(msg, msg)
            tbldata_node += msg
            return [ target_node, tbldata_node ]
        id_prefix = self.options.get('id_prefix')
        if id_prefix is None:
            print("Found id_prefix None")
            import pdb; pdb.set_trace()
        else:
            id_prefix = id_prefix.strip('"' + "'" + " ")
        # print("content=%s" % content)
        input_rows = content  # .splitlines() # is already split
        header = [x.strip() for x in input_rows[0].split("|")]
        assert len(header) == 4
        assert len(header[0]) > 0
        assert len(header[1]) > 0
        assert ":" not in header[0]
        assert ":" not in header[1]
        assert header[2] == "Value"
        assert header[3] == "Reference"
        valrefs_decoded = []
        # caption can go after list-table::  List tables can have captions like this one.
        table_rst = """
.. list-table::
   :widths: 5 10 10 10 10
   :header-rows: 1
   :stub-columns: 0

   * - Id
     - %s
     - %s
     - Value
     - Reference
""" % (header[0], header[1])
        for row_num in range(1, len(input_rows)):
            input_row = input_rows[row_num]
            # for input_row in input_rows[1:]:
            elements = [x.strip() for x in input_row.split("|")]
            assert len(elements) == 4
            assert ":" not in elements[0]
            assert ":" not in elements[1]
            assert len(elements[0]) > 0
            assert len(elements[1]) > 0
            assert len(elements[2]) > 0
            assert len(elements[3]) > 0
            # target_id = "%s%s" % (id_prefix, env.new_serialno(id_prefix))
            target_id = "%s%s" % (id_prefix, row_num)
            # target_id_node = nodes.target('','',ids=[target_id])
            valrefs = [ header[0] + ":" + elements[0], header[1] + ":" + elements[1], elements[2], elements[3],
                target_id]
            valrefs_decoded.append(valrefs)
            if elements[2] == "-" and elements[3] == "-":
                # no value or reference
                rst_ref = "`-`"
                show_val = "`-`"
            else:
                # in case multiple references, include them all
                rst_ref = []
                for ref in re.split('[ ,;]+', elements[3]):
                    rst_ref.append(":cite:`%s` :footcite:`%s`" % (ref, ref))
                rst_ref = "; ".join(rst_ref)
                # rst_ref = ":cite:`%s` :footcite:`%s`" % (elements[3], elements[3])
                # if 'Albus' in rst_ref:
                #    print("multiple reference rst_ref='%s'" % rst_ref)
                show_val = elements[2]
            table_rst += "   * - %s\n     - %s\n     - %s\n     - %s\n     - %s\n" % (
                target_id, elements[0], elements[1], show_val, rst_ref)
        title = "Data for table :ref:`%s`" % table_name
        rst = []
        rst.append(".. cssclass:: tbldata-title")
        rst.append("")
        rst.append(title)
        rst.append("")
        rst.append("The following table has data and references for table :ref:`%s`." % table_name)
        title_nodes = render_rst(self, "\n".join(rst))
        table_nodes = render_rst(self, table_rst)
        directive_info = { "docname": self.env.docname, "lineno": self.lineno, "table_name":table_name,
            "valrefs":valrefs_decoded, "target":target_node} #  "tbldata_node": tbldata_node.deepcopy()
        # save directive_info as attribute of object so is easy to retrieve in replace_tbldata_and_tblrender_nodes
        # tbldata_node.directive_info = directive_info
        tbldata_node['directive_info'] = directive_info
        # print("after saving directive info, tbldata node has:")
        # pp.pprint(dir(tbldata_node))
        save_directive_info(self.env, 'tbldata', directive_info)
        # print("saved directive_info to tbldata_node id = %s" % id(tbldata_node))
        # output_nodes = [target_node, tbldata_node, ] + rst_nodes
        # output_nodes = [target_node, ] + rst_nodes + [tbldata_node, ]
        output_nodes = [target_node, ] + title_nodes + [ tbldata_node, ] + table_nodes
        return output_nodes


def format_table_data(tds, app, fromdocname):
    # format data provided in tbldata directives into nodes that can be inserted into tables
    # (specified by the tblrender directives)
    # Returns dictionary ftd (formatted table data):
    # ftd[table_name][row][col] = [<formatted data>, <plain_text_value>, <from_document_name>, <id_number> ] 
    ftd = {}
    for table_name in tds["tbldata"]:
        for row in tds["tbldata"][table_name]:
            for col in tds["tbldata"][table_name][row]:
                ddis = tds["tbldata"][table_name][row][col]
                para = nodes.paragraph()
                first_node = True
                for ddi in ddis:
                    target = ddi["target"]
                    row_info = ddi["valref"]
                    vrow, vcol, vval, vref, target_id = row_info
                    docname = ddi["docname"]
                    # check for "-" in both value and vref.  If found, just display '-' without a link to a target
                    # this is used to allow including dashes to indicate there can be no value for this table cell
                    if vval == '-' and vref == '-':
                        newnode = nodes.Text('-', '-')
                    else:
                        # create a reference to new Id in a row
                        use_id_links = True
                        if use_id_links:
                            idref = nodes.reference('','')
                            idref['refdocname'] = ddi['docname']
                            idref['refuri'] = app.builder.get_relative_uri(
                                fromdocname, ddi['docname'])         
                            idref['refuri'] += '#' + target['refid']
                            reftext = " [" + target_id + "]"
                            idref_id = nodes.Text(reftext, reftext)
                            idref.append(idref_id)
                            valtxt = nodes.Text(vval, vval)
                            newnode = [valtxt, idref]  # += works with lists
                        else:
                            # original code, no id-links
                            # create a reference
                            newnode = nodes.reference('','')
                            newnode['refdocname'] = ddi['docname']
                            newnode['refuri'] = app.builder.get_relative_uri(
                                fromdocname, ddi['docname'])
                            # below line, version for linking to table
                            newnode['refuri'] += '#' + ddi['target']['refid']
                            # innernode = nodes.emphasis(vref, vref)
                            innernode = nodes.emphasis(vval, vval)
                            newnode.append(innernode)
                    # seperator = "; " if not first_node else ""
                    if not first_node:
                        seperator = "; "
                        para += nodes.Text(seperator, seperator)
                    first_node = False
                    # val_str = "%s%s " % (seperator, vval)
                    # para += nodes.Text(val_str, val_str)
                    para += newnode
                # save para in ftd
                if table_name not in ftd:
                    ftd[table_name] = {}
                if row not in ftd[table_name]:
                    ftd[table_name][row] = {}
                # following only stores most recent values
                entry_data = [para, vval, docname, target_id]
                ftd[table_name][row][col] = entry_data
    return ftd


def render_gridtable(di, grid_tabledata, ftd):
    # di - directive info (dictionary of info describing table)
    # grid_tabledata - structure generated from parsing gridtable or generated from ptable proprties
    # ftd - formatted table data - values to store in rendered table
    # print("entered render_gridtable; grid_tabledata=")
    # pp.pprint(grid_tabledata)
    # print("ftd=")
    # pp.pprint(ftd)
    table_name = di['table_name']
    row_labels = di["row_labels"]
    col_labels = di["col_labels"]
    row_map = { i:row_labels[i] for i in range(len(row_labels))}
    col_map = { i:col_labels[i] for i in range(len(col_labels))}
    tableline = di["lineno"]  # not currently used, but was a parameter to original function below
    grid_table_rst = render_gridtable_rst(grid_tabledata, tableline,
        widths="grid", stub_columns=1, table_name=table_name, # classes="tblrender",
        row_map=row_map, col_map=col_map, ftd=ftd)
    return grid_table_rst

# following adapted from:
# https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/docutils/docutils/parsers/rst/states.py#l1786
def render_gridtable_rst(tabledata, tableline, stub_columns=0, widths=None, classes=None,
    table_name=None, row_map=None, col_map=None, ftd=None):
    colwidths, headrows, bodyrows = tabledata
    table = nodes.table()
    if widths == 'auto':
        table['classes'] += ['colwidths-auto']
    elif widths: # "grid" or list of integers
        table['classes'] += ['colwidths-given']
    if classes is not None:
        table['classes'] += classes.split()
    tgroup = nodes.tgroup(cols=len(colwidths))
    table += tgroup
    for colwidth in colwidths:
        colspec = nodes.colspec(colwidth=colwidth)
        if stub_columns:
            colspec.attributes['stub'] = 1
            stub_columns -= 1
        tgroup += colspec
    if headrows:
        thead = nodes.thead()
        tgroup += thead
        for row in headrows:
            thead += build_gridtable_row(row, tableline)
    tbody = nodes.tbody()
    tgroup += tbody
    for row_num in range(len(bodyrows)):
        rowdata = bodyrows[row_num]
        tbody += build_gridtable_row(rowdata, tableline, table_name=table_name,
            row_num=row_num, row_map=row_map, col_map=col_map, ftd=ftd)
    return table

def build_gridtable_row(rowdata, tableline, table_name=None, row_num=None, row_map=None, col_map=None, ftd=None):
    row = nodes.row()
    for cell_num in range(len(rowdata)):
        cell = rowdata[cell_num]
        if cell is None:
            continue
        morerows, morecols, offset, cellblock = cell
        attributes = {}
        if morerows:
            attributes['morerows'] = morerows
        if morecols:
            attributes['morecols'] = morecols
        entry = nodes.entry(**attributes)
        row += entry
        table_val = " ".join(cellblock).strip()
        if (ftd is not None and table_name in ftd and row_map[row_num] in ftd[table_name] and
            cell_num > 0 and col_map[cell_num-1] in ftd[table_name][row_map[row_num]]):
            # have data for this cell
            ftd_entry = ftd[table_name][row_map[row_num]][col_map[cell_num-1]]
        else:
            ftd_entry = None
        if table_val:
            if ftd_entry is not None:
                para, vval, docname, target_id = ftd_entry
                sys.exit("Table %s, value specified in gridtable (%s) and in tbldata (%s) "
                    "from file '%s', id '%s' for row '%s'"
                    " col '%s'.  Should only be specified one location" % ( table_name, table_val,
                    vval, docname, target_id, row_map[row_num], col_map[cell_num-1]))
            entry += nodes.paragraph(text=table_val)
        elif ftd_entry is not None:
            # entry += ftd[table_name][row_map[row_num]][col_map[cell_num-1]][0]
            entry += ftd_entry[0]
    return row



def replace_tbldata_and_tblrender_nodes(app, doctree, fromdocname):
    # Does the following:
    #
    # * Replace all tblrender nodes with a table of the data with values in the table
    #   linking to the tbldata directive where the values and references were specified.
    #
    # * Modify each tbldata node with a link to the table generated containing the data.
    #   If the table appears in more than one location, for now, just pick the first location

    global envinfokey
    # print("starting replace_tbldata_and_tblrender_nodes, docname='%s'" % fromdocname)
    env = app.builder.env
    tds = make_tds(env)
    ftd = format_table_data(tds, app, fromdocname)
    # print("tds['tbldata']=")
    # pp.pprint(tds['tbldata'])
    # print("ftd=")
    # pp.pprint(ftd)
    # tds has format:
    # {
    #   "tbldata":  # information from each tbldata directive, organized by table_name, row, col.
    #               # used when building the table 
    #     { <table_name>: { <row>: { <col>: [ <tde1>, <tde2> ... ], ... }, ... }, ... }
    #       where each tde (table data entry) is: 
    #          { "value": <value>, "reference": <reference>, "ddi": <ddi> }, 
    #
    #   "tblrender":  # information from each tblrender directive, used for making link from tbldata directive node to table
    #     { <table_name>: [ <rdi>, ...], ... }
    # }
    # where:
    #
    # <ddi> ("data directive info") == { "docname": self.env.docname, "lineno": self.lineno, "table_name":table_name,
    #        "valrefs":valrefs, "target":target_node, "tbldata_node": tbldata_node.deepcopy() }
    #
    # <rdi> ("render directive info") == {"docname": self.env.docname, "table_name":table_name, "rows":rows, "cols":cols,
    #         "target": target_node, "tblrender_node": tblrender_node.deepcopy()}

    # insert description into tbldata tables
    # temporary, try to get directive info for tbldata
    for node in doctree.traverse(tblrender):
        di = node['directive_info']
        node_lst = []  # node list
        # para1 = nodes.paragraph()
        # msg = "tblrender tables go here"
        # para1 += nodes.Text(msg, msg)
        # node_lst.append(para1)
        # node_lst += di["desc_rst"]
        if di["make_ptable"]:
            para2 = nodes.paragraph()
            # msg = "ptable follows"
            # para2 += nodes.Text(msg, msg)
            node_lst.append(para2)
            # ptable = render_ptable(di, ftd)
            grid_tabledata = generate_grid_tabledata(di)
            ptable = render_gridtable(di, grid_tabledata, ftd)
            node_lst.append(ptable)
        if di["grid_tabledata"] is not None:
            para3 = nodes.paragraph()
            # msg = "gridtable follows"
            # para3 += nodes.Text(msg, msg)
            node_lst.append(para3)
            grid_tabledata = di["grid_tabledata"]
            gridtable = render_gridtable(di, grid_tabledata, ftd)
            node_lst.append(gridtable)
        node += node_lst
        node.replace_self(node_lst)

    # insert description into tbldata tables
    for node in doctree.traverse(tbldata):
        if 'directive_info' in node.attributes:
            di = node['directive_info']
            table_name = di['table_name']
            desc_rst = tds['tblrender'][table_name][0]['desc_rst']
            for i in range(1, len(node.parent.children)):
                if node.parent.children[i] == node:
                    break;
            assert node.parent.children[i] == node, "Failed to find index of tbldata node"
            prevp = node.parent.children[i-1]
            prevp += nodes.Text(' ', ' ')
            prevp += desc_rst[0].children
            # remove tbldata node
            node.replace_self(nodes.Text('', ''))
            # node.replace_self(desc_rst)
    return

saved_app = None
def setup(app):
    # save app so can get config value and source directory for building links to PDF files
    global saved_app
    saved_app = app

    app.add_node(tblrender)
    app.add_node(tbldata,
                 html=(visit_tbldata_node, depart_tbldata_node),
                 latex=(visit_tbldata_node, depart_tbldata_node),
                 text=(visit_tbldata_node, depart_tbldata_node))

    app.add_directive('tbldata', TbldataDirective)
    app.add_directive('tblrender', TblrenderDirective)
    app.connect('doctree-resolved', replace_tbldata_and_tblrender_nodes)
    app.connect('env-purge-doc', purge_directive_info)
    # from:
    # https://github.com/spatialaudio/nbsphinx/blob/ca978181ecb045974d399b522c03b96305b85290/src/nbsphinx.py#L1488-L1498
    # app.connect('html-page-context', html_page_context)
    # following for css files, from https://pypi.org/project/sphinxcontrib-platformpicker/
    app.connect("builder-inited", add_assets)
    app.connect("build-finished", copy_assets)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
