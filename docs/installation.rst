.. _installation:

============
Installation
============

We will add this project to PyPI to ease installation. For now, a local installation is needed to run the notebooks.
There are many ways of installing Pythopn projects locally. We will explain two options here.


Virtual Environment
^^^^^^^^^^^^^^^^^^^

To use the venv module, enter the following code from the base directory.


.. code-block:: shell
   :linenos:

   python3 -m venv c2p_env
   source c2p_env/bin/activate
   pip install --upgrade pip
   pip install pyphetools pandas

To work with the notebooks in this repository, it may be desirable to install the latest local version

.. code-block:: shell
   :linenos:

   source c2p_env/bin/activate
   pip install -e .


To use the kernel in notebooks, enter the following

.. code-block:: shell
   :linenos:

   pip install jupyter ipykernel
   python -m ipykernel install --name "c2p_env" --display-name "c2p_env"
   cd notebooks
   jupyter-notebook

At this point, a Jupyter page should open in the system browser. Navigate to the notebook or create one and be sure 
to activate the ``c2p_env`` kernel.