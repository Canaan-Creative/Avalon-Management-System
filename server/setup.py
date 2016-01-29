#!/usr/bin/env python3

import os
import shutil
import errno

from setuptools import setup, find_packages
from setuptools.command.install import install as _install

import ams


class install(_install):
    def run(self):
        _install.run(self)
        virtual = os.environ.get('VIRTUAL_ENV')
        if virtual is not None:
            directory = os.path.join(virtual, 'etc')
            try:
                os.makedirs(directory)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
        else:
            directory = '/etc'

        dist = os.path.join(directory, 'ams.conf')
        shutil.copyfile('ams.conf.example', dist)
        print('copying {} -> {}'.format('ams.conf.example', dist))


if __name__ == '__main__':
    setup(
        cmdclass={'install': install},
        name="ams",
        version=ams.__version__,
        packages=find_packages(),
        scripts=['amscli'],
        include_package_data=True,
        zip_safe=False,
        install_requires=["mysql-connector-python >= 2.0"],
        dependency_links=["http://cdn.mysql.com/Downloads/Connector-Python/"
                          "mysql-connector-python-2.0.4.zip#"
                          "md5=3df394d89300db95163f17c843ef49df"],
    )
