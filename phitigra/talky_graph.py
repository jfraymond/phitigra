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

from sage.graphs.graph import Graph


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

        sage: h = TalkyGraph()
        sage: h.add_vertex()
        0
    """

    def __init__(self, *args, **kwargs):
        notify = kwargs.pop('notify_callback', lambda x:None)
        super().__init__(*args, **kwargs)
        # We define notify_change after the call to Graph's constructor so that
        # no notification is done until the graph is completely built
        self.notify_change = notify

    def add_vertex(self, *args, **kwargs):
        r = Graph.add_vertex(self, *args, **kwargs)
        self.notify_change('add_vertex')    # , *args, **kwargs)
        return r

    def delete_vertex(self, *args, **kwargs):
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
