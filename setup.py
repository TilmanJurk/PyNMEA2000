from setuptools import find_packages, setup

setup(
    name='n2k',
    packages=find_packages(include=['n2k']),
    version='0.1.0',
    description='Library to communicate with NMEA2000 devices',
    author='Finn Böger',
    license='MIT',
    install_requires=[],
)