#from generic_talky_graph import TalkyGraph
#from generic_editable_graph import GenericEditableGraph

class EditableGraph(GenericEditableGraph, TalkyGraph):
    '''
    Editable graph.
    '''
    def __init__(self, *args, **kwargs):
        drawing_parameters = kwargs.pop('drawing_parameters', None)
        TalkyGraph.__init__(self, *args, **kwargs)
        GenericEditableGraph.__init__(self, drawing_parameters)
