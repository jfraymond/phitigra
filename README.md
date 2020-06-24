# graph-edit

The purpose of the code in this repository is to provide a graph
editor for [sagemath](www.sagemath.org) when using the
[jupyter](www.jupyter.org) notebook, with the following features:

  1. adding and removing edges and vertices with the mouse
  2. easy export of the drawn graph
  3. automatic update of the drawing when the graph changes

## Dependencies

  * [ipywidgets](https://github.com/jupyter-widgets/ipywidgets)
  * [ipycanvas](https://github.com/martinRenou/ipycanvas)

Should be installed from sage's shell.

## Usage

```
load("graph_editor.py")
load("talky_graph.py")
load("editable_graph.py")
eg = EditableGraph(G)
eg.show()
```
