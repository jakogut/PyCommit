from setuptools import setup

setup(
    name = 'pycommit',
    version = '0.1',
    author = 'Joseph Kogut',
    author_email = 'joseph.kogut@gmail.com',
    packages = ['pycommit'],
    url = 'http://josephkogut.com/jakgout/PyCommit',
    license = 'LICENSE.txt',
    description = "Python interface for CommitCRM",
    long_description = open('README.txt').read(),
    install_requires=[
        "untangle  >= 1.1.0",
        "pyparsing >= 2.0.3",
        "lxml      >= 3.4.4",
        ],
    )
