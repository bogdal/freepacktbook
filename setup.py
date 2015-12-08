# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='freepacktbook',
    version='0.0.1',
    description='Claim Your Free PacktPub eBook',
    author='Adam Bogdał',
    author_email='adam@bogdal.pl',
    url='https://github.com/bogdal/freepacktbook',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'beautifulsoup4',
        'requests'],
    entry_points={
        'console_scripts': [
            'claim_free_ebook = freepacktbook:claim_free_ebook']},
    zip_safe=False)
