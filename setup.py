# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 12:25:44 2024

@author: 2016570
"""

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

                         
setup(
    name='py4hw',
    version='0.1',
    author='David Castells-Rufas',
    author_email='david.castells@uab.cat',
    description='Python-based RISC-V Full System Simulator.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/davidcastells/py4hw',
    install_requires=['py4hw>=2024.3', 'pyelftools'],
    tests_require=['py4hw>=2024.3', 'pyelftools'],
    packages=find_packages(),
    package_data={'': ['*.png']}
)
