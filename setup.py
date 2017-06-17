from setuptools import setup, find_packages
from codecs import open
import os
import re

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "pystpl", "__init__.py")) as fh:
    version = re.match(r".*__version__ = \"(.*?)\"", fh.read(),re.S).group(1)

setup(
    name="pystpl",
    version=version,
    description="a small and simple template parser",
    url="https://github.com/lschw/pystpl",
    author="Lukas Schwarz",
    author_email="ls@lukasschwarz.de",
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    packages=["pystpl"],
)

