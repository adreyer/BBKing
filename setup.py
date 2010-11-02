
from setuptools import setup, find_packages

setup(name="bbking",
    version="0.0.1",
    description="A Django BBCode Parser",
    author="Rev. Johnny Healey",
    author_email="rev.null@gmail.com",
    packages=find_packages(),
    package_data={
        'bbking':['templates/bbking/tags/*.html'],
    })

