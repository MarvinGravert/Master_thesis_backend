from distutils import filelist
from setuptools import setup, find_packages

from gen_code import generate_proto_code
import os

# py_modules = generate_proto_code()
os.chdir(".\protodef_files")
setup(
    name='holo_vive_com',  
    version='0.1',  
    description='proto communication interfac for hololens-vive integration of my thesis',
    long_description='',
    author='Marvin Gravert',
    author_email='marvin.gravert@gmail.com',

    license='MIT',
    # which directories to search for imports. Importable dirs are marked by
    # py_modules=py_modules,
    # also possible but may include unwanted dir such as tests
    # packages=["protodef_files"],
    zip_safe=False,
)
