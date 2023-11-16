# Installation

We will add this project to PyPI to ease installation. For now, a local installation is needed to run the notebooks.
There are many ways of installing Python projects locally. We will explain several options here.


### Install into virtual environment
TBD

### Create a virtual environment


An optional first step is to create a virtual environment.
Feel free to skip this if you already have a virtual environment which you want to use:


```shell
python3 -m venv oncoexporter-venv
source oncoexporter-venv/bin/activate
```




The command above will create a new virtual environment at `oncoexporter-venv` and activate the environment.


### Install Oncoexporter

Next, Oncoexporter can be installed into an existing virtual environment by running:


```shell
 # Ensure you are in the repo folder
cd oncoexporter
python3 -m pip install --editable .
```

`pip` will install `oncoexporter` into the active environment. The package is installed in *editable* mode -
any code updates are available after Python restart, instead of having to reinstall.


### Use Oncoexporter in Jupyter notebook


To use the kernel in Jupyter notebook,
first, make sure you have `ipykernel` library to allow using the virtual environment as a Jupyter kernel.

```
python3 -m pip install jupyter ipykernel
```


Then, we can create a new Jupyter kernel and register the kernel with Jupyter by running:

```
python -m ipykernel install --user --name oncoexporter_env --display-name "Oncoexporter"
```

Last, starting from the project directory, we can run Jupyter to work on the notebooks of the Oncoexport repository.

```
cd notebooks
jupyter-notebook
```


At this point, a Jupyter page should open in the system browser. Navigate to the notebook or create one and be sure
to activate the ``oncoexporter_env`` kernel.
