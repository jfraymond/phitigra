from ipycanvas import Canvas, MultiCanvas, hold_canvas
from ipywidgets import Label, VBox, HBox, Output, Button, Dropdown, ColorPicker
from random import randint, randrange
from math import pi, sqrt, atan2
from itertools import chain

class GraphWithEditor(Graph):
    output = Output(layout={'border': '1px solid black'})

    def __init__(self, *args, **kwargs):
        Graph.__init__(self, *args, **kwargs)
        self.graph = self

        # The two canvas where we draw
        self.multi_canvas = MultiCanvas(2,
                                        width=800, height=600,
                                        sync_image_data=True)
        self.canvas = self.multi_canvas[0]    # The main layer
        # The layer where we draw objects in interaction
        # (moved vertices, tooltips, etc.):
        self.interact_canvas = self.multi_canvas[1]

        self.selected_vertex = None
        self.dragged_vertex = None

        self.drawing_parameters = {
            'default_radius': 20,
            # An arrow tip is defined by two values: the distance on the edge
            # taken by the arrow (arrow_tip_length) and the distance between
            # the two symmetric angles of the arrow (arrow_tip_height is half
            # this value).
            'arrow_tip_width': 15,
            'arrow_tip_height': 8
        }

        def draw_arrow(canvas):
            '''Draw an arrow at with tip at (0,0), pointing to the left.'''
            a_x = self.drawing_parameters['arrow_tip_width']
            a_y = self.drawing_parameters['arrow_tip_height']
            canvas.begin_path()
            canvas.move_to(0, 0)
            canvas.line_to(a_x, a_y)
            canvas.line_to(0.75*a_x, 0)
            canvas.line_to(a_x, -a_y)
            canvas.move_to(0, 0)
            canvas.fill()
        self.drawing_parameters['draw_arrow'] = draw_arrow

        # Radii, positions and colors of the vertices on the drawing
        self.vertex_radii = dict()

        self.pos = self.graph.get_pos()
        if self.pos is None:        # The graph has no predefined positions:
            self.random_layout()    # We pick some
        else:
            self.normalize_layout(y_flip=True)

        self.colors = {v: f"#{randrange(0x1000000):06x}"    # Random HTML color
                       for v in self.graph.vertex_iterator()}

        self._draw_graph()

        # Registering callbacks for mouse interaction on the canvas
        self.interact_canvas.on_mouse_down(self.mouse_down_handler)
        self.interact_canvas.on_mouse_move(self.mouse_move_handler)
        self.interact_canvas.on_mouse_up(self.mouse_up_handler)
        # When the mouse leaves the canvas, we free the node that
        # was being dragged, if any:
        self.interact_canvas.on_mouse_out(self.mouse_up_handler)
        self.dragged_vertex = None

        # The widgets of the graph editor (besides the canvas):
        # Where to display messages:
        self.text_output = Label("Graph Editor")

        # Button to rescale:
        self.zoom_to_fit_button = Button(description="Zoom to fit",
                                         disabled=False,
                                         button_style='',
                                         tooltip=('Rescale so that the graph '
                                                  'fills the canvas'),
                                         icon='')
        self.zoom_to_fit_button.on_click(lambda x: (self.normalize_layout(),
                                                    self._draw_graph()))

        # Selector to change layout
        self.layout_selector = Dropdown(
            options=['', 'random', 'spring', 'circular', 'planar', 'tree'],
            value='',
            description='Set layout:',
        )
        self.layout_selector.observe(self.layout_selector_callback)

        # Selector to change the color of the selected vertex
        self.color_selector = ColorPicker(
            concise=False,
            description='Vertex color:',
            value='#437FC0',
            disabled=False
        )
        self.color_selector.observe(self.color_selector_callback)

        # The drawing tools
        self.tool_selector = Dropdown(
            options=['add vertex or edge',
                     'delete vertex or edge',
                     'add walk',
                     'add clique'],
            value='add vertex or edge',
            description='Choose tool:',
        )
        self.current_tool = lambda: self.tool_selector.value

        self.widget = VBox([self.multi_canvas,
                            self.text_output,
                            HBox([self.layout_selector,
                                  self.color_selector,
                                  self.zoom_to_fit_button]),
                            HBox([self.tool_selector]),
                            self.output])

    def get_radius(self, v):
        '''Return the radius of v if it has been predefined, or the default
        radius otherwise.'''
        return self.vertex_radii.get(v,
                                     self.drawing_parameters['default_radius'])

    def random_layout(self):
        '''Randomly pick positions for the vertices.'''
        radius = self.drawing_parameters['default_radius']
        self.pos = {v: (randint(radius, self.canvas.width - radius - 1),
                        randint(radius, self.canvas.height - radius - 1))
                    for v in self.graph.vertex_iterator()}

    @output.capture()
    def layout_selector_callback(self, change):
        '''
        Apply a the layout in ``change['name']`` (if any).

        The function to call when the layout selector is used.
        If applying the layout is not possible, an error message is written
        to the text output widget.
        '''
        if change['name'] == 'value':
            new_layout = change['new']

            if new_layout == '':
                return
            elif new_layout == 'random':
                self.random_layout()
            else:
                if new_layout == 'tree' and not self.graph.is_tree():
                    self.output_text('\'tree\' layout impossible: '
                                     'the graph is not a forest!')
                elif new_layout == 'planar' and not self.graph.is_planar():
                    self.output_text('\'planar\' layout impossible: '
                                     'the graph is not planar!')
                else:
                    self.graph.layout(layout=new_layout, save_pos=True)
                    self.pos = self.graph.get_pos()
                    self.normalize_layout()

            self._draw_graph()
            self.layout_selector.value = ''

    @output.capture()
    def color_selector_callback(self, change):
        '''
        Change the color of the selected vertex (if any) for that given by
        ``change``.

        The function to call when the color selector is used.
        If no vertex is selected or the color did not change, nothing is done.
        '''
        if change['name'] == 'value':
            new_color = change['new']

            if self.selected_vertex is not None:
                # Change the color of the selected vertex
                self._set_vertex_color(self.selected_vertex, new_color)
                self._redraw_vertex(self.selected_vertex, neighbors=False)

    def normalize_layout(self, flip_y=False):
        '''
        Shift and rescale the vertices coordinates so that they fit in the
        canvas.

        ``x`` and ``y`` coordinates are scaled by the same factor and the
        graph is centered. If ``flip_y`` is ``False``, the ``y`` coordinates
        is reversed. This is useful for graphs that come with predefined
        vertex positions with the ``y`` axis pointing upwards.
        '''
        x_min = min(self.pos[v][0] for v in self.vertex_iterator())
        x_max = max(self.pos[v][0] for v in self.vertex_iterator())
        y_min = min(self.pos[v][1] for v in self.vertex_iterator())
        y_max = max(self.pos[v][1] for v in self.vertex_iterator())

        x_range = max(x_max - x_min, 0.1)    # max to avoid division by 0
        y_range = max(y_max - y_min, 0.1)

        radius = self.drawing_parameters['default_radius'] + 5
        # We scale xs and ys with the same factor to keep proportions
        factor = min((self.multi_canvas.width - 2*radius) / x_range,
                     (self.multi_canvas.height - 2*radius) / y_range)

        factor_x = (self.multi_canvas.width - 2*radius) / x_range
        factor_y = (self.multi_canvas.height - 2*radius) / y_range

        if factor_x < factor_y:
            factor = factor_x
            x_shift = radius
            y_shift = (self.multi_canvas.height - y_range * factor_x) / 2
        else:
            factor = factor_y
            x_shift = (self.multi_canvas.width - x_range * factor_y) / 2
            y_shift = radius
        
        for v in self.vertex_iterator():
            x, y = self.pos[v]
            new_x = (x - x_min) * factor + x_shift
            if flip_y:
                new_y = (y - y_min) * factor + y_shift
            else:
                new_y = (self.multi_canvas.height -
                         ((y - y_min) * factor + y_shift))
            assert new_x >= 0 and new_x <= self.multi_canvas.width
            assert new_y >= 0 and new_y <= self.multi_canvas.height
            self.pos[v] = (new_x, new_y)

    def output_text(self, text):
        self.text_output.value = text

    def _set_vertex_pos(self, v, x, y):
        '''Give the position (x,y) to vertex v.'''
        self.pos[v] = [x, y]

    def _set_vertex_color(self, v, color=None):
        '''
        Set the color of a vertex.

        If ``color`` is ``None``, use the color of the color selector.
        Does not redraw the graph.
        '''
        if color is None:
            self.colors[v] = self.color_selector.value
        else:
            self.colors[v] = color

    def add_vertex_at(self, x, y, name=None, color=None):
        '''
        Add a vertex to a given position, color it and draw it.

        If the color is ``None``, use the color of the color selector.
        '''

        if name is None:
            name = self.graph.add_vertex()
            return_name = True
        else:
            self.graph.add_vertex(name)
            return_name = False

        self._set_vertex_pos(name, x, y)
        self._set_vertex_color(name)
        self._draw_vertex(name)

        # In order to have the same behavior as the graph add_vertex function:
        if return_name:
            return name

    def _draw_vertex(self, v, canvas=None, color=None):
        '''
        Draw a given vertex.

        If ``canvas`` is ``None``, the default drawing canvas (``self.canvas``)
        is used.
        '''
        x, y = self.pos[v]
        if canvas is None:
            canvas = self.canvas
        if color is None:
            color = self.colors[v]

        radius = self.get_radius(v)

        # The inside of the node
        canvas.fill_style = color
        canvas.fill_arc(x, y, radius, 0, 2*pi)

        # The border
        canvas.line_width = 2
        canvas.stroke_style = 'black'
        canvas.stroke_arc(x, y, radius, 0, 2*pi)

        # The text
        canvas.font = '20px sans'
        canvas.text_align = 'center'
        canvas.text_baseline = 'middle'
        canvas.fill_style = 'black'
        canvas.fill_text(str(v), x, y, max_width = 2*radius)

    def _draw_vertices(self, vertices=None, canvas=None):
        '''
        Draw the ``vertices`` on ``canvas``.
        
        To use within a ``with hold_canvas`` block, preferably.
        '''
        if vertices is None:
            vertices = self.vertex_iterator()
        if canvas is None:
            canvas = self.canvas

        for v in vertices:
            self._draw_vertex(v, canvas)

    def _highlight_vertex(self, v, canvas=None, color=None):
        '''Set focus on vertex ``v``.'''

        x, y = self.pos[v]
        if canvas is None:
            canvas = self.canvas
        if color is None:
            color = 'black'

        radius = self.get_radius(v)

        # The border
        canvas.line_width = 2
        canvas.stroke_style = color
        canvas.stroke_arc(x, y, radius, 0, 2*pi)

        canvas.stroke_style = 'white'
        canvas.set_line_dash([4, 4])
        canvas.stroke_arc(x, y, radius, 0, 2*pi)
        canvas.set_line_dash([])

    def _redraw_vertex(self, v, canvas=None, highlight=True,
                       neighbors=True, color=None):
        '''
        Redraw a vertex.

        If ``highlight == True`` and ``v == self.selected_vertes``, the colored
        border around ``v`` is also drawn.
        If ``neighbors == True``, the incident edges are also redrawn, as well
        as its neighbors, so that the edges incident to the neighbors do not
        overlap their shapes.
        '''
        if canvas is None:
            canvas = self.canvas

        with hold_canvas(canvas):
            if neighbors:
                # We also redraw the incident edges
                # and the neighbors
                if self.graph.is_directed():
                    if self.graph.allows_multiple_edges():
                        # In this case we must iterate over all edges, so that
                        # we draw them in the same order as when we draw the
                        # full graph...
                        incident_edges = ((u1, u2, l)
                                          for (u1, u2, l)
                                          in self.graph.edge_iterator()
                                          if v == u1 or v == u2)
                    else:
                        # We chain the iterators in order to make a unique call
                        # to _draw_edges, which is important when dealing with
                        # digraphs with multiple edges
                        incident_edges = chain(
                            (e for e in self.graph.incoming_edge_iterator(v)),
                            (e for e in self.graph.outgoing_edge_iterator(v)))
                    # Finally we draw those directed edges
                    self._draw_edges(incident_edges, canvas=canvas)
                else:
                    self._draw_edges((e for e in self.graph.edge_iterator(v)),
                                     canvas=canvas)
                self._draw_vertices((u
                                     for u in self.graph.neighbor_iterator(v)),
                                    canvas=canvas)

            self._draw_vertex(v, canvas=canvas, color=color)
            if self.selected_vertex is not None and highlight:
                self._highlight_vertex(self.selected_vertex)

    def _draw_edge(self, e, canvas=None, curve=None, middle_arrow=False):
        u, v, lab = e
        pos_u, pos_v = self.pos[u], self.pos[v]
        if canvas is None:
            canvas = self.canvas

        if curve is not None:
            canvas.begin_path()
            canvas.move_to(*pos_u)
            # u-v distance:
            duv = sqrt((pos_u[0] - pos_v[0])**2 +
                       (pos_u[1] - pos_v[1])**2)
            # Halfway from u to v:
            huv = (pos_u[0] + (pos_v[0] - pos_u[0])/2,
                   pos_u[1] + (pos_v[1] - pos_u[1])/2)
            # Unit normal vector to uv:
            nuv = ((pos_v[1] - pos_u[1]) / duv,
                   - (pos_v[0] - pos_u[0]) / duv)
            # Control point of the curve
            cp = (huv[0] + nuv[0] * curve,
                  huv[1] + nuv[1] * curve)
            canvas.quadratic_curve_to(*cp, *pos_v)
            canvas.stroke()

            if self.graph.is_directed():
                # If the graph is directed, we also have to draw the arrow tip
                # In this case (curved edge), we draw the arrow at mid-edge.
                dist_min = self.get_radius(v) + self.get_radius(u)
                # We only do it if the vertex shapes do not overlap.
                if (abs(pos_u[0] - pos_v[0]) > dist_min or
                        abs(pos_u[1] - pos_v[1]) > dist_min):
                    canvas.save()
                    # Move the canvas so that v lies at (0,0) and
                    # rotate it so that v-y is on the x>0 axis:
                    canvas.translate(*huv)
                    canvas.rotate(float(atan2(pos_u[1] - pos_v[1],
                                              pos_u[0] - pos_v[0])))
                    # Move to the point where the edge joins v's shape and
                    # draw the arrow there:
                    canvas.translate(-self.drawing_parameters['arrow_tip_width'] / 2, curve/2)
                    self.drawing_parameters['draw_arrow'](canvas)
                    canvas.restore()

        else:
            canvas.begin_path()
            canvas.move_to(*pos_u)
            canvas.line_to(*pos_v)
            canvas.stroke()

            if self.graph.is_directed():
                # If the graph is directed, we also have to draw the arrow tip
                # We draw it at the end of the edge (as usual)
                radius_v = self.get_radius(v)
                dist_min = radius_v + self.get_radius(u)

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
                    canvas.translate(self.get_radius(v), 0)
                    self.drawing_parameters['draw_arrow'](canvas)
                    canvas.restore()

    def _draw_edges(self, edges, canvas=None, color='black'):
        '''
        Draw the edges contained in `edges` on canvas `canvas` and
        in color `color`.

        To use within a `with hold_canvas` block, preferably.
        If `edges` is not specified, draw the edges of the whole graph.
        If `canvas` is not specified, draw on self.canvas.

        WARNING: When dealing with oriented multigraphs, the following should
        be applied: for every vertices u and v, all the edges between u and v
        (in either direction) should be drawn within the same call to
        _draw_edges (otherwise some edges might be drawn on top of each other).
        '''

        if canvas is None:
            canvas = self.canvas

        canvas.stroke_style = color
        canvas.line_width = 3

        if not self.graph.allows_multiple_edges():
            for e in edges:
                self._draw_edge(e, canvas=canvas)
        else:
            # To count how many times an edge (u,v) has been drawn
            # so far
            seen_edges = dict()
            # To remember which of (u,v) and (v,u) was drawn the latest
            seen_last = dict()

            def get_curve(e):
                '''Return the curve of the edge e.'''
                u, v, _ = e
                # How many times we saw an edge between these vertices so far:
                cur_mul = seen_edges.get((u, v), 0) + seen_edges.get((v, u), 0)
                seen_edges[(u, v)] = 1 + seen_edges.get((u, v), 0)
                if not cur_mul:
                    # No edge between u and v has been drawn so far
                    seen_last[(u, v)] = True
                    seen_last[(v, u)] = False
                    return 0
                else:
                    # Among edges of the forms (u,v) and (v,u),
                    # was an edge of the form (u,v) seen last?
                    uv_last = seen_last[(u, v)]
                    seen_last[(u, v)] = True
                    seen_last[(v, u)] = False
                    factor = -1 if uv_last else 1
                    if is_even(cur_mul):
                        return factor * cur_mul * 15
                    else:
                        return -factor * (cur_mul+1) * 15

        for e in edges:
            self._draw_edge(e, canvas=canvas, curve=get_curve(e))

    def _draw_graph(self):
        '''
        Clear the drawing canvas and draw the whole graph.
        '''
        with hold_canvas(self.canvas):
            self.canvas.clear()
            self._draw_edges(self.graph.edge_iterator())
            self._draw_vertices()
            if self.selected_vertex is not None:
                self._highlight_vertex(self.selected_vertex)

    def show(self):
        return self.widget

    def mouse_action_add_ve(self, on_vertex=None):
        #        blah
        if (self.selected_vertex is not None and
            self.selected_vertex != v):
            # A node was selected and we clicked on a new node v:
            # we link v and the previously selected vertex
            self.graph.add_edge(self.selected_vertex, v)
            self.output_text("Added edge from " +
                             str(self.selected_vertex) +
                             " to " + str(v))
            self.selected_vertex = None
            self._draw_graph()
            return

        # At this point, no vertex is currently selected
        self.dragged_vertex = v
        self.initial_click_pos = (pixel_x, pixel_y)
        self.output_text("Clicked on vertex " + str(v))
        with hold_canvas(self.multi_canvas):
            # On the main canvas we draw everything,
            # except the dragged vertex and the edges
            # incident to it.
            self.canvas.clear()
            self._draw_edges(((u1, u2, label)
                              for (u1, u2, label) in self.graph.edge_iterator()
                              if (v != u1 and v != u2)))
            self._draw_vertices((u
                                 for u in self.graph.vertex_iterator()
                                 if u != v))
            # We draw the rest on the interact canvas.
            self.interact_canvas.clear()
            self._redraw_vertex(v, canvas=self.interact_canvas,
                                neighbors=True,
                                highlight=False,
                                color='gray')
        return
        # If we reach this point, the click was not an an existing vertex mark

        self.output_text("Click not on a vertex")
        if self.selected_vertex is not None:
            # If a vertex is selected and we click on the background, we
            # un-select it
            self._redraw_vertex(self.selected_vertex,
                                highlight=False,
                                neighbors=False)    # Redraw without focus
            self.selected_vertex = None
        else:
            # Otherwise, we add a new vertex
            self.add_vertex_at(pixel_x, pixel_y)

    @output.capture()
    def mouse_down_handler(self, click_x, click_y):
        '''
        Callback for mouse clicks.

        If a vertex is selected and a different vertex is clicked, add an
        edge between these vertices. Otherwise, start dragging the clicked
        vertex.
        '''

        # Find the clicked node (if any):
        clicked_node = None
        for v in self.graph.vertex_iterator():
            v_x, v_y = self.pos[v]
            radius = self.get_radius(v)

            if (abs(click_x - v_x) < radius and
                    abs(click_y - v_y) < radius):
                # The user clicked on vertex v!
                clicked_node = v
                break

        if self.current_tool() == 'add vertex or edge':
            return self.mouse_action_add_ve(v)
        elif self.current_tool() == 'delete vertex or edge':

            # Check for edges:
            thresold = 20
            for v in self.graph.vertex_iterator():
                if click_x < self.pos[v][0]:
                    #print('Not this one:' + str(click_x))
                    continue
                for u in self.graph.neighbor_iterator(v):
                    p_v, p_u = self.pos[v], self.pos[u]

                    if p_u[0] < click_x:
                        continue
                    if (click_y > self.pos[v][1] and
                         click_y > self.pos[u][1]):
                        continue
                    if (click_y < self.pos[v][1] and
                        click_y < self.pos[u][1]):
                        #print('nope')
                        continue
                    delta_y = p_u[1] - p_v[1]
                    delta_x = p_u[0] - p_v[0]
                    slope =  ((delta_y if abs(delta_y) > 0.1 else 0.1) /
                              (delta_x if abs(delta_x) > 0.1 else 0.1))
                    uv_edge_at_c_x = (p_v[1] - (p_v[0] - click_x) * slope)
                    uv_edge_at_c_y = (p_v[0] - (p_v[1] - click_y) / slope)
                    dh = abs(click_y - uv_edge_at_c_x)
                    dv = abs(click_x - uv_edge_at_c_y)
                    if dh < thresold or dv < thresold:
                        self.output_text('Deleted edge ' + str(u) + ', ' + str(v))
                        self.canvas.stroke_style = f"#{randrange(0x1000000):06x}"
                        self._draw_edge((u,v,''))
                        return
                                        
            
                    #            return self.mouse_action_del_ve(v)
        else:
            self.output_text('Not implemented!')
            return

    @output.capture()
    def mouse_move_handler(self, pixel_x, pixel_y):

        if self.dragged_vertex is not None:
            # We are dragging a vertex...
            self.output_text("Draging vertex " + str(self.dragged_vertex))
            v = self.dragged_vertex
            self.pos[v] = (pixel_x, pixel_y)

            with hold_canvas(self.interact_canvas):
                # We only redraw what changes: the position of the dragged
                # vertex, the edges incident to it and also its neighbors
                # (so that the redrawn edges are not drawn on the neighbors
                # shapes):
                self.interact_canvas.clear()
                self._redraw_vertex(v, canvas=self.interact_canvas,
                                    neighbors=True,
                                    highlight=False,
                                    color='gray')

    @output.capture()
    def mouse_up_handler(self, pixel_x, pixel_y):
        if self.dragged_vertex is not None:
            # If we dragged the vertex very close to its initial position,
            # we actually wanted to (un)select it
            if (abs(pixel_x - self.initial_click_pos[0]) < 10
                    and abs(pixel_y - self.initial_click_pos[1]) < 10):
                if self.selected_vertex is None:
                    self.selected_vertex = self.dragged_vertex
                    self.output_text("Selected vertex " +
                                     str(self.selected_vertex))
                    self.color_selector.value = self.colors[self.selected_vertex]
                else:
                    self.selected_vertex = None

                self._redraw_vertex(self.dragged_vertex)
                self.dragged_vertex = None
            else:
                self.selected_vertex = None
                self.output_text("Done draging vertex.")
                self._draw_graph()
            self.dragged_vertex = None
            # Should be after _draw_graph to prevent screen flickering:
            self.interact_canvas.clear()
