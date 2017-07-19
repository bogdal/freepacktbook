# -*- coding: utf-8 -*-
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]
    test_args = []

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='freepacktbook',
    version='1.1.0',
    description='Claim Your Free PacktPub eBook',
    author='Adam Bogdał',
    author_email='adam@bogdal.pl',
    url='https://github.com/bogdal/freepacktbook',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'beautifulsoup4',
        'python-slugify>=1.2.0',
        'requests',
        'tqdm>=3.4.0'],
    cmdclass={
        'test': PyTest},
    tests_require=[
        'mock',
        'pytest>=2.8.1',
        'pytest-cov',
        'requests-mock',
        'vcrpy>=1.7.3'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    entry_points={
        'console_scripts': [
            'claim_free_ebook = freepacktbook:claim_free_ebook',
            'download_ebooks = freepacktbook:download_ebooks']},
    zip_safe=False)
