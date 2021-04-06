from _pytest.python import Package
from setuptools import setup, find_packages


setup(
    name='backend_core',
    version='0.1',
    description='api and utils for the backend',
    long_description='',
    author='Marvin Gravert',
    author_email='marvin.gravert@gmail.com',

    packages=find_packages(exclude=("tests",)),
    license='MIT',
    zip_safe=False,
)
