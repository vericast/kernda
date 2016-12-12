import versioneer
from setuptools import setup

setup_args = dict(
    name='kernda',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Add conda environment activation to an IPython kernel spec',
    url='https://github.com/parente/kernda',
    author='MaxPoint Interactive',
    author_email='peter.parente@maxpoint.com',
    maintainer='MaxPoint Interactive',
    maintainer_email='peter.parente@maxpoint.com',
    license='BSD 3-Clause',
    platforms=['Linux', 'Mac OSX'],
    packages=['kernda'],
    entry_points={
        'console_scripts': ['kernda = kernda.cli:cli']
    }
)

if __name__ == '__main__':
    setup(**setup_args)
