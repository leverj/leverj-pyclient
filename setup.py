import json
import sys

from setuptools import find_packages, setup

version = "0.1"
name = "leverj_pyclient"

setup(
    name=name,
    version=version,
    description='Python client library for Leverj spot and futures exchange',
    long_description='Python client library for Leverj spot and futures exchange',
    author='leverj',
    url='https://leverj.io',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.0',
    install_requires=['web3>=4.8.2', 'setuptools'],
    setup_requires=['nose'],
    extras_require={'dev': ['nose']},
    test_suite='nose.collector',
    project_urls={'Source': f'https://github.com/leverj/leverj-pyclient'}
)
