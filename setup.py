import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="phitigra",
    version="0.0.1",
    author="Jean-Florent Raymond",
    author_email="j-florent.raymond@uca.fr",
    description="A graph editor for jupyter/sagemath",
    url="https://gitlab.limos.fr/jfraymon/graph-edit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    'keywords': ['jupyter', 'widget', 'graph'],
)
