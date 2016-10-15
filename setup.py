import versioneer
from setuptools import setup

setup_args = dict(
    name='kernda',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Peter Parente',
    author_email='parente@cs.unc.edu',
    license='BSD 3-Clause',
    platforms=['Linux', 'Mac OSX'],
    packages=['kernda'],
    entry_points={
        'console_scripts': ['kernda = kernda.cli:cli']
    }
)

if __name__ == '__main__':
    setup(**setup_args)
