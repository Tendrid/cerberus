#!/usr/bin/env python

from setuptools import setup

setup(
    name='cerberus',
    version='1.0',
    description='Cerberus Discord Bot',
    author='Tendrid',
    author_email='tendrid@gmail.com',
    url='peoplebacon.com',
    packages=['cerberus'],
    classifiers=[
        'Programming Language :: Python :: 3.7'
    ],
    install_requires=[
        'discord.py>=1.7.3'
    ],
    entry_points={
        'console_scripts': [
            'cerberus=cerberus.command:main',
        ],
    }
)
