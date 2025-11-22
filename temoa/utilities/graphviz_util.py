from collections.abc import Callable, Iterable, Sequence, Sized


def get_color_config(*, grey_flag: bool) -> dict[str, str | tuple[str, ...]]:
    """Return a dictionary of color configurations for the graph."""

    is_colored = not grey_flag
    kwargs: dict[str, str | tuple[str, ...]] = {
        'tech_color': 'darkseagreen' if is_colored else 'black',
        'commodity_color': 'lightsteelblue' if is_colored else 'black',
        'unused_color': 'powderblue' if is_colored else 'gray75',
        'arrowheadout_color': 'forestgreen' if is_colored else 'black',
        'arrowheadin_color': 'firebrick' if is_colored else 'black',
        'usedfont_color': 'black',
        'unusedfont_color': 'chocolate' if is_colored else 'gray75',
        'menu_color': 'hotpink',
        'home_color': 'gray75',
        'font_color': 'black' if is_colored else 'white',
        'fill_color': 'lightsteelblue' if is_colored else 'white',
        # MODELDETAILED,
        'md_tech_color': 'hotpink',
        'sb_incom_color': 'lightsteelblue' if is_colored else 'black',
        'sb_outcom_color': 'lawngreen' if is_colored else 'black',
        'sb_vpbackg_color': 'lightgrey',
        'sb_vp_color': 'white',
        'sb_arrow_color': 'forestgreen' if is_colored else 'black',
        # SUBGRAPH 1 ARROW COLORS
        'color_list': (
            (
                'red',
                'orange',
                'gold',
                'green',
                'blue',
                'purple',
                'hotpink',
                'cyan',
                'burlywood',
                'coral',
                'limegreen',
                'black',
                'brown',
            )
            if is_colored
            else ('black', 'black')
        ),
    }
    return kwargs


def _get_len(key: int) -> Callable[[Sequence[Sized]], int]:
    """Return a function that gets the length of an item at a specific index in a sequence."""

    def wrapped(obj: Sequence[Sized]) -> int:
        return len(obj[key])

    return wrapped


def create_text_nodes(nodes: Iterable[tuple[str, str]], indent: int = 1) -> str:
    """
    Return a set of text nodes in Graphviz DOT format, optimally padded for
    easier reading and debugging.

    Args:
        nodes: iterable of (id, attribute) node tuples
               e.g. [(node1, attr1), (node2, attr2), ...]
        indent: integer, number of tabs with which to indent all Dot node lines
    """
    # Convert to list to avoid consuming iterable multiple times if it's an iterator
    nodes_list = list(nodes)
    if not nodes_list:
        return '// no nodes in this section\n'

    # Step 1: for alignment, get max item length in node list
    # The `+ 2` accounts for the two extra quotes that will be added.
    maxl = max(map(_get_len(0), nodes_list), default=0) + 2

    # Step 2: prepare a text format based on max node size that pads all
    #         lines with attributes
    nfmt_attr = f'{{0:<{maxl}}} [ {{1}} ] ;'  # node text format
    nfmt_noa = '{0} ;'

    # Step 3: create each node, and place string representation in a set to
    #         guarantee uniqueness
    q = '"%s"'  # enforce quoting for all nodes
    gviz = {nfmt_attr.format(q % n, a) for n, a in nodes_list if a}
    gviz.update(nfmt_noa.format(q % n) for n, a in nodes_list if not a)

    # Step 4: return a sorted version of nodes, as a single string
    indent_str = '\n' + '\t' * indent
    return indent_str.join(sorted(gviz))


def create_text_edges(edges: Iterable[tuple[str, str, str]], indent: int = 1) -> str:
    """
    Return a set of text edge definitions in Graphviz DOT format, optimally
    padded for easier reading and debugging.

    Args:
        edges: iterable of (from, to, attribute) edge tuples
               e.g. [(inp1, tech1, attr1), (inp2, tech2, attr2), ...]
        indent: integer, number of tabs with which to indent all Dot edge lines
    """
    # Convert to list
    edges_list = list(edges)
    if not edges_list:
        return '// no edges in this section\n'

    # Step 1: for alignment, get max length of items on left and right side of
    # graph operator token ('->'). The `+ 2` accounts for the two extra quotes.
    maxl = max(map(_get_len(0), edges_list), default=0) + 2
    maxr = max(map(_get_len(1), edges_list), default=0) + 2

    # Step 2: prepare format to be "\n\tinp+PADDING -> out+PADDING [..."
    efmt_attr = f'{{0:<{maxl}}} -> {{1:<{maxr}}} [ {{2}} ] ;'  # with attributes
    efmt_noa = f'{{0:<{maxl}}} -> {{1}} ;'  # no attributes

    # Step 3: add each edge to a set (to guarantee unique entries only)
    q = '"%s"'  # enforce quoting for all tokens
    gviz = {efmt_attr.format(q % i, q % t, a) for i, t, a in edges_list if a}
    gviz.update(efmt_noa.format(q % i, q % t) for i, t, a in edges_list if not a)

    # Step 4: return a sorted version of the edges, as a single string
    indent_str = '\n' + '\t' * indent
    return indent_str.join(sorted(gviz))
