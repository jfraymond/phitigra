# phitigra

Phitigra is a graph editor widget for [SageMath](www.sagemath.org)
when using the [Jupyter](www.jupyter.org) notebook.

## Features

  * adding and removing edges and vertices with the mouse
  * easy export of the drawn graph
  * automatic update of the drawing when the graph changes
  * zoom in and zoom out
  * different layout options

## Dependencies

  * [ipywidgets](https://github.com/jupyter-widgets/ipywidgets)
  * [ipycanvas](https://github.com/martinRenou/ipycanvas)


## Usage

```
load("graph_editor.py")
load("talky_graph.py")
load("editable_graph.py")
eg = EditableGraph(graphs.RandomGNP(10, 0.25))
eg.show()
```
