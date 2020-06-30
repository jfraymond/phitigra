# -*- coding: utf-8 -*-
r"""
TalkyGraph

This module defines the ``TalkyGraph`` class, that subclasses Sage's ``Graph`
class to trigger a notification when changes are made to the instances.
"""

# ****************************************************************************
#
#       Copyright (C) 2020      Jean-Florent Raymond <j-florent.raymond@uca.fr>
#
# ****************************************************************************

from sage.graphs.all import Graph


class TalkyGraph(Graph):
    """
    Subclass of Sage's ``Graph`` class that behaves exactly the same, except
    that a callback is called when changes are made to the instance (addition
    and deletion of vertices).

    EXAMPLES:
        sage: def f(s): print("Notification: " + str(s))
        sage: g = TalkyGraph(notify_callback=f)
        sage: g.add_vertex(0)
        Notification: add_vertex
        sage: g.add_vertex()
        Notification: add_vertex
        1
        sage: g.add_edge(0, )
        Notification: add_edge
        sage: g.delete_vertex(1)
        Notification: delete_vertex

    The default callback is the function that does nothing::
 
        sage: h = TalkyGraph()
        sage: h.add_vertex()
        0

    TESTS:

    The construction of the graph does not trigger any notification::

        sage: def f(s): print("Notification: " + str(s))
        g = TalkyGraph(2, notify_callback=f); g
        Graph on 2 vertices
    """

    def __init__(self, *args, **kwargs):
        # Get the callback if given or use a no-op function otherwise
        notify = kwargs.pop('notify_callback', lambda x:None)
        super().__init__(*args, **kwargs)

        # notify_change refers to the callback that functions modifying the
        # graph will call. We define it after the call to Graph's constructor
        # so that no notification is done until the graph is completely built
        self.notify_change = notify

    def _repr_(self):
        """
        Return a string representation of the graph.

        EXAMPLES::

            sage: g = TalkyGraph(5); g
            TalkyGraph with base Graph on 5 vertices
            sage: g = TalkyGraph(graphs.PetersenGraph()); g
            TalkyGraph with base Petersen graph: Graph on 10 vertices
        """
        return "TalkyGraph with base " + Graph._repr_(self)
        
    def add_vertex(self, *args, **kwargs):
        r"""
        Create an isolated vertex.

        Same as :meth:`Graph.add_vertex` but followed by a call to
        :meth:`notify_change`.

        TESTS::

            sage: def f(s): print("The graph changed: " + str(s))
            sage: g = TalkyGraph(notify_callback=f)
            sage: g.add_vertex(0)
            The graph changed: add_vertex
            sage: g.add_vertex()
            The graph changed: add_vertex
            1
        """
        r = Graph.add_vertex(self, *args, **kwargs)
        self.notify_change('add_vertex')    # , *args, **kwargs)
        return r

    def delete_vertex(self, *args, **kwargs):
        r"""
        Delete vertex, removing all incident edges.

        Same as :meth:`Graph.delete_vertex` but followed by a call to
        :meth:`notify_change`.

        TESTS::

            sage: def f(s): print("The graph changed: " + str(s))
            sage: g = TalkyGraph(2, notify_callback=f)
            sage: g.delete_vertex(1)
            The graph changed: delete_vertex
            sage: g.delete_vertex(1)
            Traceback (most recent call last):
            ...
            ValueError: vertex (1) not in the graph
        """
        r = Graph.delete_vertex(self, *args, **kwargs)
        self.notify_change('delete_vertex')    # , *args, **kwargs)
        return r

    def add_vertices(self, *args, **kwargs):
        r = Graph.add_vertices(self, *args, **kwargs)
        self.notify_change('add_vertices')    # , *args, **kwargs)
        return r

    def delete_vertices(self, *args, **kwargs):
        r = Graph.delete_vertices(self, *args, **kwargs)
        self.notify_change('delete_vertices')    # , *args, **kwargs)
        return r

    def add_edge(self, *args, **kwargs):
        r = Graph.add_edge(self, *args, **kwargs)
        self.notify_change('add_edge')    # , *args, **kwargs)
        return r

    def delete_edge(self, *args, **kwargs):
        r = Graph.delete_edge(self, *args, **kwargs)
        self.notify_change('delete_edge')    # , *args, **kwargs)
        return r

    def add_edges(self, *args, **kwargs):
        r = Graph.add_edges(self, *args, **kwargs)
        self.notify_change('add_vertices')    # , *args, **kwargs)
        return r

    def notify_change(self, s):
        """
        The function called whenever a vertex or edge deletion or addition is
        made.

        By default empty, this function can be specified when creating a new
        instance
        """
        return
