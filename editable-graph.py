from ipycanvas import Canvas, MultiCanvas, hold_canvas
from ipywidgets import Label, VBox, Output
from random import randint, randrange
from math import pi

# Todo: récupérer l'évènement que la souris sort du canvas pour déselectionner l'éventel noeud tiré

class GraphWithEditor():
    output = Output(layout={'border': '1px solid black'})
    def __init__(self, *args, **kwargs):
        self.graph = Graph(*args, **kwargs)

        # The two canvas where we draw
        self.multi_canvas = MultiCanvas(2, width=600, height=300, sync_image_data=True)
        self.canvas = self.multi_canvas[0] # The main layer
        # The layer where we draw objects in interaction
        # (moved vertices, tooltips, etc.):
        self.interact_canvas = self.multi_canvas[1]

        # Radii, positions and colors of the vertices on the drawing
        self.default_radius = 20 # Default radius of vertex marks
        self.vertex_radii = dict()
        self.pos = {v:
                    [randint(self.default_radius, self.canvas.width - self.default_radius - 1),
                     randint(self.default_radius, self.canvas.height - self.default_radius - 1)]
                    for v in self.graph.vertex_iterator()}
        self.colors = {v: f"#{randrange(0x1000000):06x}" # A random HTML color
                       for v in self.graph.vertex_iterator()}

        self._draw_graph()

        self.text_output = Label("Graph Editor")
        #self.output = Output(layout={'border': '1px solid black'})
        self.widget = VBox([self.multi_canvas, self.text_output, self.output])
        
        # Registering callbacks for mouse interaction
        self.interact_canvas.on_mouse_down(self.mouse_down_handler)
        self.interact_canvas.on_mouse_move(self.mouse_move_handler)
        self.interact_canvas.on_mouse_up(self.mouse_up_handler)
        # When the mouse leaves the canvas, we free the node that
        # was being dragged, if any:
        self.interact_canvas.on_mouse_out(self.mouse_up_handler)
        self.dragged_vertex = None

        
    def vertex_iterator(self):
        return self.graph.vertex_iterator()

    def edge_iterator(self):
        return self.graph.edge_iterator()

    def output_text(self, text):
        self.text_output.value = text
    
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
            self._draw_vertex(v)


    def _draw_edge(self, e, canvas=None):
        u, v, _ = e
        if canvas is None:
            canvas = self.canvas
        self.canvas.begin_path()
        self.canvas.move_to(*self.pos[u])
        self.canvas.line_to(*self.pos[v])
        self.canvas.stroke()
            
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

            if (pixel_x > mark_x - mark_radius
                and pixel_x < mark_x + mark_radius
                and pixel_y > mark_y - mark_radius
                and pixel_y < mark_y + mark_radius):
                self.dragged_vertex = v
                self.output_text("Clicked on vertex " + str(v))
                with hold_canvas(self.canvas):
                    # On the main canvas we draw everything,
                    # except the dragged vertex and the edges
                    # incident to it:
                    self.canvas.clear()
                    self._draw_edges(((u1, u2, l) for (u1, u2, l) in self.edge_iterator()
                                    if v is not u1 and v is not u2))
                    self._draw_vertices((u for u in self.vertex_iterator()
                                        if u is not v))

                break
        self.output_text("Click not on a vertex")

    @output.capture()
    def mouse_move_handler(self, pixel_x, pixel_y):
        self.output_text("Moving mouse to (" + str(pixel_x) + ", " + str(pixel_y) + ")")

        if self.dragged_vertex is not None:
            # We are dragging a vertex...
            self.output_text("Draging vertex " + str(self.dragged_vertex))
            v = self.dragged_vertex
            self.pos[v] = [pixel_x, pixel_y]
            
            with hold_canvas(self.interact_canvas):
                # We only redraw what changes: the position of the dragged
                # vertex, the edges incident to it and also its neighbors
                # (so that the redrawn edges are not drawn on the neighbors
                # shapes):
                self.interact_canvas.clear()
                for u in self.graph.neighbor_iterator(v):
                    # The edge:
                    self.interact_canvas.stroke_style = 'red'
                    self.interact_canvas.line_width = 2
                    self.interact_canvas.begin_path()
                    self.interact_canvas.move_to(*self.pos[u])
                    self.interact_canvas.line_to(*self.pos[v])
                    self.interact_canvas.stroke()
                    # The neighbor:
                    self._draw_vertex(u, canvas=self.interact_canvas)
                self._draw_vertex(v, canvas=self.interact_canvas, color='blue')

    @output.capture()
    def mouse_up_handler(self, pixel_x, pixel_y):
        if self.dragged_vertex is not None:
            self.dragged_vertex = None
            self.output_text("Done draging vertex.")
            self.interact_canvas.clear()            
            self._draw_graph()

