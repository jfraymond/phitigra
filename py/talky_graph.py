from sage.graphs.graph import Graph, DiGraph

'''
A class to add notifications to the class Graph and DiGraph when vertices and
edges are added or deleted.
'''


class TalkyGraph(Graph):
    '''
    Add notification for created or deleted edges or vertices of a
    sage ``Graph``.
    '''
    def __init__(self, *args, **kwargs):
        notify = kwargs.pop('notify_callback', lambda x:None)
        super().__init__(*args, **kwargs)
        # We define notify_change after the call to Graph's constructor so that
        # no notification (asking to redraw the graph) is done until the graph
        # is completely built
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
        '''
        The function called whenever a vertex or edge deletion or addition is
        made.

        By default empty, this function can be specified when creating a new
        instance
        '''
        return
