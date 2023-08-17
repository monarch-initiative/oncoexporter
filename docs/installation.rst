.. _installation:

============
Installation
============

We will add this project to PyPI to ease installation. For now, a local installation is needed to run the notebooks.
There are many ways of installing Python projects locally. We will explain several options here.



Loading the package from file system
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before the import statements, add the correct path using the sys module. For instance, to access the c2p 
package from the ``notebooks`` folder, put the following lines at the top of the notebook.

.. code-block:: shell
   :linenos:

   import sys
   sys.path.append('../src')
   import c2p

Note that the python code for the c2p package is found in the folder ``src/c2p``.


Virtual Environment
^^^^^^^^^^^^^^^^^^^

To use the venv module, enter the following code from the base directory.


.. code-block:: shell
   :linenos:

   python3 -m venv c2p_env
   source c2p_env/bin/activate
   pip install --upgrade pip
   pip install .

Note that the last line will install the core dependencies listed in the ``pyproject.toml`` file.
To install the test dependency (pytest), enter the following line

.. code-block:: shell
   :linenos:

   pip install .[test]


To use the virtual environment, enter the following

.. code-block:: shell
   :linenos:

   source c2p_env/bin/activate

To use the kernel in notebooks, enter the following

.. code-block:: shell
   :linenos:

   pip install jupyter ipykernel
   python -m ipykernel install --name c2p_env --display-name "c2p_env" --local
   cd notebooks
   jupyter-notebook

At this point, a Jupyter page should open in the system browser. Navigate to the notebook or create one and be sure 
to activate the ``c2p_env`` kernel.


Creating read the docs locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pushing changes to to the repository will cause the online documentation to be updated. If you want
to work on the docuemntation locally, install the following packages

.. code-block:: shell
   :linenos:

   pip install sphinx sphinx-rtd-theme 
   # to create documentation do the following
   cd docs
   make html
   # this will create HTML pages in the docs/_build/html folder