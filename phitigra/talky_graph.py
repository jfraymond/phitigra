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
    Subclass of Sage's :class:`Graph` class that behaves exactly the same,
    except that a callback is called when changes are made to the instance
    (addition or deletion of vertices or edges).

    EXAMPLES:

    Here we define a graph with a callback that prints a notification when
    a change is made::

        sage: def f(*s, **t): print("Notification: " + str(s))
        sage: g = TalkyGraph(notify_callback=f)
        sage: g.add_vertex(0)
        Notification: ('add_vertex', 0)
        sage: g.add_vertex()
        Notification: ('add_vertex',)
        1
        sage: g.add_edge(0, 1)
        Notification: ('add_edge', 0, 1)
        sage: g.delete_vertex(1)
        Notification: ('delete_vertex', 1)

    The default callback is the function that does nothing::
 
        sage: h = TalkyGraph()
        sage: h.add_vertex()
        0

    TESTS:

    The construction of the graph does not trigger any notification::

        sage: def f(*s, **t): print("Hello!")
        g = TalkyGraph(2, notify_callback=f); g
        Graph on 2 vertices
    """

    def __init__(self, *args, **kwargs):
        # Get the callback if given and use a no-op function otherwise
        notify = kwargs.pop('notify_callback', lambda x:None)
        super().__init__(*args, **kwargs)

        # notify_change refers to the callback that functions modifying
        # the graph will call. We define it after the call to Graph's
        # constructor so that no notification is done until the graph is
        # completely built:
        self.notify_change = notify

    def _repr_(self):
        """
        Return a string representation of the graph.

        EXAMPLES::

            sage: g = TalkyGraph(5); g._repr_()
            TalkyGraph over a Graph on 5 vertices
            sage: g = TalkyGraph(graphs.PetersenGraph()); g._repr_()
            TalkyGraph over a Petersen graph: Graph on 10 vertices
        """
        return "TalkyGraph over a " + Graph._repr_(self)

    def add_vertex(self, *args, **kwargs):
        r"""
        Create an isolated vertex.

        Same as :meth:`Graph.add_vertex` but followed by a call to
        :meth:`notify_change`.

        TESTS::

            sage: def f(*s, **t): print("The graph changed: " + str(s))
            sage: g = TalkyGraph(notify_callback=f)
            sage: g.add_vertex(0)
            The graph changed: ('add_vertex', 0)
            sage: g.add_vertex()
            The graph changed: ('add_vertex',)
            1
        """
        r = Graph.add_vertex(self, *args, **kwargs)
        self.notify_change('add_vertex', *args, **kwargs)
        return r

    def delete_vertex(self, *args, **kwargs):
        r"""
        Delete vertex, removing all incident edges.

        Same as :meth:`Graph.delete_vertex` but followed by a call to
        :meth:`notify_change`.

        TESTS::

            sage: def f(*s, **t): print("The graph changed: " + str(s))
            sage: g = TalkyGraph(2, notify_callback=f)
            sage: g.delete_vertex(1)
            The graph changed: ('delete_vertex', 1)
            sage: g.delete_vertex(1)
            Traceback (most recent call last):
            ...
            ValueError: vertex (1) not in the graph
        """
        r = Graph.delete_vertex(self, *args, **kwargs)
        self.notify_change('delete_vertex', *args, **kwargs)
        return r

    def add_vertices(self, *args, **kwargs):
        r"""
        Delete vertex, removing all incident edges.

        Same as :meth:`Graph.delete_vertex` but followed by a call to
        :meth:`notify_change`.

        TESTS::
        
            sage: def f(*s, **t): print("The graph changed: " + str(s))
            sage: g = TalkyGraph(2, notify_callback=f)
            sage: g.add_vertices([1,2])
            The graph changed: ('add_vertices', [1,2])
            sage: g.add_vertices([None, 3, None])
            The graph changed: ('add_vertices', [None, 3, None])
            [0, 4]
        """
        r = Graph.add_vertices(self, *args, **kwargs)
        self.notify_change('add_vertices', *args, **kwargs)
        return r

    def delete_vertices(self, *args, **kwargs):
        r"""
        Delete vertices from the (di)graph taken from an iterable container of
        vertices.

        Same as :meth:`Graph.delete_vertices` but followed by a call to
        :meth:`notify_change`.

        TESTS::
        
            sage: def f(*s, **t): print("The graph changed: " + str(s))
            sage: g = TalkyGraph(5, notify_callback=f)
            sage: g.delete_vertices([1,2])
            The graph changed: ('delete_vertices', [1,2])
            sage: g.delete_vertices([1, 3])
            Traceback (most recent call last):
            ...
            ValueError: vertex (1) not in the graph
        """
        r = Graph.delete_vertices(self, *args, **kwargs)
        self.notify_change('delete_vertices', *args, **kwargs)
        return r

    def add_edge(self, *args, **kwargs):
        r"""
        Add an edge between two vertices.

        Same as :meth:`Graph.add_edge` but followed by a call to
        :meth:`notify_change`.

        TESTS::
        
            sage: def f(*s, **t): print("Change: " + str(s) + " " + str(t))
            sage: g = TalkyGraph(5, notify_callback=f)
            sage: g.add_edge(1, 2)
            Change: ('add_edge', 1, 2) 
            sage: g.add_edge(1, 42, label='hello')
            Change: ('add_edge', 0, 42) {'label': 'hello'}
        """
        r = Graph.add_edge(self, *args, **kwargs)
        self.notify_change('add_edge', *args, **kwargs)
        return r

    def delete_edge(self, *args, **kwargs):
        r"""
        Delete the edge between two vertices.

        Same as :meth:`Graph.delete_edge` but followed by a call to
        :meth:`notify_change`.

        TESTS::
        
            sage: def f(*s, **t): print("Change: " + str(s) + " " + str(t))
            sage: g = TalkyGraph(graphs.PetersenGraph(), notify_callback=f)
            sage: g.delete_edge(0, 1)
            Change: ('delete_edge', 0, 1)
            sage: g.num_edges()
            14
            sage: g.delete_edge(0, 9)
            Change: ('delete_edge', 0, 9)
            sage: g.num_edges()
            14
        """
        r = Graph.delete_edge(self, *args, **kwargs)
        self.notify_change('delete_edge', *args, **kwargs)
        return r

    def add_edges(self, *args, **kwargs):
        r"""
        Add edges from an iterable container.

        Same as :meth:`Graph.add_edges` but followed by a call to
        :meth:`notify_change`.

        TESTS::
        
            sage: def f(*s, **t): print("Change: " + str(s))
            sage: g = TalkyGraph(10, notify_callback=f)
            sage: g.add_edges([(3, 0), (4, 1), (5, 2)])
            Change: ('add_edges', [(3, 0), (4, 1), (5, 2)])
        """
        r = Graph.add_edges(self, *args, **kwargs)
        self.notify_change('add_vertices', *args, **kwargs)
        return r

    def notify_change(self, *args, **kwargs):
        """
        The function called whenever a vertex or edge deletion or addition is
        made.

        By default empty, this function can be specified when creating a new
        instance.

        TESTS::
            sage: g = TalkyGraph(1)
            sage: g.add_vertex()
            0
        """
        return
