r"""
Graph editor for sage on jupyter

A simple graph editor where one can see the graph, add vertices/edges,
etc.

EXAMPLES::

    sage: from phitigra import SimpleGraphEditor
    sage: ed = SimpleGraphEditor(graphs.RandomGNP(10, 0.5))
    sage: ed.show() # random
    # Now you can play with the graph!

AUTHORS:

- Jean-Florent Raymond (2020-04-05): initial version
"""

# ***********************************************************************
#     Copyright (C) 2020 Jean-Florent Raymond <j-florent.raymond@uca.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ***********************************************************************

from ipycanvas import MultiCanvas, hold_canvas
from ipywidgets import (Label, BoundedIntText, VBox, HBox, Output, Button,
                        Dropdown, ColorPicker, ToggleButton,
                        Layout, ToggleButtons)
from random import randint, randrange
from math import pi, sqrt, atan2
from copy import copy

from sage.graphs.all import Graph
from sage.matrix.constructor import matrix
from sage.modules.free_module_element import vector


class SimpleGraphEditor():
    """
    Base class for the graph editor.
    """

    # Output widget used to print error messages (for debug)
    output = Output()

    @staticmethod
    def draw_arrow(canvas):
        """
        Draw an arrow at with tip at (0,0), pointing to the left.

        Used when drawing directed graphs.
        """
        a_x = 15  # Length of the arrow
        a_y = 8   # Half-width of the arrow
        canvas.begin_path()
        canvas.move_to(0, 0)
        canvas.line_to(a_x, a_y)
        canvas.line_to(0.75*a_x, 0)
        canvas.line_to(a_x, -a_y)
        canvas.move_to(0, 0)
        canvas.fill()

    def __init__(self, G=Graph(0), drawing_parameters=dict()):
        """
        Prepare the widget with the given graph.

        The graph should not allow loops neither multiedges.
        In this function the properties of vertices and eges (width, color)
        are initialized and the elements of the graph editor (widgets, canvas,
        callbacks) are defined.

        INPUT:

        - ``G`` -- graph from :class:`Graph` or :class:`DiGraph` that does not
          allow loops neither multiedges (default: `Graph(0)`); the graph to
          plot and edit.

        - ``drawing_parameters`` -- dictionary (default: `{}`); the
          parameters to use for the drawing, which are `'width'`,
          `'height'`, `'default_radius'` (for vertex shapes),
          `'default_vertex_color'` (for drawing the vertice initially in
          the graph), and `'default_edge_color'`.

        OUTPUT: a graph editor widget

        EXAMPLES:

            sage: from phitigra import SimpleGraphEditor
            sage: param = {'width': 200, 'height': 200}
            sage: ed = SimpleGraphEditor(graphs.PetersenGraph(),drawing_parameters=param)
            sage: type(e)
            <class 'phitigra.simple_editor.SimpleGraphEditor'>

            sage: g = Graph(0)
            sage: g.allow_multiple_edges(True)
            sage: SimpleGraphEditor(g)
            Traceback (most recent call last):
            ...
            ValueError: Cannot deal with graphs that allow loops or multiple edges

        """

        if G.allows_multiple_edges() or G.allows_loops():
            raise ValueError("Cannot deal with graphs that allow"
                             " loops or multiple edges")

        self.graph = G

        # Define the default drawing parameters and update them
        # with the provided parameters (if any)

        # Default parameters
        self.drawing_parameters = {
            # Sizes of the widget
            'width': 600,
            'height': 400,
            # Defaults for drawing vertices
            'default_radius': 20,
            'default_vertex_color': None,
            'default_edge_color': 'black'
        }

        # Take into account the provided drawing parameters (if any)
        self.drawing_parameters.update(drawing_parameters)

        # The layout (+6 to account for the 3px border on both sides)
        lyt = {'border': '3px solid lightgrey',
               'width': str(self.drawing_parameters['width'] + 6) + 'px',
               'height': str(self.drawing_parameters['height'] + 6) + 'px',
               'overflow': 'visible'}
        
        # The canvas where to draw
        self.multi_canvas = (
            MultiCanvas(2,
                        width=self.drawing_parameters['width'],
                        height=self.drawing_parameters['height'],
                        sync_image_data=True,
                        layout=lyt)
        )

        # It consists in two layers
        self.canvas = self.multi_canvas[0]    # The main layer
        # The layer where we draw objects in interaction
        # (moved vertices, etc.):
        self.interact_canvas = self.multi_canvas[1]

        self.selected_vertices = set()
        self.selected_edges = set()
        self.dragged_vertex = None
        self.dragging_canvas_from = None

        # Registering callbacks for mouse interaction on the canvas
        self.interact_canvas.on_mouse_down(self.mouse_down_handler)
        self.interact_canvas.on_mouse_move(self.mouse_move_handler)
        self.interact_canvas.on_mouse_up(self.mouse_up_handler)
        # When the mouse leaves the canvas, we free the node that
        # was being dragged, if any:
        self.interact_canvas.on_mouse_out(self.mouse_up_handler)

        # The widgets of the graph editor (besides the canvas):

        # Where to display messages:
        self.text_output = Label("Graph Editor", layout={'width': '100%'})
        # Data about the graph:
        self.text_graph = Label("", layout={'width': '100%'})

        # The drawing tools
        self.tool_selector = ToggleButtons(
            options=['select / move',
                     'add vertex or edge',
                     'delete vertex or edge',
                     'add walk',
                     'add clique',
                     'add star'],
            description='',
            disabled=False,
            button_style='',
            tooltips=['Move vertices or the canvas',
                      'Add vertices or edges',
                      'Delete vertices or edges',
                      'Add a walk through new or existing vertices',
                      'Add a clique through new or existing vertices',
                      'Add a star through new or existing vertices'],
            icons=['']*5,
            layout={'width': '150px', "margin": "0px 2px 0px auto"}
        )
        # We unselect any possibly selected vertex when the currrent
        # tool is changed, in order to avoid problems with the deletion
        # tool
        self.tool_selector.observe(lambda _: self.tool_selector_callback())
        self.current_tool = lambda: self.tool_selector.value

        # Selector to change layout
        self.layout_selector = Dropdown(
            options=[('- change layout -', '- change layout -'),
                     ('random', 'random'),
                     ('spring', 'spring'),
                     ('circular', 'circular'),
                     ('planar', 'planar'),
                     ('forest (root up)', 'forest (root up)'),
                     ('forest (root down)', 'forest (root down)'),
                     ('directed acyclic', 'acyclic')],
            value='- change layout -',
            description='',
            layout={'width': '150px', "margin": "1px 2px 1px auto"}
        )
        self.layout_selector.observe(self.layout_selector_callback)

        # Buttons to rescale:
        self.zoom_in_button = Button(description='',
                                     disabled=False,
                                     button_style='',
                                     tooltip='Zoom in',
                                     icon='search-plus',
                                     layout={'height': '36px',
                                             'width': '36px',
                                             'margin': '0px 1px 0px 0px'})
        self.zoom_in_button.on_click(lambda x: (self._scale_layout(1.5),
                                                self._draw_graph()))
        self.zoom_to_fit_button = Button(description='',
                                         disabled=False,
                                         button_style='',
                                         tooltip=('Zoom to fit'),
                                         icon='compress',
                                         layout={'height': '36px',
                                                 'width': '36px',
                                                 'margin': '0px 1px 0px 1px'})
        self.zoom_to_fit_button.on_click(lambda x: (self._normalize_layout(),
                                                    self._draw_graph()))
        self.zoom_out_button = Button(description='',
                                      disabled=False,
                                      button_style='',
                                      tooltip='Zoom out',
                                      icon='search-minus',
                                      layout={'height': '36px',
                                              'width': '36px',
                                              'margin': '0px 1px 0px 1px'})
        self.zoom_out_button.on_click(lambda x: (self._scale_layout(2/3),
                                                 self._draw_graph()))

        # To clear the drawing
        self.clear_drawing_button = Button(description="",
                                           disabled=False,
                                           button_style='',
                                           tooltip=('Clear the drawing and '
                                                    'delete the graph'),
                                           icon='trash',
                                           layout={'height': '36px',
                                                   'width': '36px',
                                                   'margin': ('0px 0px '
                                                              '0px 1px')})
        self.clear_drawing_button.on_click(self.clear_drawing_button_callback)

        # Selector to change the color of the selected vertex
        self.color_selector = ColorPicker(
            concise=False,
            description='',
            value='#437FC0',
            disabled=False,
            layout={'height': '36px',
                    'width': '112px',
                    'margin': '0px 1px 0px 0px'}
        )
        self.color_button = Button(description='',
                                   disabled=False,
                                   button_style='',
                                   tooltip=('Apply color to the '
                                            'selected elements'),
                                   icon='paint-brush',
                                   layout={'height': '36px',
                                           'width': '36px',
                                           'margin': '0px 0px 0px 1px'})
        self.color_button.on_click((lambda x: self.color_button_callback()))

        self.vertex_radius_box = BoundedIntText(
            value=self.drawing_parameters['default_radius'],
            min=1,
            max=100,
            step=1,
            description="",
            disabled=False,
            layout={'width': '90px',
                    'margin': 'auto 1px auto 0px'}
        )
        self.radius_button = Button(description='',
                                    disabled=False,
                                    button_style='',
                                    tooltip=('Change the radius of the '
                                             'selected vertices'),
                                    icon='expand',
                                    layout={'height': '36px',
                                            'width': '36px',
                                            'margin': '0px 0px 0px 1px'})
        self.radius_button.on_click((lambda x: self.radius_button_callback()))

        self.vertex_name_toggle = ToggleButton(
            value=True,
            description='Show vertex labels',
            disabled=False,
            button_style='',
            tooltip='Should the vertex label be drawn?',
            icon='',
            layout={"width": "150px", "margin": "1px 2px 1px auto"}
        )
        self.vertex_name_toggle.observe(lambda _: self._draw_graph())

        # A 'next' button to call a custom function
        self.next_button = Button(description='Next',
                                  disabled=False,
                                  button_style='',
                                  tooltip=('Call a custom function. Define it'
                                           ' via the \'set_next_callback\''
                                           ' method.'),
                                  icon='forward',
                                  layout={"width": "150px",
                                          "margin": "1px 2px 0px auto"})

        # The final widget, which contains all the parts defined above
        self.widget = HBox([VBox([self.multi_canvas,
                                  HBox([self.text_graph, self.text_output]),
                                  self.output]),
                            VBox([
                                self.tool_selector,
                                self.layout_selector,
                                HBox([self.zoom_in_button,
                                      self.zoom_to_fit_button,
                                      self.zoom_out_button,
                                      self.clear_drawing_button],
                                     layout=Layout(margin="1px 2px 1px auto")),
                                HBox([self.color_selector, self.color_button],
                                     layout=Layout(margin="1px 2px 1px auto")),
                                HBox([Label(value='⌀',
                                            layout={'margin': ('auto '
                                                               '2px auto 0px')
                                                    }),
                                      self.vertex_radius_box,
                                      self.radius_button],
                                     layout=Layout(margin="1px 2px 1px auto")),
                                self.vertex_name_toggle,
                                self.next_button],
                                 layout=Layout(min_width='160px',
                                               width="160px"))
                            ], layout=Layout(width='100%',
                                             height='auto',
                                             overflow='auto hidden'))

        # Prepare the graph data

        # Radii, positions and colors of the vertices or edges on the drawing
        self.vertex_radii = dict()
        self.vertex_radii = {v: self.drawing_parameters['default_radius']
                             for v in self.graph.vertex_iterator()}

        if self.drawing_parameters['default_vertex_color'] is None:
            self.colors = {v: f"#{randrange(0x1000000):06x}"    # Random color
                           for v in self.graph.vertex_iterator()}
        else:
            self.colors = {v: self.drawing_parameters['default_vertex_color']
                           for v in self.graph.vertex_iterator()}

        self.edge_colors = {e: 'black'
                            for e in self.graph.edge_iterator(labels=False)}

        if self.graph.get_pos() is None:
            # The graph has no predefined positions: we pick some
            self._random_layout()

        # The transformation matrix recording all transformations
        # done to the graph drawing
        # There is a "-1" because when drawing, the y-axis goes downwards
        # see :wikipedia:Transformation_matrix#Affine_transformations
        self._transform_matrix = matrix([[1, 0, 0],
                                         [0, -1, 0],
                                         [0, 0, 1]])

        # Update the transform matrix so that the vertex position
        # fit the canvas
        self._normalize_layout()

        self._draw_graph()
        self.text_graph_update()

    def show(self):
        """
        Return the editor widget.
        
        TESTS::

            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor()
            sage: w = ed.show()
            sage: type(w)
            <class 'ipywidgets.widgets.widget_box.HBox'>
        """
        return self.widget

    # Getters and setters

    def get_graph(self):
        """
        Return a copy of the drawn graph.

        EXAMPLES:

        The returned graph is different from that of the editor:

            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(graphs.PetersenGraph())
            sage: g = ed.get_graph()
            sage: g.delete_vertex(0)
            sage: (len(g), len(ed.graph))
            (9, 10)
        """
        return copy(self.graph)

    def _get_radius(self, v):
        """
        Return the radius of a vertex.

        If the radius of v has not been set, return the default radius.

        EXAMPLES:
        
            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(graphs.PetersenGraph(), drawing_parameters={'default_radius': 41})
            sage: ed.vertex_radius(0)
            41
            sage: ed.set_vertex_radius(0, 42)
            sage: ed.vertex_radius(0)
            42
        """
        return self.vertex_radii.get(v,
                                     self.drawing_parameters['default_radius'])

    def set_vertex_radius(self, v, radius=None):
        """
        Set the radius of a vertex shape.

        If ``radius`` is ``None``, use the radius in the radius box.

        WARNING: this function does not redraw the graph.
        
        EXAMPLES:
        
            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(graphs.PetersenGraph(), drawing_parameters={'default_radius': 41})
            sage: ed.vertex_radius(0)
            41
            sage: ed.set_vertex_radius(0, 42)
            sage: ed.vertex_radius(0)
            42

        TESTS::

        Behavior when no radius is provided:

            sage: ed.set_vertex_radius(0)
            sage: ed.vertex_radius(0) == self.vertex_radius_box.value
            True
        """
        if radius is None:
            self.vertex_radii[v] = self.vertex_radius_box.value
        else:
            self.vertex_radii[v] = radius

    def get_vertex_color(self, v):
        """
        Get the color of a vertex.

        EXAMPLES:
        
        Colors can be given as named colors or hex values:

            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(Graph(1))
            sage: ed.set_vertex_color(0, 'blue')
            sage: ed.get_vertex_color(0)
            'blue'
            sage: ed.set_vertex_color(0, '#fff')
            sage: ed.get_vertex_color(0)
            '#fff'
        """
        return self.colors[v]

    def set_vertex_color(self, v, color=None):
        """
        Set the color of a vertex.

        If ``color`` is ``None``, use the color of the color selector.

        WARNING: this function does not redraw the graph.

        EXAMPLES:
        
        Colors can be given as named colors or hex values:

            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(Graph(1))
            sage: ed.set_vertex_color(0, 'blue')
            sage: ed.get_vertex_color(0)
            'blue'
            sage: ed.set_vertex_color(0, '#fff')
            sage: ed.get_vertex_color(0)
            '#fff'

        TESTS::

        Behavior when no color is provided:

            sage: ed = SimpleGraphEditor(Graph(1))
            sage: ed.set_vertex_color(0)
            sage: ed.get_vertex_color(0) == self.color_selector.value
            True
        """
        if color is None:
            self.colors[v] = self.color_selector.value
        else:
            self.colors[v] = color

    def get_edge_color(self, e):
        """
        Return the color of an edge.

        EXAMPLES:
        
        Edge colors for undirected graphs:

            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(graphs.PetersenGraph())
            sage: ed.set_edge_color((1, 6), '#123456')
            sage: ed.get_edge_color((1, 6))
            '#123456'
            sage: ed.get_edge_color((6, 1))
            '#123456'
            sage: ed.get_edge_color((6, 1, 'label'))
            '#123456'
            sage: ed.get_edge_color((5, 9))
            Traceback (most recent call last):
            ...
            KeyError: (5, 9)

        Edge colors for directed graphs:

            sage: ed = SimpleGraphEditor(digraphs.Circuit(4))
            sage: ed.set_edge_color((0, 1), '#123456')
            sage: ed.get_edge_color((0, 1))
            '#123456'
            sage: ed.get_edge_color((1, 0))
            Traceback (most recent call last):
            ...
            KeyError: (1, 0)
        """

        u, v, *_ = e
        try:
            c = self.edge_colors[(u, v)]
        except KeyError:
            if not self.graph.is_directed():
                c = self.edge_colors[(v, u)]
            else:
                raise

        return c

    def set_edge_color(self, e, color=None):
        """
        Set the color of an edge.

        If ``color`` is ``None``, use the default color.
        Raise an exception if the edge does not belong to the graph.
        See :meth:`get_edge_color` for examples.
        
       .. WARNING:: this function does not redraw the graph.

        TESTS:

            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(graphs.PetersenGraph())
            sage: ed.set_edge_color((1, 6)
            sage: ed.get_edge_color((1,6)) == self.drawing_parameters['default_edge_color']
            True
            sage: ed.set_edge_color((1,5))
            Traceback (most recent call last):
            ...
            ValueError: edge (1, 5) does not belong to the graph
        """
        
        u, v, *_ = e
        if color is None:
            color = self.drawing_parameters['default_edge_color']

        if not self.graph.has_edge(e):
            raise ValueError("edge " + str(e) + " does not belong to the graph")

        if (u, v) in self.edge_colors.keys():
            self.edge_colors[(u, v)] = color
        else:
            self.edge_colors[(v, u)] = color

    def _get_coord_on_canvas(self, x, y):
        """
        Return the coordinates on the canvas corresponding to the
        coordinates `x` and `y` in the basis where the graph positions
        are stored.

        These coordinates are obtained from the coordinates from
        ``Graph.get_pos`` by applying the transformations stored in
        ``self._transform_matrix`` and casting to integer.

        .. WARNING::

            The output coordinates do not necessarily belong to the
            canvas range. They are just the coordinates of ``(x,y)``
            translated and scaled using ``self._transform_matrix``,
            so they can be negative or over the canvas width/height.

        TESTS::
        
            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(Graph(1))
            sage: ed._set_vertex_pos(0, 50, 50)
            sage: x, y = ed.graph.get_pos()[0]
            sage: cx, cy = ed._get_coord_on_canvas(x, y)
            sage: abs(cx - 50) < 2 and abs(cy - 50) < 2
            True
        """

        m = self._transform_matrix * matrix([[x], [y], [1]])
        return int(m[0][0]), int(m[1][0])  # New x and y

    def _get_vertex_pos(self, v):
        """
        Return the vertex coordinates on the canvas.

        See :meth:`_get_coord_on_canvas` for details.

        TESTS::

            sage: ed = SimpleGraphEditor(Graph(1))
            sage: ed._set_vertex_pos(0, 50, 50)
            sage: x, y = ed._get_vertex_pos(0)
            sage: abs(x - 50) < 2 and abs(y - 50) < 2
            True
        """
        x, y = self.graph.get_pos()[v]

        return self._get_coord_on_canvas(x, y)

    def _get_vertices_pos(self):
        """
        Return a dictionary of the coordinates of the vertices on the
        canvas.

        See :meth:`_get_coord_on_canvas` for details.

        TESTS::

            Interesting tests are actually done in :meth:`_get_coord_on_canvas`.

            sage: ed = SimpleGraphEditor(graphs.PetersenGraph())
            sage: d = ed._get_vertices_pos()
            sage: type(d)
            <class 'dict'>
            sage: len(d) == len(ed.graph)
            True
        """

        graph_pos = self.graph.get_pos()
        canvas_pos = {v: self._get_coord_on_canvas(*graph_pos[v])
                      for v in self.graph}
        return canvas_pos

    def _set_vertex_pos(self, v, x, y):
        """
        Set the position of a vertex.

        The arguments ``x`` and ``y`` denote the position on the canvas
        (in pixel) where the vertex ``v`` should be placed.
        These values are translated and scaled using the inverse of
        ``self._transform_matrix`` before being stored.

        TESTS::

        Same as in :meth:`_get_vertex_pos`.

            sage: ed = SimpleGraphEditor(Graph(1))
            sage: ed._set_vertex_pos(0, 50, 50)
            sage: x, y = ed._get_vertex_pos(0)
            sage: abs(x - 50) < 2 and abs(y - 50) < 2
            True
        """

        pos = self.graph.get_pos()
        if pos is None:
            pos = dict()
            self.graph.set_pos(pos)

        m = self._transform_matrix.inverse() * matrix([[x], [y], [1]])
        pos[v] = [m[0][0], m[1][0]]

    def _get_vertex_at(self, x, y):
        """
        Return which vertex is drawn at (x,y).

        Actually return the vertex whose shape contains `(x,y)` and whose
        center is the closest to `(x,y)`.
        Return `None` if no vertex shape contains `(x,y)`.

        EXAMPLES:

            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(Graph(2), drawing_parameters={'default_radius': 20})
            sage: ed._set_vertex_pos(0, 50, 50)
            sage: ed._set_vertex_pos(1, 70, 50)
            sage: ed._get_vertex_at(55, 50)
            0
            sage: ed._get_vertex_at(65, 50)
            1
            sage: ed._get_vertex_at(60, 25)
            None
        """

        canvas_pos = self._get_vertices_pos()

        min_dist = self.drawing_parameters['width']  # aka infinity
        arg_min = None

        for v in self.graph.vertex_iterator():
            v_x, v_y = canvas_pos[v]
            radius = self._get_radius(v)

            d_x = abs(x - v_x)
            d_y = abs(y - v_y)
            if (d_x < radius and d_y < radius):
                # The user clicked close to vertex v (approximatively)!
                d = sqrt(d_x*d_x + d_y*d_y)
                if d <= radius and d < min_dist:
                    min_dist = d
                    arg_min = v

        return arg_min

    def _get_edge_at(self, x, y):
        """
        Return the closest edge near the point with coordinates (x,y).

        Return `None` if no edge is close enough to (x,y).

        .. WARNING::
            This function assumes that edges are straigh lines between
            their endpoints.

        EXAMPLES:
        
            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(graphs.PathGraph(3))
            sage: ed._set_vertex_pos(0, 50, 50)
            sage: ed._set_vertex_pos(1, 50, 100)
            sage: ed._set_vertex_pos(2, 100, 100)
            sage: ed._set_vertex_pos(3, 100, 50)
            sage: ed._get_edge_at(50, 75)
            (0, 1)
            sage: ed._get_edge_at(51, 75)
            (0, 1)
            sage: ed._get_edge_at(75, 100)
            (1, 2)
            sage: ed._get_edge_at(52, 98)
            (1, 2)
        """

        def sqnorm(a, b):
            # Square of the norm
            # (to avoid computing square roots)
            d = [a[0] - b[0], a[1] - b[1]]
            return d[0] * d[0] + d[1] * d[1]

        canvas_pos = self._get_vertices_pos()

        min_dist = 10  # We don't want edges too far from the click
        closest_edge = None

        p = vector([x, y])

        for e in self.graph.edge_iterator():
            u, v, *_ = e

            pv = vector(canvas_pos[v])
            pu = vector(canvas_pos[u])

            if (x < min(pv[0], pu[0]) - 10 or
                    x > max(pv[0], pu[0]) + 10 or
                    y < min(pv[1], pu[1]) - 10 or
                    y > max(pv[1], pu[1]) + 10):
                # In the expression above it is important to keep slack
                # (10) in order to deal with horizontal or vertical edges
                continue

            t = (p - pv).dot_product(pu - pv) / sqnorm(pv, pu)
            proj = pv + t * (pu - pv)
            d = sqnorm(proj, p)
            if d < min_dist:
                min_dist = d
                if self.graph.has_edge(u, v):
                    # Case distinction to deal with digraphs
                    closest_edge = (u, v)
                else:
                    closest_edge = (v, u)
        return closest_edge

    ##########
    # Layout #
    ##########

    def _random_layout(self):
        """
        Randomly pick and set positions for the vertices.

        Coordinates are integers chosen between 0 and the square of the
        order of the graph.

        TESTS::

            sage: ed = SimpleGraphEditor(graphs.PathGraph(3))
            sage: self._random_layout()
            sage: self.graph.get_pos(1) >= 0 and self.graph.get_pos(1) <= 9
            True
        """
        n = self.graph.order()
        n2 = n*n
        rnd_pos = {v: (randint(0, n2),
                       randint(0, n2))
                   for v in self.graph.vertex_iterator()}
        self.graph.set_pos(rnd_pos)

    def _normalize_layout(self):
        """
        Redefines the transformation matrix so that the graph drawing
        fits well the canvas.

        ``x`` and ``y`` coordinates are scaled by the same factor and
        the graph is centered.

        TESTS::

            sage: ed = SimpleGraphEditor(Graph(5), drawing_parameters={'width': 101, height: 101})
            sage: ed._set_vertex_pos(0, 10, 10)
            sage: ed._set_vertex_pos(1, 5, 10)
            sage: ed._set_vertex_pos(2, 15, 10)
            sage: ed._set_vertex_pos(3, 10, 8)
            sage: ed._set_vertex_pos(4, 10, 12)
            sage: ed._normalize_layout()
            sage: d = ed._get_vertices_pos()
            sage: d[0] == (50, 50)
            True
            sage: d[1][0] < 6
            True
            sage: d[3][1] >= 6
            True
        """

        if not self.graph:
            # There is nothing to do with the one vertex graph
            return

        pos = self.graph.get_pos()

        # Etrema for vertex centers
        x_min = min(pos[v][0] for v in self.graph)
        x_max = max(pos[v][0] for v in self.graph)
        y_min = min(pos[v][1] for v in self.graph)
        y_max = max(pos[v][1] for v in self.graph)

        x_range = max(x_max - x_min, 0.1)  # max to avoid division by 0
        y_range = max(y_max - y_min, 0.1)

        # We keep some margin on the sides

        margin = max((self._get_radius(v)
                      for v in self.graph.vertex_iterator())) + 5

        target_width = self.multi_canvas.width - 2 * margin
        target_height = self.multi_canvas.height - 2 * margin
        # Some computations to decide of the scaling factor in order to
        # simultaneously fill the canvas on at least one axis range and
        # keep proportions, and to center the image
        factor_x = target_width / x_range
        factor_y = target_height / y_range

        factor = min(factor_x, factor_y)
        x_shift = margin + (target_width - x_range * factor) / 2
        y_shift = margin + (target_height - y_range * factor) / 2

        # See :wikipedia:Transformation_matrix#Affine_transformations
        translate_to_origin = matrix([[1, 0, -x_min],
                                      [0, 1, -y_min],
                                      [0, 0, 1]])
        scale_to_canvas_size = matrix([[factor, 0,      0],
                                       [0,      factor, 0],
                                       [0,      0,      1]])
        translate_to_center = matrix([[1, 0, x_shift],
                                      [0, 1, y_shift],
                                      [0, 0, 1]])

        self._transform_matrix = (translate_to_center
                                  * scale_to_canvas_size
                                  * translate_to_origin)

    def _scale_layout(self, ratio):
        """
        Rescale the vertices coordinates around the center of the image
        and with respect to the given ratio.

        This is done by updating the transform matrix.

        TESTS::
        
            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(Graph(5), drawing_parameters={'width': 101, 'height': 101})
            sage: ed._set_vertex_pos(0, 50, 50)
            sage: ed._set_vertex_pos(1, 30, 50)
            sage: ed._set_vertex_pos(2, 70, 50)
            sage: ed._set_vertex_pos(3, 50, 30)
            sage: ed._set_vertex_pos(4, 50, 70)
            sage: ed._scale_layout(1.5)
            sage: x, y = ed._get_vertex_pos(0)
            sage abs(x - 50) <= 1 and abs(y - 50) <= 1
            True
            sage: ed._get_vertex_pos(1)[0] <= 21
            True
            sage: abs(ed._get_vertex_pos(1)[1] - 50) <= 1
            True
        """

        x_shift = self.multi_canvas.width * (1 - ratio) / 2
        y_shift = self.multi_canvas.height * (1 - ratio) / 2

        scale_and_center = matrix([[ratio, 0,     x_shift],
                                   [0,     ratio, y_shift],
                                   [0,     0,     1]])
        self._transform_matrix = scale_and_center * self._transform_matrix

    def _translate_layout(self, vec):
        """
        Translate the vertices coordinates.

        This is done by updating the transform matrix.
        
        TESTS::
        
            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(Graph(1))
            sage: ed._set_vertex_pos(0, 50, 50)
            sage: ed._translate_layout((25, 25))
            sage: x, y = ed._get_vertex_pos(0)
            sage: x, y == (75, 75)
            True
        """

        x_shift, y_shift = vec
        translate = matrix([[1, 0, x_shift],
                            [0, 1, y_shift],
                            [0, 0, 1]])
        self._transform_matrix = translate * self._transform_matrix

    #########################
    # Text output functions #
    #########################

    def output_text(self, text):
        """
        Write the input string in the textbox of the editor.
        
        TESTS::
        
            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(Graph(1))
            sage: ed.output_text("Hello world!")
            sage: ed.text_output.value == "Hello world!"
            True
        """

        self.text_output.value = text

    def text_graph_update(self):
        """Update the caption with data about the graph.

        TESTS::
        
            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(graphs.PetersenGraph())
            sage: print(ed.text_graph.value)
            Graph on 10 vertices and 15 edges.
        """

        self.text_graph.value = ("Graph on " + str(self.graph.order())
                                 + " vertices and "
                                 + str(self.graph.num_edges())
                                 + " edges.")

    ######################
    # Graph modification #
    ######################

    def add_vertex_at(self, x, y, name=None, color=None):
        """
        Add a vertex to a given position, color it and draw it.

        If ``color`` is ``None``, use the current color of the color
        picker.
        The return value is the same as with
        :meth:`~GenericGraph.add_vertex`.

        TESTS::

            sage: ed = SimpleGraphEditor(Graph(0))
            sage: ed.add_vertex_at(10, 42, name="vert", color='#112233')
            sage: v=next(ed.graph.vertex_iterator())
            sage: v
            'vert'
            sage: ed.get_vertex_pos(v)
            (10, 42)
            sage: ed.colors[v]
            '#112233'
            sage: ed.add_vertex_at(20, 20)
            0
        """

        if name is None:
            name = self.graph.add_vertex()
            return_name = True
        else:
            self.graph.add_vertex(name)
            return_name = False

        self._set_vertex_pos(name, x, y)
        self.set_vertex_color(name, color)
        self.set_vertex_radius(name)

        self._draw_vertex(name)
        self.text_graph_update()

        # Return the vertex name if it was not specified,
        # as the graph add_vertex function:
        if return_name:
            return name

    def add_edge(self, u, v, label=None, color=None):
        """
        Add an edge between two vertices and draw it

        If ``color`` is ``None``, use the default color.

        TESTS::

            sage: ed = SimpleGraphEditor(Graph(['u', 'v']))
            sage: ed.graph.has_edge('u', 'v')
            False
            sage: ed.add_edge('u', 'v', color='#112233'); ed.graph.has_edge('u', 'v')
            True
            sage: ed.get_edge_color(('u', 'v'))
            '#112233'
        """
        self.graph.add_edge((u, v, label))
        self.set_edge_color((u, v), color)

        with hold_canvas(self.canvas):
            self._draw_edge((u, v, label))
            self._draw_vertex(u)
            self._draw_vertex(v)

        self.text_graph_update()

    #####################
    # Drawing functions #
    #####################

    def _draw_vertex(self, v, canvas=None, color=None, highlight=True):
        """
        Draw the shape of a vertex.

        Also write the vertex name.
        The position is given by
        :meth:`~SimpleGraphEditor._get_vertex_pos`.
        If ``canvas`` is ``None``, the default drawing canvas
        (``self.canvas``) is used.
        If ``color`` is ``None`` the color is as given by
        :meth:`~SimpleGraphEditor.`get_vertex_color`.
        If ``highlight`` is true, also draw the focus on ``v``.
        
        TESTS::
        
        Check that something is drawn. It is hard to check more...

            sage: from phitigra import SimpleGraphEditor
            sage: ed = SimpleGraphEditor(Graph(0))
            sage: ed.vertex_name_toggle.value = False
            sage: ed.canvas.sync_image_data = True; ed.canvas.get_image_data(20, 20, 1, 1)
            array([[[0, 0, 0, 0]]], dtype=uint8)
            sage: ed.canvas.sync_image_data = False
            sage: ed.add_vertex_at(20, 20, name=0, color='#000000')
            sage: ed.canvas.sync_image_data = True; ed.canvas.get_image_data(20, 20, 1, 1)
            array([[[  0,   0,   0, 255]]], dtype=uint8)
        """

        if canvas is None:
            canvas = self.canvas
        if color is None:
            color = self.colors[v]

        x, y = self._get_vertex_pos(v)
        radius = self._get_radius(v)

        # The inside of the node
        canvas.fill_style = color
        canvas.fill_arc(x, y, radius, 0, 2*pi)

        # The border
        canvas.line_width = 2
        canvas.stroke_style = 'black'
        canvas.stroke_arc(x, y, radius, 0, 2*pi)

        if self.vertex_name_toggle.value:
            # The vertex name
            canvas.font = '20px sans'
            canvas.text_align = 'center'
            canvas.text_baseline = 'middle'
            canvas.fill_style = 'black'
            canvas.fill_text(str(v), x, y, max_width=2*radius)

        if highlight and v in self.selected_vertices:
            # Draw the focus
            canvas.stroke_style = 'white'
            canvas.set_line_dash([4, 4])
            canvas.stroke_arc(x, y, radius, 0, 2*pi)
            canvas.set_line_dash([])

    def _draw_neighbors(self, v, canvas=None):
        """
        Draw the neighbors of a vertex and the edges leading to them.
        """
        
        # Below We use ignore_direction=True to get all edges incident to a
        # vertex in the case where self.graph is directed
        for e in self.graph.edge_iterator(v, ignore_direction=True):
            self._draw_edge(e, canvas=canvas)
        # Draw the neighbors:
        for u in self.graph.neighbor_iterator(v):
            self._draw_vertex(u, canvas=canvas)

    def _draw_edge(self, e, endpoints=False, clear_first=False, canvas=None):
        """
        Draw an edge.

        An arrow is added if the graph is directed.

        INPUT:

        - ``e`` -- edge; of the form (first_end, second_end, label); the
          label is ignored;
        - ``endpoints`` -- Boolean (default: ``False``), whether to
          redraw the endpoints of the edge;
        - ``clear_first`` -- Boolean (default: ``False``), whether to
          erase the edge first by drawing a white edge over it (to use
          together with ``endpoints``);
        - ``canvas`` -- canvas where to draw the edge
          (default: ``None``); with the default value,
          ``self.canvas`` is used.

        WARNING:

        - The function does not check that ``e`` is an edge of ``self``;

        - The drawn edge start and end at the centers of the shapes of
          its endpoint vertices, so it is necessary to redraw these
          vertices after drawing the edge. The keyword ``endpoints``
          exists for that purpose.
        """

        u, v, *_ = e
        pos_u = self._get_vertex_pos(u)
        pos_v = self._get_vertex_pos(v)

        if canvas is None:
            canvas = self.canvas

        canvas.line_width = 3

        if clear_first:
            canvas.stroke_style = 'white'
            canvas.begin_path()
            canvas.move_to(*pos_u)
            canvas.line_to(*pos_v)
            canvas.stroke()

        canvas.stroke_style = self.get_edge_color((u, v))

        if (u, v) in self.selected_edges or (v, u) in self.selected_edges:
            # If the edge is selected, we draw it dashed
            canvas.set_line_dash([4, 4])

        canvas.begin_path()
        canvas.move_to(*pos_u)
        canvas.line_to(*pos_v)
        canvas.stroke()

        canvas.set_line_dash([])  # Reset dash pattern

        if self.graph.is_directed():
            # If the graph is directed, we also have to draw the arrow
            # tip; We draw it at the end of the edge (as usual)
            radius_v = self._get_radius(v)
            dist_min = radius_v + self._get_radius(u)

            # We only do it if the vertex shapes do not overlap.
            if (abs(pos_u[0] - pos_v[0]) > dist_min
                    or abs(pos_u[1] - pos_v[1]) > dist_min):
                canvas.save()
                # Move the canvas so that v lies at (0,0) and
                # rotate it so that v-y is on the x>0 axis:
                canvas.translate(*pos_v)
                canvas.rotate(float(atan2(pos_u[1] - pos_v[1],
                                          pos_u[0] - pos_v[0])))
                # Move to the point where the edge joins v's shape and
                # draw the arrow there:
                canvas.translate(radius_v, 0)
                canvas.fill_style = self.get_edge_color((u, v))
                SimpleGraphEditor.draw_arrow(canvas)
                canvas.restore()

        if endpoints:
            self._draw_vertex(u, canvas=canvas)
            self._draw_vertex(v, canvas=canvas)

    def _draw_graph(self):
        """
        Redraw the whole graph.

        Clear the drawing canvas (``self.canvas``) and draw the whole
        graph on it.
        """
        with hold_canvas(self.canvas):
            self.canvas.clear()
            for e in self.graph.edge_iterator():
                self._draw_edge(e)

            for v in self.graph.vertex_iterator():
                self._draw_vertex(v, highlight=False)

            # Selected vertices are (re)drawn on top
            for v in self.selected_vertices:
                self._draw_vertex(v, highlight=True)

    def refresh(self, vertex=None):
        if vertex:
            self._draw_vertex(vertex)
        else:
            self._draw_graph()

    def _select_vertex(self, vertex=None, redraw=True):
        """
        Add or remove a vertex from the set of selected vertices.

        INPUT:

        - `vertex` -- vertex (default: `None`); the vertex to be (un)selected;
        if `vertex` is `None` then the set of selected vertices is emptied;
        - `redraw` -- Boolean (default: `True`); when True, redraw `vertex`,
        otherwise does not change the drawing (useful when the graph is going
        to be fully redrawn afterwards anyway).

        OUTPUT:

        No output. Only side effects:

        - if `vertex` is `None` then the set `self.selected_vertices` is
        empied; otherwise `vertex` is added (if not already present) or
        removed (otherwise) in `self.selected_vertices`.
        - if `redraw` is `True`, `vertex` is redrawn, with or without the
        selection focus depending on whether it was selected or unselected.

        WARNING:
        No check is done that `vertex` indeed is a vertex of the graph.
        """

        if vertex is None:
            self.selected_vertices.clear()
            if redraw:
                self.refresh()
            return
        else:
            # Flip selected/unselected state
            try:
                self.selected_vertices.remove(vertex)
                self.output_text("Unselected vertex " +
                                 str(vertex))
            except KeyError:
                self.selected_vertices.add(vertex)
                self.output_text("Selected vertex " +
                                 str(vertex))

            # the radius of the selected vertex becomes the default one
            self.vertex_radius_box.value = (self._get_radius(vertex))

            if redraw:
                self._draw_vertex(vertex)

    ####################################################
    # Callbacks for mouse action and related functions #
    ####################################################

    def _clean_tools(self):
        """
        Forget that some drawing is taking place.

        This function deletes the `current_clique`, `current_walk_vertex`,
        `current_star_center`, and `current_star_leaf` variables of `self`,
        that store data used when adding a clique, a walk or a star to the
        graph.

        TESTS::

            sage: ed = SimpleGraphEditor(Graph(0))
            sage: attrs = ['current_clique', 'current_walk_vertex', 'current_star_center', 'current_star_leaf']
            sage: for attr in attrs: setattr(e, attr, 42)
            sage: ed._clean_tools()
            sage: any((hasattr(e, a) for a in attrs)
            False
        """
        attrs = ['current_clique',
                 'current_walk_vertex',
                 'current_star_center',
                 'current_star_leaf']

        for attr in attrs:
            try:
                delattr(self, attr)
            except AttributeError:
                pass

    @output.capture()
    def mouse_action_select_move(self,
                                 on_vertex, closest_edge,
                                 pixel_x, pixel_y):
        if on_vertex is not None:
            # Click was on a vertex
            self.dragged_vertex = on_vertex
            self.output_text("Click on vertex " + str(on_vertex))
            with hold_canvas(self.multi_canvas):

                # On the interact canvas we draw the moved vertex and
                # its neighbors
                self.interact_canvas.clear()
                self._draw_neighbors(on_vertex, canvas=self.interact_canvas)
                self._draw_vertex(on_vertex, canvas=self.interact_canvas)

                # Draw everything else on the main canvas
                self.canvas.clear()
                for (u1, u2, label) in self.graph.edge_iterator():
                    if (on_vertex != u1 and on_vertex != u2):
                        self._draw_edge((u1, u2, label))
                for u in self.graph.vertex_iterator():
                    if u != on_vertex:
                        self._draw_vertex(u)

        elif closest_edge is not None:
            # Click was not on a vertex but near an edge
            if closest_edge in self.selected_edges:
                self.selected_edges.remove(closest_edge)
            else:
                self.selected_edges.add(closest_edge)
            self._draw_edge(closest_edge, endpoints=True, clear_first=True)
        else:
            # The click was neither on a vertex nor on an edge
            self.dragging_canvas_from = [pixel_x, pixel_y]
            return

    def mouse_action_add_ve(self, on_vertex=None, pixel_x=None, pixel_y=None):
        """
        Function that is called after a click on ``on_vertex``
        (if not None) when the tool is 'add vertex or edge'.
        """
        if on_vertex is not None:
            # The click is done on an existing vertex

            if len(self.selected_vertices) == 0:
                # No vertex was selected: select the clicked vertex
                self._select_vertex(on_vertex)
            else:
                if on_vertex in self.selected_vertices:
                    # The click is done on the selected vertex
                    self._select_vertex()  # Unselect
                    return

                if len(self.selected_vertices) > 1:
                    raise ValueError

                selected_iterator = (v for v in self.selected_vertices)
                only_selected_vertex = next(selected_iterator)

                # A single vertex was selected and we clicked on a new
                # one: we link it to the previously selected vertex
                self.add_edge(only_selected_vertex, on_vertex)
                self._select_vertex()  # Unselect
                self.output_text("Added edge from " +
                                 str(only_selected_vertex) +
                                 " to " + str(on_vertex))
        else:
            # The click is not done on an existing vertex

            self.output_text("Click was not on a vertex")
            if len(self.selected_vertices):
                # If a vertex is selected and we click on the
                # background, we un-select it:
                self.selected_vertices.clear()
            else:
                # Otherwise, we add a new vertex
                self.add_vertex_at(pixel_x, pixel_y)
        self.refresh()
        self.text_graph_update()

    def mouse_action_del_ve(self, on_vertex=None, on_edge=None):

        if on_vertex is not None:
            self.graph.delete_vertex(on_vertex)
        elif on_edge is not None:
            self.graph.delete_edge(on_edge)
        else:
            return
        self._draw_graph()
        self.text_graph_update()

    def mouse_action_add_clique(self, clicked_node, click_x, click_y):
        if clicked_node is None:
            # Click on the canvas: we add a vertex
            clicked_node = self.add_vertex_at(click_x, click_y)

        if not hasattr(self, 'current_clique'):
            self.current_clique = [clicked_node]
            return
        if clicked_node in self.current_clique:
            self.output_text("Done constructing clique")
            del self.current_clique
            return

        for u in self.current_clique:
            self.add_edge(clicked_node, u)
        self.current_clique.append(clicked_node)

    def mouse_action_add_walk(self, clicked_node, click_x, click_y):
        if clicked_node is None:
            # Click on the canvas: we add a vertex
            clicked_node = self.add_vertex_at(click_x, click_y)

        if not hasattr(self, 'current_walk_vertex'):
            # The clicked vertex is the first vertex of the walk
            self.output_text("Constructing a walk - "
                             "click on the last vertex when you are done.")
            self.current_walk_vertex = clicked_node
            self._select_vertex(clicked_node)  # Select and redraw
            self.text_graph_update()
            return

        if clicked_node == self.current_walk_vertex:
            self.output_text("Done constructing walk")
            del self.current_walk_vertex
            self._select_vertex(clicked_node, redraw=False)  # Select
            self._draw_graph()
            self.text_graph_update()
            return

        self.add_edge(self.current_walk_vertex, clicked_node)
        self._select_vertex(self.current_walk_vertex)  # Unselect&redraw
        self._select_vertex(clicked_node)  # Select & redraw
        self.current_walk_vertex = clicked_node

    def mouse_action_add_star(self, clicked_node, click_x, click_y):
        if clicked_node is None:
            # Click on the canvas: we add a vertex
            clicked_node = self.add_vertex_at(click_x, click_y)

        if not hasattr(self, 'current_star_center'):
            # We start drawing a star from the center
            self.current_star_center = clicked_node
            self.current_star_leaf = clicked_node
            self._select_vertex(clicked_node)
            self.output_text('Star with center ' +
                             str(self.current_star_center) +
                             ': click on the leaves')
        elif (clicked_node == self.current_star_center or
                clicked_node == self.current_star_leaf):
            # We are done drawing a star
            self.output_text("Done drawing star")
            del self.current_star_center
            del self.current_star_leaf
            self._select_vertex(redraw=False)
            self._draw_graph()
        else:
            # We are drawing a star
            self.current_star_leaf = clicked_node
            self.add_edge(self.current_star_center,
                          self.current_star_leaf)
            self.output_text('Star with center ' +
                             str(self.current_star_center) +
                             ': click on the leaves')

    @output.capture()
    def mouse_down_handler(self, click_x, click_y):
        """
        Callback for mouse (down) clicks.

        If a vertex is selected and a different vertex is clicked, add
        an edge between these vertices. Otherwise, start dragging the
        clicked vertex.
        """

        self.initial_click_pos = (click_x, click_y)
        clicked_node = self._get_vertex_at(click_x, click_y)
        closest_edge = None

        if self.current_tool() == 'add vertex or edge':
            return self.mouse_action_add_ve(clicked_node, click_x, click_y)
        if self.current_tool() == 'add walk':
            return self.mouse_action_add_walk(clicked_node, click_x, click_y)
        if self.current_tool() == 'add clique':
            return self.mouse_action_add_clique(clicked_node, click_x, click_y)
        if self.current_tool() == 'add star':
            return self.mouse_action_add_star(clicked_node, click_x, click_y)

        if clicked_node is None:
            closest_edge = self._get_edge_at(click_x, click_y)

        if self.current_tool() == 'delete vertex or edge':
            return self.mouse_action_del_ve(clicked_node, closest_edge)
        if self.current_tool() == 'select / move':
            return self.mouse_action_select_move(clicked_node,
                                                 closest_edge,
                                                 click_x,
                                                 click_y)

    @output.capture()
    def mouse_move_handler(self, pixel_x, pixel_y):
        """Callback for mouse movement."""
        if self.dragged_vertex is not None:
            # We are dragging a vertex...
            self.output_text("Dragging vertex " + str(self.dragged_vertex))
            v = self.dragged_vertex
            self._set_vertex_pos(v, pixel_x, pixel_y)

            with hold_canvas(self.interact_canvas):
                # We only redraw what changes: the position of the
                # dragged vertex, the edges incident to it and also its
                # neighbors (so that the redrawn edges are not drawn on
                # the neighbors shapes):
                self.interact_canvas.clear()
                self._draw_neighbors(v, canvas=self.interact_canvas)
                self._draw_vertex(v, canvas=self.interact_canvas)

        elif self.dragging_canvas_from is not None:
            # We are dragging the canvas
            translation = [pixel_x - self.dragging_canvas_from[0],
                           pixel_y - self.dragging_canvas_from[1]]
            self._translate_layout(translation)
            self.dragging_canvas_from = [pixel_x, pixel_y]
            self._draw_graph()

    @output.capture()
    def mouse_up_handler(self, pixel_x, pixel_y):
        """Callback for mouse (up) click."""
        if self.dragged_vertex is not None:
            # If we dragged the vertex very close to its initial
            # position, we actually wanted to (un)select it
            if (abs(pixel_x - self.initial_click_pos[0]) < 10
                    and abs(pixel_y - self.initial_click_pos[1]) < 10):
                # (Un)select
                self._select_vertex(self.dragged_vertex, redraw=False)
                with hold_canvas(self.canvas):
                    # We redraw these on the main canvas
                    self._draw_neighbors(self.dragged_vertex)
                    self._draw_vertex(self.dragged_vertex)
                self.dragged_vertex = None
            else:
                self.output_text("Done dragging vertex.")
                self._draw_graph()

            self.dragged_vertex = None
            # Should be after _draw_graph to prevent screen flickering:
            self.interact_canvas.clear()

        elif self.dragging_canvas_from is not None:
            # We stop dragging the canvas
            self.dragging_canvas_from = None
            # If we dragged the canvas by very little (or not at all),
            # it was just a click on the canvas to unselect everything
            if (abs(pixel_x - self.initial_click_pos[0]) < 10
                    and abs(pixel_y - self.initial_click_pos[1]) < 10):
                self.output_text("Emptied selection.")
                self._select_vertex(redraw=False)
                self.selected_edges.clear()
                self.refresh()

    ##############################################
    # Callback functions for the widget elements #
    ##############################################

    def tool_selector_callback(self):
        """Called when changing tools."""
        self._clean_tools()
        self._select_vertex(redraw=False)
        self.selected_edges.clear()
        self.refresh()
        self.output_text('')

    def layout_selector_callback(self, change):
        """
        Apply the graph layout given by ``change['name']`` (if any).

        This function is called when the layout selector is used.
        If applying the layout is not possible, an error message is
        written to the text output widget.
        """
        if change['name'] != 'value':
            return
        elif change['new'] == '- change layout -':
            return

        new_layout = change['new']
        self.layout_selector.value = '- change layout -'

        # Interrupt any drawing action that is taking place:
        self._clean_tools()

        self.output_text('Updating layout, please wait...')

        # Handling unreasonable demands
        if new_layout == 'planar' and not self.graph.is_planar():
            self.output_text('\'planar\' layout impossible: '
                             'the graph is not planar!')
            return
        if new_layout == 'acyclic' and not self.graph.is_directed():
            self.output_text('\'directed acyclic\' layout impossible:'
                             ' the graph is not directed!')
            return

        if new_layout == 'random':
            self._random_layout()
        else:
            layout_kw = {'save_pos': True}  # Args for the layout fun

            if (new_layout == 'forest (root up)' or
                    new_layout == 'forest (root down)'):

                # Unreasonable demands again
                if self.graph.is_directed():
                    self.output_text('\'forest\' layout impossible: '
                                     'it is defined only for '
                                     'undirected graphs')
                    return
                if not self.graph.is_forest():
                    self.output_text('\'forest\' layout impossible: '
                                     'the graph is not a forest!')
                    return
                else:
                    # Now we can set the correct parameters
                    # for the forest layout
                    layout_kw['layout'] = 'forest'
                    try:
                        # Pick a selected vertex (if any) as root
                        root = next((v for v in self.selected_vertices))
                        layout_kw['forest_roots'] = [root]
                    except StopIteration:
                        pass
                    if new_layout == 'forest (root up)':
                        layout_kw['tree_orientation'] = 'down'
                    else:
                        layout_kw['tree_orientation'] = 'up'
            else:
                layout_kw['layout'] = new_layout

            # Now parameters are set so we can call the layout function
            self.graph.layout(**layout_kw)

        self._normalize_layout()  # Rescale so that it fits well
        self._draw_graph()
        self.output_text('Done updating layout.')

    def color_button_callback(self):
        """
        Change the color of the selected elements (if any).

        The new color is that of the color wheel:
        ``self.color_selector.value``.
        """
        new_color = self.color_selector.value

        for e in self.selected_edges:
            self.set_edge_color(e, new_color)
        for v in self.selected_vertices:
            self.set_vertex_color(v, new_color)
        self.refresh()

    def vertex_radius_box_callback(self, change):
        """
        Change the radius of the selected vertex (if any).

        The new radius is ``change['new']``.
        This function is called when the value in the
        ``vertex_radius_box`` box is changed.
        If no vertex is selected, nothing is done the set value becomes
        the new default value to be used for new vertices.
        """

        for v in self.selected_vertices:
            # Change the radius of the selected vertices
            self.set_vertex_radius(v, change['new'])
        self.refresh()

    def radius_button_callback(self):
        """
        Change the radius of the selected vertices (if any).

        The new radius is that of the radius text box.
        """
        r = self.vertex_radius_box.value
        for v in self.selected_vertices:
            self.set_vertex_radius(v, r)
        self.refresh()

    def clear_drawing_button_callback(self, b):
        """Callback for the clear_drawing_button."""
        self.graph = Graph(0)
        self._select_vertex(redraw=None)
        self._draw_graph()
        self.output_text("Cleared drawing.")
        self.text_graph_update()

    def set_next_callback(self, f):
        """
        Define a callback for the `Next` button.
        """
        self.next_button.on_click(lambda x: f())
