from ipycanvas import Canvas, MultiCanvas, hold_canvas
from ipywidgets import Label, VBox, HBox, Output, Button, Dropdown, ColorPicker
from random import randint, randrange
from math import pi

# Todo: récupérer l'évènement que la souris sort du canvas pour déselectionner l'éventel noeud tiré

class GraphWithEditor():
    output = Output(layout={'border': '1px solid black'})
    def __init__(self, *args, **kwargs):
        self.graph = Graph(*args, **kwargs)

        # The two canvas where we draw
        self.multi_canvas = MultiCanvas(2, width=800, height=600, sync_image_data=True)
        self.canvas = self.multi_canvas[0] # The main layer
        # The layer where we draw objects in interaction
        # (moved vertices, tooltips, etc.):
        self.interact_canvas = self.multi_canvas[1]

        self.selected_vertex = None
        self.dragged_vertex = None
        
        # Radii, positions and colors of the vertices on the drawing
        self.default_radius = 20 # Default radius of vertex marks
        self.vertex_radii = dict()

        self.pos = self.graph.get_pos()
        if self.pos is None: # The graph has no predefined positions:
            self.random_layout() # We pick some
        else:
            self.normalize_layout()
            
        self.colors = {v: f"#{randrange(0x1000000):06x}" # A random HTML color
                       for v in self.graph.vertex_iterator()}

        self._draw_graph()

        # Some widgets:
        # Where to display messages:
        self.text_output = Label("Graph Editor")

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
            description='Vertex color',
            value='#437FC0',
            disabled=False
        )
        self.color_selector.observe(self.color_selector_callback)

        #self.output = Output(layout={'border': '1px solid black'})
        self.widget = VBox([self.multi_canvas,
                            self.text_output,
                            HBox([self.layout_selector, self.color_selector]),
                            self.output])
        
        # Registering callbacks for mouse interaction
        self.interact_canvas.on_mouse_down(self.mouse_down_handler)
        self.interact_canvas.on_mouse_move(self.mouse_move_handler)
        self.interact_canvas.on_mouse_up(self.mouse_up_handler)
        # When the mouse leaves the canvas, we free the node that
        # was being dragged, if any:
        self.interact_canvas.on_mouse_out(self.mouse_up_handler)
        self.dragged_vertex = None

    def random_layout(self):
        '''Randomly pick positions for the vertices.'''
        self.pos = {v:
                (randint(self.default_radius, self.canvas.width - self.default_radius - 1),
                 randint(self.default_radius, self.canvas.height - self.default_radius - 1))
                for v in self.graph.vertex_iterator()}

    @output.capture()
    def layout_selector_callback(self, change):
        if change['name']=='value':
            new_layout = change['new']

            if new_layout == '':
                return
            elif new_layout == 'random':
                self.random_layout()
            else:
                if new_layout == 'tree' and not self.graph.is_tree():
                    self.output_text("\'tree\' layout impossible: the graph is not a forest!")
                elif new_layout == 'planar' and not self.graph.is_planar():
                    self.output_text("\'planar\' layout impossible: the graph is not planar!")
                else:
                    self.graph.layout(layout=new_layout, save_pos=True)
                    self.pos = self.graph.get_pos()
                    self.normalize_layout()

            self._draw_graph()
            self.layout_selector.value=''

    @output.capture()
    def color_selector_callback(self, change):
        if change['name']=='value':
            new_color = change['new']

            if self.selected_vertex is not None:
                # Change the color of the selected vertex
                self.colors[self.selected_vertex] = new_color
                self._redraw_vertex(self.selected_vertex, neighbors=False)
        
    def normalize_layout(self):
        '''Rescale the vertices coordinates so that they fit in the canvas.'''
        x_min = min(self.pos[v][0] for v in self.vertex_iterator())
        x_max = max(self.pos[v][0] for v in self.vertex_iterator())
        y_min = min(self.pos[v][1] for v in self.vertex_iterator())
        y_max = max(self.pos[v][1] for v in self.vertex_iterator())

        x_range = x_max - x_min
        y_range = y_max - y_min

        
        for v in self.vertex_iterator():
            x, y = self.pos[v]
            radius = self.vertex_radii.get(v, self.default_radius) + 5 # + 5 to get some margin
            
            new_x = (x - x_min) * (self.multi_canvas.width - 2*radius) / x_range + radius
            new_y = self.multi_canvas.height - ((y - y_min) * (self.multi_canvas.height - 2*radius) / y_range + radius)
            assert new_x >=0 and new_x <= self.multi_canvas.width
            assert new_y >= 0 and new_y <= self.multi_canvas.height, "y = " + str(new_y)
            self.pos[v] = (new_x, new_y)
        
    def vertex_iterator(self):
        return self.graph.vertex_iterator()

    def edge_iterator(self):
        return self.graph.edge_iterator()

    def output_text(self, text):
        self.text_output.value = text

    def add_vertex(self, x, y, name=None, color=None):
        '''Add a vertex that will be drawn at position x,y.'''
        if name is None:
            name = self.graph.add_vertex()
            return_name = True
        else:
            self.graph.add_vertex(name)
            return_name = False
            
        self.pos[name] = (x, y)
        if color is None:
            self.colors[name] = self.color_selector.value
        else:
            self.colors[name] = color
        self._draw_vertex(name)

        # In order to have the same behavior as the graph add_vertex function:
        if return_name:
            return name

    def add_edge(self, u, v):
        '''Add an edge to the undelying graph and draw it on the main canvas.'''
        self.graph.add_edge(u,v)
        # We draw the edge and the nodes shapes on top of it
        with hold_canvas(self.canvas):
            self._draw_edges([(self.selected_vertex, v, None)])
            self._draw_vertex(v)
            self._draw_vertex(self.selected_vertex)

    def _draw_vertex(self, v, canvas=None, color=None):
        x, y = self.pos[v]
        if canvas is None:
            canvas = self.canvas
        if color is None:
            color = self.colors[v]
            
        radius = self.vertex_radii.get(v, self.default_radius)
 
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
        # To use within a "with hold_canvas" block, preferably
        if vertices is None:
            vertices = self.vertex_iterator()
        if canvas is None:
            canvas = self.canvas

        for v in vertices:
            self._draw_vertex(v, canvas)

    def _highlight_vertex(self, v, canvas=None, color=None):
        '''Draw a thicker border on `v` with color `color`.'''
        
        x, y = self.pos[v]
        if canvas is None:
            canvas = self.canvas
        if color is None:
            color = 'red'
            
        radius = self.vertex_radii.get(v, self.default_radius)
 
        # The border
        canvas.line_width = 2
        canvas.stroke_style = color
        canvas.stroke_arc(x, y, radius, 0, 2*pi)

    def _redraw_vertex(self, v, canvas=None, highlight=True, neighbors=True, color=None):
        '''Redraw a vertex.
        If `highlight == True` and `v == self.selected_vertes`, the colored
        border around `v` is also drawn.
        If `neighbors == True`, the incident edges are also redrawn, as well
        as its neighbors, so that the edges incident to the neighbors do not
        overlap their shapes.
        '''
        if canvas is None:
            canvas = self.canvas
            
        with hold_canvas(canvas):
            if neighbors: # We also redraw the incident edges and the neighbors
                self._draw_edges(((u, v, None) for u in self.graph.neighbor_iterator(v)), canvas=canvas)
                self._draw_vertices((u for u in self.graph.neighbor_iterator(v)), canvas=canvas)
            self._draw_vertex(v, canvas=canvas, color=color)
            if self.selected_vertex is not None and highlight:
                self._highlight_vertex(self.selected_vertex)

    def _draw_edge(self, e, canvas=None):
        u, v, _ = e
        if canvas is None:
            canvas = self.canvas
        canvas.begin_path()
        canvas.move_to(*self.pos[u])
        canvas.line_to(*self.pos[v])
        canvas.stroke()
            
    def _draw_edges(self, edges=None, canvas=None, color='black'):
        # To use within a "with hold_canvas" block, preferably

        if edges is None:
            edges = self.edge_iterator()
        if canvas is None:
            canvas = self.canvas
        canvas.stroke_style = color
        canvas.line_width = 2
        for e in edges:
            self._draw_edge(e, canvas=canvas)

    def _draw_graph(self):

        with hold_canvas(self.canvas):
            self.canvas.clear()
            self._draw_edges()
            self._draw_vertices()
            if self.selected_vertex is not None:
                self._highlight_vertex(self.selected_vertex)
                
    def show(self):
        return self.widget

    @output.capture()
    def mouse_down_handler(self, pixel_x, pixel_y):
        # To be called when one clicks on pixel_x, pixel_y
        self.output_text("Click at (" + str(pixel_x) + ", " + str(pixel_y) + ")")

        # Find the clicked node (if any):
        for v in self.vertex_iterator():
            mark_x, mark_y = self.pos[v]
            mark_radius = self.vertex_radii.get(v, self.default_radius)

            if (abs(pixel_x - mark_x) < mark_radius
                and
                abs(pixel_y - mark_y) < mark_radius):
                # The user clicked on vertex v!

                if self.selected_vertex is not None:
                    if self.selected_vertex == v:
                        # We unselect vertex v
                        self.selected_vertex = None
                        self.output_text("No vertex selected")
                        self._redraw_vertex(v) # Redraw without highlight
                        return
                    else:
                        # We link v and the previously selected vertex
                        self.add_edge(self.selected_vertex, v)
                        self.output_text("Added edge from " + str(self.selected_vertex) + " to " + str(v))
                        self.selected_vertex = None
                        return

                # At this point, no vertex is currently selected
                self.dragged_vertex = v
                self.initial_click_pos = (pixel_x, pixel_y)
                self.output_text("Clicked on vertex " + str(v))
                with hold_canvas(self.multi_canvas):
                    # On the main canvas we draw everything,
                    # except the dragged vertex and the edges
                    # incident to it. We draw the rest on the
                    # interact canvas.
                    self.canvas.clear()
                    self.interact_canvas.clear()
                    self._draw_edges(((u1, u2, l) for (u1, u2, l) in self.edge_iterator()
                                    if v is not u1 and v is not u2))
                    self._draw_vertices((u for u in self.vertex_iterator()
                                        if u is not v))
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
            self._redraw_vertex(self.selected_vertex, highlight=False) # Redraw it without highlighting
            self.selected_vertex = None
        else:
            # Otherwise, we add a new vertex
            self.add_vertex(pixel_x, pixel_y)

    @output.capture()
    def mouse_move_handler(self, pixel_x, pixel_y):
#        self.output_text("Moving mouse to (" + str(pixel_x) + ", " + str(pixel_y) + ")")

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
            # If we dragged the vertex very close to its initial position
            # we actually wanted to select it
            if (abs(pixel_x - self.initial_click_pos[0]) < 10
                and abs(pixel_y - self.initial_click_pos[1]) < 10):
                assert self.selected_vertex is None
                self.selected_vertex = self.dragged_vertex
                self.output_text("Selected vertex " + str(self.selected_vertex))
                self.color_selector.value = self.colors[self.selected_vertex]
                self._draw_graph()
                #self._redraw_vertex(self.selected_vertex)
                
            else:
                self.output_text("Done draging vertex.")
                self._draw_graph()
            self.dragged_vertex = None
            #self._draw_graph()
            # Should be after _draw_graph to prevent screen flickering:
            self.interact_canvas.clear()
