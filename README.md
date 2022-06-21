# Phitigra

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jfraymond/phitigra/master?filepath=demo.ipynb)

_Phitigra_ is a graph editor widget for [SageMath](www.sagemath.org)
when using the [Jupyter](www.jupyter.org) notebook.
<p><img width="600" src="https://raw.githubusercontent.com/jfraymond/phitigra/master/docs/source/images/editor.png"></p>

Try the [demo](https://mybinder.org/v2/gh/jfraymond/phitigra/master?filepath=demo.ipynb) notebook on mybinder!  
**Note:** for some unknown reason the above link stopped working.

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

With jupyter, you might need the following
```
jupyter nbextension enable --py widgetsnbextension
```
after you install ipywidgets, and possibly more if using virtualenv and working in an activated virtual environment, see [ipywidget's documentation](https://ipywidgets.readthedocs.io/en/latest/user_install.html) for full details.  
**This is the first thing to check if the import of the package works fine but nothing shows when you try to display the widget.**

With jupyterlab, the `jupyterlab_widgets` package is also required for the widget to show.

## How to try it?

### On mybinder

(Runs online, nothing to install.)  

**Note:** for some unknown reason the link below stopped working.
Clicking [here](https://mybinder.org/v2/gh/jfraymond/phitigra/master?filepath=demo.ipynb) will open the demo notebook on mybinder in a new tab. Note that this uses the _stable_ version of phitigra (that from the `master` branch), which may differ from the one in the `develop` branch.  

### From a standalone SageMath installation

This assumes that SageMath is installed on your system. See http://www.sagemath.org for install instructions.

#### Stable version

The _stable_ version is on [pypi](https://pypi.org/project/phitigra/) so it can be installed as follows
```
sage -pip install --upgrade phitigra
```

#### Development version

Clone the source from the repository
```
git clone https://github.com/jfraymond/phitigra.git
```

Install or upgrade with pip:
```
sage -pip install --upgrade path/to/the/cloned/repository
```

That's it!

To uninstall:
```
sage -pip uninstall phitigra
```

Note that the above commands should not be run from the repository directory, otherwise `pip` [might](https://github.com/pypa/pip/issues/6703) complain that it did not find files to uninstall.

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

There are many more examples in the demo notebook.

## Tests

As with SageMath's code, tests and code quality checks can be started with the `--tox` option (from the cloned directory):
```
sage --tox src/phitigra
```

## Building the documentation

From the package directory
```
cd docs
sage -sh -c "make html"
```

The main file of the documentation is then in `docs/build/html/index.html`.
A recent build of the documentation can be found [here](https://perso.limos.fr/~jfraymon/phitigra_docs/html/).

## What's new

### v0.2.6

  * Minor change to adapt to the new ipycanvas; this version will not work with ipycanvas < 0.12.0

### v0.2.5

  * Minor fixes in the documentation
  * Fixed an issue when building the documentation

### v0.2.4

  * Show/hide edge labels
  * User-defined vertex labels
  * Exposing vertex positioning functions
  * Removing the `Next` button
  * Updating links after move to github
  * More examples in the demo notebook

### v0.2.3

  * Improved doc
  * Polished code, which now passes all tests 
  * Changed package structure to follows [python guidelines](https://packaging.python.org/tutorials/packaging-projects/)

### v0.2.2

  * Single (major) change: renaming ``SimpleGraphEditor`` into ``GraphEditor``. Code written for previous versions is not compatible with this one, but can be easily fixed.

### v0.2.1

  * Demo notebook
  * Binder link
  * Improved update time when moving vertices
  * Minor fixes

### v0.2.0

  * Docstrings and doctests in (almost) all functions
  * Hiding of internal objects
  * Cleaning code
