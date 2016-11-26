from setuptools import find_packages, setup

setup(
    name="UWShitpostBot",
    author="Alex Cuoci, Jeffrey Zhao",
    packages=find_packages(),
    install_requires=[i.strip() for i in open("requirements.txt").readlines()]
)
