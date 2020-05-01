from .talky_graph import TalkyGraph
from .graph_editor import GenericEditableGraph

class EditableGraph(TalkyGraph):
    '''
    Editable graph.
    '''
    def __init__(self, *args, **kwargs):
        drawing_parameters = kwargs.pop('drawing_parameters', None)
        self.editor = GenericEditableGraph(self, drawing_parameters=drawing_parameters)
        #        notify_callback = (lambda _:self.editor.redraw_graph())
        super().__init__(*args, notify_callback=self.notify, **kwargs)
        self.editor._prepare()
        self.editor.output_text("Welcome!")
    def notify(self, s):
        self.editor.notify(s)
    def show(self):
        return self.editor.show()
