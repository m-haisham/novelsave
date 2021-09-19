from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    install_requires=requirements,
    packages=['novelsave', 'static', 'test'],
    include_package_data=True,
    package_data={
        'static': ['*.mako', '*.css', '*.js'],
    },
)
