# Python Package Template

This is used as an Template for python package structure. It will be extended further down the line. For the moment it functions as a testbed for learning about python packaging

## What has been learned

Hereafter, the lessons learned will be talked about. A pretty good baseline are [this write down](https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/) and [this stackoverflow](https://stackoverflow.com/questions/51286928/what-is-where-argument-for-in-setuptools-find-packages). In theory also [this python packaging guide](https://packaging.python.org/guides/packaging-namespace-packages/), though I found a bit confusing as the provided examples are not matching up with the code in the guide. The overall documentation/explanation of the setuptool can be found [here](https://setuptools.readthedocs.io/en/latest/setuptools.html).

### Package namespaces

To allow access like `import package.subpackage.module`{:.language-python}. One needs a structure such as shown in this repository. The package is a folder in the top level repo (same level as the setup.py). One level further down the subpackages are stored which individually each have an ___init___.py. 

Now it suffices to place find_packages in the setup.py to find all the subpackages and modules. 

## Usage

```bash
testImportRunner 
```
This will write messages into the console