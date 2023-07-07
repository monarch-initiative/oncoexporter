# c2p
Cancer data to GA4GH phenopacket




## Set up

pip install -r requirements.txt

or:

One way of installing the dependencies is
```
python3 -m venv c2penc
pip install --upgrade pip
pip install phenopackets
pip install git+https://github.com/CancerDataAggregator/cda-python.git
pip install jupyter ipykernel
python -m ipykernel install --name "c2penv" --user
# The open a notebook
jupyter-notebook
# choose the c2penv kernel from the kernel menu in the notebook
```



# Data sources
## Cancer Data Aggregator
https://github.com/CancerDataAggregator