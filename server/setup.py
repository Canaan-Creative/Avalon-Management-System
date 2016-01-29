#!/usr/bin/env python3

from setuptools import setup, find_packages
import ams

setup(
    name="ams",
    version=ams.__version__,
    packages=find_packages(),
    scripts=['amscli'],
    install_requires=["mysql-connector-python >= 2.0"],
    dependency_links=["http://cdn.mysql.com/Downloads/Connector-Python/"
                      "mysql-connector-python-2.0.4.zip#"
                      "md5=3df394d89300db95163f17c843ef49df"],
)
