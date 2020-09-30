# Phitigra

A graph editor widget for [SageMath](www.sagemath.org)
when using the [Jupyter](www.jupyter.org) notebook.
<p><img width="300" src="docs/source/images/phtgr.gif"></p>

## Features

  * adding and removing edges and vertices with the mouse
  * easy export of the drawn graph
  * zoom in and zoom out
  * different layout options

## Planned features

  * automatic update of the drawing when the graph changes
  * changes of the drawing attributes from external functions

## Dependencies

  * [ipywidgets](https://github.com/jupyter-widgets/ipywidgets)
  * [ipycanvas](https://github.com/martinRenou/ipycanvas)

Do not forget the following
```
jupyter nbextension enable --py widgetsnbextension
```
after you install ipywidgets (see the [documentation](https://ipywidgets.readthedocs.io/en/latest/user_install.html)).

*Note:* until [that issue](https://github.com/martinRenou/ipycanvas/issues/117) with ipycanvas is resolved, please stick to version 0.4.7 of ipycanvas otherwise you will not be able to interact with the widget.

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
