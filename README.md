# Phitigra

_Phitigra_ is a graph editor widget for [SageMath](www.sagemath.org)
when using the [Jupyter](www.jupyter.org) notebook.
<p><img width="300" src="docs/source/images/phtgr.gif"></p>

## Features

  * positioning vertices with the mouse, adding edges and vertices
  * can deal with undirected or directed graphs (but not multigraphs)
  * changing the color of vertices and edges
  * easy export of the drawn graph for use with Sage
  * zoom in and zoom out
  * different layout options
  * step-by-step execution of a custom script on the drawn graph

## Dependencies

  * [ipywidgets](https://github.com/jupyter-widgets/ipywidgets)
  * [ipycanvas](https://github.com/martinRenou/ipycanvas)

Do not forget the following
```
jupyter nbextension enable --py widgetsnbextension
```
after you install ipywidgets (see the [documentation](https://ipywidgets.readthedocs.io/en/latest/user_install.html)).

Phitigra is not known to work with JupyterLab at the moment.

## Installation

Clone the source from the repository
```
git clone https://gitlab.limos.fr/jfraymon/phitigra
```

Change to the root directory of the cloned repository and run:
```
$ sage -pip install --upgrade --no-index -v .
```
That's it!

## Usage

```
from phitigra import SimpleGraphEditor
e = SimpleGraphEditor(graphs.RandomGNP(10, 0.5))
e.show()
# Now you can play with the graph!
```

A copy of the currently drawn graph can be obtained with the `get_graph` function:
```
G = e.get_graph()
# Now G is a copy of the graph drawn in editor e
```
