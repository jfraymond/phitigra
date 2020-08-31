# Phitigra

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

Do not forget the following
```
jupyter nbextension enable --py widgetsnbextension
```
after you install ipywidgets (see the [documentation](https://ipywidgets.readthedocs.io/en/latest/user_install.html)).

*Note:* until [that issue](https://github.com/martinRenou/ipycanvas/issues/117) with ipycanvas is resolved, please stick to version 0.4.7 of ipycanvas otherwise you will not be able to interact with the widget.

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
from phitigra import EditableGraph
eg = EditableGraph(graphs.RandomGNP(10, 0.5))
eg.show()
# Now you can play with the graph!
```
