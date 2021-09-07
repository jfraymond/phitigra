# Phitigra

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/git/https%3A%2F%2Fgitlab.limos.fr%2Fjfraymon%2Fphitigra/develop?filepath=demo.ipynb)

_Phitigra_ is a graph editor widget for [SageMath](www.sagemath.org)
when using the [Jupyter](www.jupyter.org) notebook.
<p><img width="300" src="docs/source/images/phtgr.gif"></p>
(Note: this animation is from an older version of phitigra.)



Try the [demo](https://mybinder.org/v2/git/https%3A%2F%2Fgitlab.limos.fr%2Fjfraymon%2Fphitigra/develop?filepath=demo.ipynb) notebook on binder!

## Features

With phitigra one can:

  * draw graphs using the mouse to add vertices and edges
  * move the vertices positions, zoom in and out
  * draw undirected as well as directed graphs
  * choose the color of vertices and edges
  * apply various layout algorithms
  * easily retrieve the drawn graph for use with SageMath
  * run step-by-step a custom script on the drawn graph
  * change and refresh the drawing with external functions

## Non-features

The following are not supported:

  * multigraphs: multiple edges will not be drawn
  * large graphs: the rendering will be unpraticably slow
  
## Dependencies

  * [ipywidgets](https://github.com/jupyter-widgets/ipywidgets), for user interaction
  * [ipycanvas](https://github.com/martinRenou/ipycanvas), for the drawing

You might need the following
```
jupyter nbextension enable --py widgetsnbextension
```
after you install ipywidgets (see the [documentation](https://ipywidgets.readthedocs.io/en/latest/user_install.html)).

_Note:_ phitigra is not known to work with JupyterLab at the moment.

## How to try it?

### On binder

(Runs online, nothing to install.)  
Clicking [here](https://mybinder.org/v2/git/https%3A%2F%2Fgitlab.limos.fr%2Fjfraymon%2Fphitigra/develop?filepath=demo.ipynb) will open the demo notebook on binder in a new tab. Note that this uses the development version of phitigra, which may differ from the one in the `master` branch. 

### From a standalone SageMath installation

This assumes that SageMath is installed on your system. See http://www.sagemath.org for install instructions.

Clone the source from the repository
```
git clone https://gitlab.limos.fr/jfraymon/phitigra
```

Change to the root directory of the cloned repository and run:
```
sage -pip install .
```

That's it!

## Usage

```
from phitigra import GraphEditor
editor = GraphEditor(graphs.RandomGNP(10, 0.5))
editor.show()
# Now you can play with the graph!
```

A copy of the currently drawn graph can be obtained with the `get_graph` function:
```
G = editor.get_graph()
# Now G is a copy of the graph drawn in editor e
```

There are more examples in the [demo](demo.ipynb) notebook.

## Tests

As with SageMath's code, tests and code quality checks can be started with the `--tox` option (from the cloned directory):
```
sage --tox phitigra
```

## Changelog

### In v0.2.2

Single change: renaming ``SimpleGraphEditor`` into ``GraphEditor``. Code written for previous versions is not compatible with this one, but can be easily fixed.

### In v0.2.1

  * Demo notebook
  * Binder link
  * Improved update time when moving vertices
  * Minor fixes

### In v0.2.0

  * Docstrings and doctests in (almost) all functions
  * Hiding of internal objects
  * Cleaning code
