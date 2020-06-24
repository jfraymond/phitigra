<h1 align="center">phitigra</h1>
<h2 align="center"> a graph editor for SageMath</h2>


# phitigra

Phitigra is a graph editor widget for [SageMath](www.sagemath.org)
when using the [Jupyter](www.jupyter.org) notebook.

## Features

  1. adding and removing edges and vertices with the mouse
  2. easy export of the drawn graph
  3. automatic update of the drawing when the graph changes
  4. zoom in and zoom out
  5. different layout options

## Dependencies

  * [ipywidgets](https://github.com/jupyter-widgets/ipywidgets)
  * [ipycanvas](https://github.com/martinRenou/ipycanvas)


## Usage

```
load("graph_editor.py")
load("talky_graph.py")
load("editable_graph.py")
eg = EditableGraph(G)
eg.show()
```
