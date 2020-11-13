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
    description="Tool to convert webnovel to epub",
    author_email='mhaisham79@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        "Operating System :: OS Independent",
    ],
    license="MIT license",
    keywords='webnovel novel scrape save own',

    url='https://github.com/mHaisham/novelsave',
    project_urls={
        'Source code': 'https://github.com/mHaisham/novelsave'
    },
    entry_points={
        'console_scripts': [
            'novelsave = novelsave.__main__:main'
        ]
    },
    packages=find_packages(),
    python_requires='>=3.6'
)
