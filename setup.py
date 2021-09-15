import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="phitigra",
    version="0.2.4",
    author="Jean-Florent Raymond",
    author_email="j-florent.raymond@uca.fr",
    description="A graph editor for SageMath/Jupyter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jfraymond/phitigra",
    project_urls={
        "Bug Tracker": "https://github.com/jfraymond/phitigra/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["ipycanvas",
                      "ipywidgets"]
)
