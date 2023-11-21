import os

from setuptools import setup, find_packages

# %%


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='sars_cov2_signals',
    version='2.2',
    packages=["requirements.txt"],
    # py_modules=["main.py"],
    url='https://gitlab.phe.gov.uk/gpha/horizon-scanning/sars_cov2_signals_automation',
    license='',
    author='Mike Brown',
    author_email='michael.d.brown@phe.gov.uk',
    description='This package is intended for the manual and or automation running of signal review analysis which '
                'serves function within Horizon Scanning (GPHA) bi-weekly reporting and meetings',
    long_description=read("README.md"),
    classifiers=["Development Status :: 5 - Production/Stable"],
)
