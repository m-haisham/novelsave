from setuptools import setup, find_packages

from novelsave import meta

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    name='novelsave',
    version=meta.__version__,
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

    url=meta.github,
    project_urls={
        'Source code': meta.github,
    },
    entry_points={
        'console_scripts': [
            'novelsave = novelsave.__main__:main'
        ]
    },
    packages=find_packages(),
    python_requires='>=3.6'
)
