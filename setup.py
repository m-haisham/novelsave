from setuptools import setup, find_packages

import novelsave

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    name='novelsave',
    version=novelsave.__version__,
    author="Schicksal",
    description="This is a commandline tool to download and convert novels from numerous sources to epub files",
    author_email='mhaisham79@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'Topic :: Games/Entertainment',
    ],
    license="APACHE-2.0 license",
    keywords='webnovel novel lightnovel scrape download epub save',

    url=novelsave.__source__,
    entry_points={
        'console_scripts': [
            'novelsave = novelsave.cli.main:cli'
        ]
    },
    packages=find_packages(),
    python_requires='>=3.6'
)
