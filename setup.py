# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='freepacktbook',
    version='0.0.3',
    description='Claim Your Free PacktPub eBook',
    author='Adam Bogdał',
    author_email='adam@bogdal.pl',
    url='https://github.com/bogdal/freepacktbook',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'beautifulsoup4',
        'requests'],
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
            'claim_free_ebook = freepacktbook:claim_free_ebook']},
    zip_safe=False)
