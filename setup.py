from distutils.core import setup

setup(
    name = 'PyCommit',
    version = 'git',
    author = 'Joseph Kogut',
    author_email = 'joseph.kogut@gmail.com',
    packages = ['pycommit'],
    url = 'http://josephkogut.com/jakgout/PyCommit',
    license = 'LICENSE.txt',
    description = "Python interface for CommitCRM",
    long_description = open('README.txt').read(),
    install_required=[
        "untangle" >= "1.1.0"
        ],
    )
