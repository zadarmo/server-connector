#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='server_connector',
    version='0.0.1',
    description=(
        'A simple tool for developers that can perform operations on server with just a few line of codes.'
    ),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='zadarmo',
    author_email='wx01290804@163.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'paramiko',
    ],
)
